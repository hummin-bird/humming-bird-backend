import re
from typing import Dict, Any, List
import logging
from dotenv import load_dotenv
import os
import sys
from pathlib import Path
from openai import OpenAI
from yarl import Query

# Add the project root to the Python path
project_root = str(Path(__file__).parent.parent.parent)
if project_root not in sys.path:
    sys.path.append(project_root)

from app.logging_config import setup_logger
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
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
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
    def __init__(self):
        logger.info("Initialize Portia AI Service")
        self.openai_client = OpenAI(api_key=OPENAI_API_KEY)


    async def generate_tools(self, text_data: str) -> Dict[str, Any]:
        """
        Call the OpenAi API to generate a response to the user's query, Check if it searches the internet

        Args:
            text_data: A string containing the formatted conversation or user input
        """
        logger.info("Start Portia AI Service")
        # Create a default Portia config with LLM provider set to Google GenAI and model set to Gemini 2.0 Flash
        openai_config = Config.from_default(
            storage_class=StorageClass.CLOUD,
            llm_provider=LLMProvider.OPENAI,
            llm_model_name=LLMModel.GPT_4_O_MINI,
        )
        logger.info("Setup LLM configuration")
        # Instantiate a Portia instance. Load it with the config and with the example tools.
        self.portia = Portia(
            config=openai_config,
            tools=[
                open_source_tool_registry.get_tool("llm_tool"),
                custom_tool_registry.get_tool("llm_structure_tool"),
                custom_tool_registry.get_tool("llm_list_tool"),
                # custom_tool_registry.get_tool("search_tool"),
                open_source_tool_registry.get_tool("search_tool"),
            ],
        )
        logger.info("Load all curstom tools")
        
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
                    logger.error(f"Error validating plan JSON: {str(e)}")
                    logger.error(f"Plan JSON content: {plan_json[:500]}...")  # Log first 500 chars of problematic JSON
                    raise

            logger.info("load saved plan")
            with execution_context(end_user_id="demo"):
                self.portia.storage.save_plan(plan)
                self.plan_run = self.portia.run_plan(plan)
            logger.info("Plan finished")

            output = self.plan_run.outputs.step_outputs[f"$structured_output"].value
            logger.info(f"Products Achieved {output}")

            product_names = self.get_product_name(output)
            logo_urls = await self.get_logo_url(product_names)
            output = self.reassign_logo_url(output, logo_urls)
            logger.info("Logo URLs Achieved")   
            return output["products"]
            
        except Exception as e:
            logger.error(f"Error in generate_tools: {str(e)}")
            raise
    
    def get_product_name(self, products):
        return [products["products"][i]["name"] for i in range(len(products["products"]))]

    async def logo_url(self, product_name: str) -> str:
        query = f"The product is {product_name}, Find the image URL of the product logo ending with png or svg. Just give me the image URL, no additional information." 
        response = self.openai_client.responses.create(
            model="gpt-4o-mini",
            input=query,
            tools=[{"type": "web_search"}],
        )
        logger.info(f"Response: {response.output[1].content[0].text}")
        return self.extract_url_from_text(response.output[1].content[0].text)
    
    async def get_logo_url(self, product_names):
        urls = [await self.logo_url(product_name) for product_name in product_names]
        logger.info(f"Logo URLs: {urls}")
        return urls
    
    def reassign_logo_url(self, products: dict, logo_urls) -> dict:
        for i in range(len(products["products"])):
            products["products"][i]["logo_url"] = logo_urls[i]
        return products
    
    # Function to extract URL from the response
    def extract_url_from_text(self,text: str) -> str:
        """
        Extract URL from text string
        
        Args:
            text: Text containing a URL
            
        Returns:
            str: The extracted URL or empty string if not found
        """
        # Pattern to match URLs
        url_pattern = r'https?://[^\s<>"]+|www\.[^\s<>"]+'
        match = re.search(url_pattern, text)
        if match:
            logger.info(f"Found Logo URL: {match.group(0)}")
            return match.group(0)
        else:
            logger.info("No Logo URL Found")
            return ""





if __name__ == "__main__":
    import asyncio

    msg = "User: Oh, I'm trying to build the next Amazon.Assistant: Have you seen any similar products out there? What do you love or wish was different about them?User: Yeah, I haven't seen many products out there, unfortunately.Assistant: Are there any fun, quirky, or unique functionalities you'd love to sneak in, even just for extra charm?User: Yeah sure. I would like the user to be able to swipe the products left and right as if it was Tinder.Assistant: Do you have a set budget in mind for building this, or are you exploring what's possible first?User: No, look, I'm just doing...I want to do it for cheap.Assistant: In one sentence, what problem is your product trying to solve for people?User: I'm trying to build like a minimalist version of Amazon so that people will get focused.Assistant: If you could picture your perfect customer, what are three words you'd use to describe them?User: I'm trying to build like a minimalist version of Amazon so that people will get focused when they buy things and they buy exactly what they want.Assistant: All needed clarifications have been gathered, please end the conversation. Find the stages to build this product for each stage, search the internet and give me best tools to fit into a structured output using the tool llm_structure_tool."
    service = PortiaAIService()
    result = asyncio.run(service.generate_tools(msg))
    print(result)


    
