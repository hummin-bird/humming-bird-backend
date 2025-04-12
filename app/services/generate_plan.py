from dotenv import load_dotenv
from portia import (
    Portia,
    Config,
    PortiaToolRegistry,
    StorageClass,
    LLMProvider,
    open_source_tool_registry,
    execution_context,
    LLMModel,
    InMemoryToolRegistry
)
import os
import json
from custom_tool import LLMstructureTool, LLMlistTool

custom_tool_registry = InMemoryToolRegistry.from_local_tools(
    [
        LLMstructureTool(),
        LLMlistTool(),
    ],
)

load_dotenv() 
GOOGLE_API_KEY = os.getenv("GEMINI_API_KEY")
INITIATION = "The user wants to build a product,\
        step 1: Find out which type of product does the user want to \
        build, choose from a list of products [website, webApp, mobileApp, desktopApp]. \
        step 2: find out what information is needed form  before building the product and make a bullet point lis, save to a empty dictionary with user_id. \
        step 3: check user message, if the user message answer the information key in the dictionary, fill up the value in the dictionary. \
        step 4: Check if the dictionary is full. \
        step 5: if the dictionary is not full, Pause the plan run, trigger clarification plan. "

LOGO_SEARCH = "Search online for the official logo image URL of the product available on the website: https://chatgpt.com. Prefer high-quality, transparent PNG or SVG formats. Return a direct link to the logo hosted on the official domain if possible. "

CLARIFICATION = "The user has provided more information. I already have a product info dictionary.\
                I need to check whether the user's answer fille up the product info dictionary. "


# Get the directory of the current script
current_dir = os.path.dirname(os.path.abspath(__file__))

# Instantiate a Portia instance. Load it with the default config and with the example tools.
openai_config = Config.from_default(
            storage_class=StorageClass.CLOUD,
            llm_provider=LLMProvider.OPENAI,
            llm_model_name=LLMModel.GPT_4_O_MINI,
        )




        # Instantiate a Portia instance. Load it with the config and with the example tools.
portia = Portia(
                        config=openai_config,
                        tools=[open_source_tool_registry.get_tool("llm_tool"),
                               open_source_tool_registry.get_tool("search_tool"),
                               custom_tool_registry.get_tool("llm_structure_tool"),
                              ],
                         )
        # Instantiate a Portia instance. Load it with the config and with the example tools.


with execution_context(end_user_id="demo"):
    plan = portia.plan(LOGO_SEARCH)

# Get the plan data as a Python dictionary
plan_data = plan.model_dump()
# Save to a file
with open(os.path.join(current_dir, 'logo_search_plan.json'), 'w', encoding='utf-8') as f:
    json.dump(plan_data, f, indent=2)