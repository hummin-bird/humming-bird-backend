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
)
import os
import json

load_dotenv()
GOOGLE_API_KEY = os.getenv("GEMINI_API_KEY")
INITIATION = "The user wants to build a product,\
        step 1: Find out which type of product does the user want to \
        build, choose from a list of products [website, webApp, mobileApp, desktopApp]. \
        step 2: find out what information is needed form  before building the product and make a bullet point lis, save to a empty dictionary with user_id. \
        step 3: check user message, if the user message answer the information key in the dictionary, fill up the value in the dictionary. \
        step 4: Check if the dictionary is full. \
        step 5: if the dictionary is not full, Pause the plan run, trigger clarification plan. "

# GENERATION = " extract the information dictionary with corresponding user_id. \
#         step 1: if the dictionary is full, \
#        step 6: Keep asking until the storage has all the information required to start building. \
#         step 7: Then define the development steps in a bullet list. \
#         step 8: For each step, search the internet \
#         and give me 5 best tools i can use."

CLARIFICATION = (
    "The user has provided the following information: information_dictionary. \
                Based on the information required before building the product type. \
                Find out what kind of information is missing. \
                Construct a question to ask user for the missing information."
)

# Instantiate a Portia instance. Load it with the default config and with the example tools.
google_config = Config.from_default(
    storage_class=StorageClass.CLOUD,
    llm_provider=LLMProvider.GOOGLE_GENERATIVE_AI,
    llm_model_name=LLMModel.GEMINI_2_0_FLASH,
    google_api_key=GOOGLE_API_KEY,
)
# Instantiate a Portia instance. Load it with the config and with the example tools.
portia = Portia(
    config=google_config,
    tools=PortiaToolRegistry(google_config) + open_source_tool_registry,
)

with execution_context(end_user_id="demo"):
    plan = portia.plan(INITIATION)

# Get the plan data as a Python dictionary
plan_data = plan.model_dump()
# Save to a file
with open(
    "humming-bird-backend/app/services/initiation_plan.json", "w", encoding="utf-8"
) as f:
    json.dump(plan_data, f, indent=2)

