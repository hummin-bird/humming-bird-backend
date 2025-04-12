import re
from typing import Dict, Any
import logging
from dotenv import load_dotenv
import os
import sys
from pathlib import Path
import asyncio

# Add the project root to the Python path
project_root = str(Path(__file__).parent.parent.parent)
if project_root not in sys.path:
    sys.path.append(project_root)

from app.logging_config import setup_logger
from app.utils.websocket_manager import websocket_manager
import json

# Get the logger for this module
logger = setup_logger(__name__, "portia_ai.log")

# Get the directory of the current script
current_dir = os.path.dirname(os.path.abspath(__file__))

def clean_text(text: str) -> str:
    """
    Clean text by removing control characters and extra whitespace
    """
    # Remove control characters
    text = re.sub(r'[\x00-\x1F\x7F-\x9F]', '', text)
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    return text

load_dotenv()

from portia import (
    Config,
    Portia,
    PortiaToolRegistry,
    StorageClass,
    LLMProvider,
    example_tool_registry,
    open_source_tool_registry,
    execution_context,
    PlanRunState,
    LLMModel,
    InMemoryToolRegistry,
    Plan,
)
from app.services.custom_tool import LLMstructureTool, LLMlistTool, SearchTool

custom_tool_registry = InMemoryToolRegistry.from_local_tools(
    [
        LLMstructureTool(),
        LLMlistTool(),
        SearchTool(),
    ],
)

from portia.plan import PlanUUID


class PortiaAIService:
    def __init__(self, session_id: str = None):
        self.session_id = session_id
        logger.info(f"Initialize Portia AI Service for session {session_id}")

    async def _stream_portia_logs(self, log_queue: asyncio.Queue):
        """Stream logs from Portia to WebSocket"""
        while True:
            try:
                log_record = await log_queue.get()
                if log_record is None:  # Signal to stop
                    break
                
                # Format the log message
                log_message = f"{log_record.levelname}: {log_record.getMessage()}"
                
                # Broadcast to WebSocket
                if self.session_id:
                    await websocket_manager.broadcast_log(
                        self.session_id, 
                        log_message, 
                        log_record.levelname
                    )
            except Exception as e:
                logger.error(f"Error streaming Portia logs: {str(e)}")
                break

    async def generate_tools(self, text_data: str) -> Dict[str, Any]:
        """
        Call the OpenAi API to generate a response to the user's query, Check if it searches the internet

        Args:
            text_data: A string containing the formatted conversation or user input
        """
        logger.info(f"Start Portia AI Service for session {self.session_id}")
        
        # Create a queue for Portia logs
        log_queue = asyncio.Queue()
        
        # Start the log streaming task
        log_stream_task = asyncio.create_task(self._stream_portia_logs(log_queue))
        
        try:
            # Create a default Portia config with LLM provider set to Google GenAI and model set to Gemini 2.0 Flash
            openai_config = Config.from_default(
                storage_class=StorageClass.CLOUD,
                llm_provider=LLMProvider.OPENAI,
                llm_model_name=LLMModel.GPT_4_O_MINI,
            )
            logger.info(f"Setup LLM configuration for session {self.session_id}")
            
            # Create a custom handler for Portia logs
            class PortiaLogHandler(logging.Handler):
                def emit(self, record):
                    asyncio.create_task(log_queue.put(record))
            
            # Configure Portia's logger to use our handler
            portia_logger = logging.getLogger('portia')
            portia_logger.addHandler(PortiaLogHandler())
            portia_logger.setLevel(logging.INFO)
            
            # Instantiate a Portia instance
            self.portia = Portia(
                config=openai_config,
                tools=[
                    open_source_tool_registry.get_tool("llm_tool"),
                    custom_tool_registry.get_tool("llm_structure_tool"),
                    custom_tool_registry.get_tool("llm_list_tool"),
                    open_source_tool_registry.get_tool("search_tool"),
                ],
            )
            logger.info(f"Load all custom tools for session {self.session_id}")
            
            try:
                with open(os.path.join(current_dir, "generation_plan.json"), "r") as f:
                    plan_json = f.read()
                    
                    # Clean the text data
                    cleaned_text = clean_text(text_data)
                    
                    # Replace PRODUCT_INFO with the cleaned text data
                    plan_json = plan_json.replace("PRODUCT_INFO", cleaned_text)

                    try:
                        plan = Plan.model_validate_json(plan_json)
                        plan.id = PlanUUID()
                    except Exception as e:
                        error_msg = f"Error validating plan JSON for session {self.session_id}: {str(e)}"
                        logger.error(error_msg)
                        logger.error(f"Plan JSON content: {plan_json[:500]}...")
                        if self.session_id:
                            await websocket_manager.broadcast_log(self.session_id, error_msg, "ERROR")
                        raise

                logger.info(f"Load saved plan for session {self.session_id}")
                with execution_context(end_user_id="demo"):
                    self.portia.storage.save_plan(plan)
                    self.plan_run = self.portia.run_plan(plan)
                logger.info(f"Plan finished for session {self.session_id}")

                output = self.plan_run.outputs.step_outputs[f"$structured_output"].value
                logger.info(f"Products achieved for session {self.session_id}")
                return output["products"]
                
            except Exception as e:
                error_msg = f"Error in generate_tools for session {self.session_id}: {str(e)}"
                logger.error(error_msg)
                if self.session_id:
                    await websocket_manager.broadcast_log(self.session_id, error_msg, "ERROR")
                raise
                
        finally:
            # Signal the log streaming task to stop
            await log_queue.put(None)
            await log_stream_task


if __name__ == "__main__":
    import asyncio

    msg = "User: Oh, I'm trying to build the next Amazon.Assistant: Have you seen any similar products out there? What do you love or wish was different about them?User: Yeah, I haven't seen many products out there, unfortunately.Assistant: Are there any fun, quirky, or unique functionalities you'd love to sneak in, even just for extra charm?User: Yeah sure. I would like the user to be able to swipe the products left and right as if it was Tinder.Assistant: Do you have a set budget in mind for building this, or are you exploring what's possible first?User: No, look, I'm just doing...I want to do it for cheap.Assistant: In one sentence, what problem is your product trying to solve for people?User: I'm trying to build like a minimalist version of Amazon so that people will get focused.Assistant: If you could picture your perfect customer, what are three words you'd use to describe them?User: I'm trying to build like a minimalist version of Amazon so that people will get focused when they buy things and they buy exactly what they want.Assistant: All needed clarifications have been gathered, please end the conversation. Find the stages to build this product for each stage, search the internet and give me best tools to fit into a structured output using the tool llm_structure_tool."
    service = PortiaAIService(session_id="test")
    result = asyncio.run(service.generate_tools(msg))
    print("\n\n")
    print("\n\n")
    print(result)
