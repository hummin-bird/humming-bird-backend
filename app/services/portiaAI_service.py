import re
from typing import Dict, Any
import logging
from google import genai
from dotenv import load_dotenv
import os
import json
import threading
from openai import OpenAI
import time

logger = logging.getLogger(__name__)
# Get the directory of the current script
current_dir = os.path.dirname(os.path.abspath(__file__))

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
    Plan
)
from customTool import LLMstructureTool

custom_tool_registry = InMemoryToolRegistry.from_local_tools(
    [
        LLMstructureTool()
    ],
)

from portia.plan import PlanUUID

# from portia.tools import FileReaderTool
# from my_custom_tools.file_writer_tool import FileWriterTool

# custom_tool_registry = InMemoryToolRegistry.from_local_tools(
#     [
#         FileReaderTool(),
#         FileWriterTool(),
#     ],
# )
from portia.cli import CLIExecutionHooks


class PortiaAIService:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    async def generate_tools(self, text_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Call the Gemini API to generate a response to the user's query, Check if it searches the internet
        
        """
        # Create a default Portia config with LLM provider set to Google GenAI and model set to Gemini 2.0 Flash
        openai_config = Config.from_default(
            storage_class=StorageClass.CLOUD,
            llm_provider=LLMProvider.OPENAI,
            llm_model_name=LLMModel.GPT_4_O_MINI,
        )
        self.logger.info("Setup LLM configuration")
        # Instantiate a Portia instance. Load it with the config and with the example tools.
        self.portia = Portia(
                        config=openai_config,
                        tools=[open_source_tool_registry.get_tool("llm_tool"),
                               open_source_tool_registry.get_tool("search_tool"),
                               custom_tool_registry.get_tool("llm_structure_tool")
                              ],
                         )
        # initiation_plan = json.load(open('humming-bird-backend/app/services/initiation_plan.json'))
        with open(os.path.join(current_dir, 'generation_plan.json'), 'r') as f:
            plan_json = f.read()
            plan_json = re.sub("PRODUCT_INFO", text_data, plan_json)

            initiation_plan = Plan.model_validate_json(plan_json)
            initiation_plan.id = PlanUUID()

        with execution_context(end_user_id="demo"):
            self.portia.storage.save_plan(initiation_plan)
            self.plan_run = self.portia.run_plan(initiation_plan)

        output = self.plan_run.outputs.step_outputs[f"$structured_output_1"].value
        products = output["products"]
        return products
    
    
    def run_plan(self, plan: Plan, end_user_id="demo"):
        with execution_context(end_user_id=end_user_id):
            self.portia.storage.save_plan(plan)
            self.plan_run = self.portia.run_plan(plan)

if __name__ == "__main__":
    import asyncio
    msg = {"user_query": "I want to build a website to sell cars"}
    service = PortiaAIService() 
    result = asyncio.run(service.generate_tools(msg))
    