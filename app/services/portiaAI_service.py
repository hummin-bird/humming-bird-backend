from typing import Dict, Any
import logging
from google import genai
from dotenv import load_dotenv
import os
import json
import threading

logger = logging.getLogger(__name__)
load_dotenv() 
GOOGLE_API_KEY = os.getenv("GEMINI_API_KEY")

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
    Plan
)
from portia.cli import CLIExecutionHooks



class PortiaAIService:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    async def init_portia(self, text_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Call the Gemini API to generate a response to the user's query, Check if it searches the internet
        
        """
        # Create a default Portia config with LLM provider set to Google GenAI and model set to Gemini 2.0 Flash
        # google_config = Config.from_default(
        #     storage_class=StorageClass.CLOUD,
        #     llm_provider=LLMProvider.GOOGLE_GENERATIVE_AI,
        #     llm_model_name=LLMModel.GEMINI_2_0_FLASH,
        #     google_api_key=GOOGLE_API_KEY,
        # )
        # Instantiate a Portia instance. Load it with the config and with the example tools.
        self.portia = Portia(
                        # config=google_config,
                        # tools=PortiaToolRegistry(google_config),
                        tools=example_tool_registry,
                         )

        # initiation_plan = json.load(open('humming-bird-backend/app/services/initiation_plan.json'))
        with open('humming-bird-backend/app/services/initiation_plan.json', 'r') as f:
            plan_json = f.read()
            initiation_plan = Plan.model_validate_json(plan_json)
            initiation_plan.plan_context.query = text_data["user_query"]

        with execution_context(end_user_id="demo"):
            self.plan_run = self.portia.run_plan(initiation_plan)
        # thread = threading.Thread(target=self.run_plan, args=(initiation_plan,))
        # thread.start()
        self.plan_run.outputs.final_output.summary
        return self.plan_run.outputs.final_output.summary
    
    async def run_plan(self, plan: Plan):
        with execution_context(end_user_id="demo"):
            self.plan_run = self.portia.run_plan(plan)

    async def resume(self, text_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Resume the plan from the last step
        """
        while self.plan_run.state == PlanRunState.NEED_CLARIFICATION:
        # If clarifications are needed, resolve them before resuming the plan run
            # Once clarifications are resolved, resume the plan run
            self.plan_run = self.portia.resume(self.plan_run)
        return
            
    async def process_text_data(self, text_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process audio data received from ElevenLabs webhook
        """
        try:
            # TODO: Implement deep research processing logic
            self.logger.info("Processing audio data")
            
            # Placeholder for processing logic
            result = {
                "status": "success",
                "message": "Audio data processed successfully",
                "data": text_data
            }
            
            return result
        except Exception as e:
            self.logger.error(f"Error processing audio data: {str(e)}")
            raise

if __name__ == "__main__":
    import asyncio
    msg = {"user_query": "I want to build a website to sell cars"}
    service = PortiaAIService() 
    asyncio.run(service.init_portia(msg))
    