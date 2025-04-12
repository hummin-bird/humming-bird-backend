from __future__ import annotations

from typing import ClassVar

from pydantic import BaseModel, Field, AnyUrl

from portia.config import LLM_TOOL_MODEL_KEY
from portia.model import Message
from portia.tool import Tool, ToolRunContext

from typing import List, Union, Type
import os
import httpx
from portia.errors import ToolHardError, ToolSoftError
import httpx


class StringListSchema(BaseModel):
    items: List[str] = Field(..., min_items=5, max_items=5)


class ProductSchema(BaseModel):
    id: str
    name: str
    description: str
    image_url: AnyUrl
    website_url: AnyUrl


class ProductListSchema(BaseModel):
    products: List[ProductSchema]


class LLMToolSchema(BaseModel):
    """Input for LLM Tool."""

    task: str = Field(
        ...,
        description="The task to be completed by the LLM tool.",
    )


class UrlOnlySchema(BaseModel):
    url: AnyUrl


class LLMstructureTool(Tool[str]):
    """General purpose LLM tool. Customizable to user requirements. Won't call other tools."""

    LLM_TOOL_ID: ClassVar[str] = "llm_structure_tool"
    id: str = LLM_TOOL_ID
    name: str = "LLM Structure Tool"
    description: str = (
        "Jack of all trades tool to respond to a prompt by relying solely on LLM capabilities. "
        "YOU NEVER CALL OTHER TOOLS. You use your native capabilities as an LLM only. "
        "This includes using your general knowledge, your in-built reasoning "
        "and your code interpreter capabilities. This tool can be used to summarize the outputs of "
        "other tools, make general language model queries or to answer questions. This should be "
        "used only as a last resort when no other tool satisfies a step in a task, however if "
        "there are no other tools that can be used to complete a step or for steps that don't "
        "require a tool call, this SHOULD be used"
    )
    args_schema: type[BaseModel] = LLMToolSchema
    product_list_schema: type[BaseModel] = ProductListSchema
    output_schema: tuple[str, str] = (
        "str",
        "The LLM's response to the user query.",
    )
    prompt: str = """
        You are a Jack of all trades used to respond to a prompt by relying solely on LLM.
        capabilities. YOU NEVER CALL OTHER TOOLS. You use your native capabilities as an LLM
         only. This includes using your general knowledge, your in-built reasoning and
         your code interpreter capabilities. You exist as part of a wider system of tool calls
         for a multi-step task to be used to answers questions, summarize outputs of other tools
         and to make general language model queries. You might not have all the context of the
         wider task, so you should use your general knowledge and reasoning capabilities to make
         educated guesses and assumptions where you don't have all the information. Be concise and
         to the point.
        """
    tool_context: str = ""

    def run(self, ctx: ToolRunContext, task: str) -> str:
        """Run the LLMTool."""
        model = ctx.config.resolve_model(LLM_TOOL_MODEL_KEY)

        # Define system and user messages
        context = (
            "Additional context for the LLM tool to use to complete the task, provided by the "
            "run information and results of other tool calls. Use this to resolve any "
            "tasks"
        )
        if ctx.execution_context.plan_run_context:
            context += f"\nRun context: {ctx.execution_context.plan_run_context}"
        if self.tool_context:
            context += f"\nTool context: {self.tool_context}"
        content = task if not len(context.split("\n")) > 1 else f"{context}\n\n{task}"
        messages = [
            Message(role="user", content=self.prompt),
            Message(role="user", content=content),
        ]
        response = model.get_structured_response(
            messages, schema=self.product_list_schema
        )
        return response.model_dump(mode="json")



class ListSchema(BaseModel):
    products: List


class LLMlistTool(Tool[str]):
    """General purpose LLM tool. Customizable to user requirements. Won't call other tools."""

    LLM_TOOL_ID: ClassVar[str] = "llm_list_tool"
    id: str = LLM_TOOL_ID
    name: str = "LLM List Tool"
    description: str = (
        "Jack of all trades tool to respond to a prompt by relying solely on LLM capabilities. "
        "YOU NEVER CALL OTHER TOOLS. You use your native capabilities as an LLM only. "
        "This includes using your general knowledge, your in-built reasoning "
        "and your code interpreter capabilities. This tool can be used to summarize the outputs of "
        "other tools, make general language model queries or to answer questions. This should be "
        "used only as a last resort when no other tool satisfies a step in a task, however if "
        "there are no other tools that can be used to complete a step or for steps that don't "
        "require a tool call, this SHOULD be used"
    )
    args_schema: type[BaseModel] = LLMToolSchema
    list_schema: type[BaseModel] = StringListSchema
    output_schema: tuple[str, str] = (
        "str",
        "The LLM's response to the user query.",
    )
    prompt: str = """
        You are a jack-of-all-trades assistant that responds using only your native LLM capabilities. 
        You NEVER call other tools—instead, rely on your general knowledge, built-in reasoning, 
        and code interpreter skills. You are part of a larger system of tool calls used to answer 
        questions, summarize tool outputs, and handle general language tasks. Since you may not always 
        have full context, make smart assumptions based on reasoning. Be concise and to the point.
        """
    tool_context: str = ""

    def run(self, ctx: ToolRunContext, task: str) -> str:
        """Run the LLMTool."""
        model = ctx.config.resolve_model(LLM_TOOL_MODEL_KEY)

        # Define system and user messages
        context = (
            "Additional context for the LLM tool to use to complete the task, provided by the "
            "run information and results of other tool calls. Use this to resolve any "
            "tasks"
        )
        if ctx.execution_context.plan_run_context:
            context += f"\nRun context: {ctx.execution_context.plan_run_context}"
        if self.tool_context:
            context += f"\nTool context: {self.tool_context}"
        content = task if not len(context.split("\n")) > 1 else f"{context}\n\n{task}"
        messages = [
            Message(role="user", content=self.prompt),
            Message(role="user", content=content),
        ]
        response = model.get_structured_response(messages, schema=self.list_schema)
        return response.model_dump(mode="json")


MAX_RESULTS = 3


class SearchToolSchema(BaseModel):
    """Input for SearchTool."""

    search_query: str = Field(
        ...,
        description=(
            "The query to search for. For example, 'what is the capital of France?' or "
            "'who won the US election in 2020?'"
        ),
    )


class LogoSearchTool(Tool[str]):
    """Searches the internet to find answers to the search query provided.."""

    id: str = "logo_search_tool"
    name: str = "Logo Search Tool"
    description: str = (
        "Searches the internet (using Tavily) to find the official logo of the website provided in the search query. "
        "Returns only the URL of the logo image (preferably in PNG or SVG format). "
        "The search tool can access general website information but will only return a logo URL and no other data."
    )
    args_schema: type[BaseModel] = SearchToolSchema
    output_schema: tuple[str, str] = (
        "str",
        "The URL of the logo image (preferably in PNG or SVG format).",
    )
    should_summarize: bool = True

    def run(self, _: ToolRunContext, search_query: str) -> str:
        """Run the Search Tool."""
        api_key = os.getenv("TAVILY_API_KEY")
        if not api_key or api_key == "":
            raise ToolHardError("TAVILY_API_KEY is required to use search")

        url = "https://api.tavily.com/search"

        payload = {
            "query": search_query,
            "include_answer": True,
            "api_key": api_key,
        }
        headers = {"Content-Type": "application/json"}

        response = httpx.post(url, headers=headers, json=payload)
        response.raise_for_status()
        json_response = response.json()
        if "answer" in json_response:
            results = json_response["results"]
            return results[:MAX_RESULTS]
        raise ToolSoftError(f"Failed to get answer to search: {json_response}")

class WebsiteSearchTool(Tool[str]):
    """Searches the internet to find answers to the search query provided.."""

    id: str = "website_search_tool"
    name: str = "Website Search Tool"
    description: str = (
    "Searches the internet (using Tavily) to find one website provided in the search query. "
    "Returns only the URL of the website."
    "The search tool can access general website information but will only return a URL and no other data."
    )
    args_schema: type[BaseModel] = SearchToolSchema
    output_schema: tuple[str, str] = (
        "str",
        "The URL of the website.",
    )
    should_summarize: bool = True

    def run(self, _: ToolRunContext, search_query: str) -> str:
        """Run the Search Tool."""
        api_key = os.getenv("TAVILY_API_KEY")
        if not api_key or api_key == "":
            raise ToolHardError("TAVILY_API_KEY is required to use search")

        url = "https://api.tavily.com/search"
        headers = {"Content-Type": "application/json"}
        payload = {
            "query": search_query,
            "include_answer": True,
            "api_key": api_key,
        }

        # Configure client with timeout and retry settings
        client = httpx.Client(
            timeout=httpx.Timeout(
                connect=5.0,  # Time to establish connection
                read=10.0,    # Time to read response
                write=5.0,    # Time to write request
                pool=5.0      # Time to get connection from pool
            ),
            retries=3,        # Number of retries
            retry_delay=1.0   # Delay between retries in seconds
        )

        try:
            # Try the request with retries
            for attempt in range(3):
                try:
                    response = client.post(url, headers=headers, json=payload)
                    response.raise_for_status()
                    json_response = response.json()
                    
                    if "answer" in json_response:
                        results = json_response["results"]
                        return results[:MAX_RESULTS]
                    else:
                        raise ToolSoftError(f"Failed to get answer to search: {json_response}")
                        
                except (httpx.ReadTimeout, httpx.ConnectTimeout) as e:
                    if attempt == 2:  # Last attempt
                        raise ToolSoftError(f"Search timed out after {attempt + 1} attempts: {str(e)}")
                    continue
                except httpx.HTTPError as e:
                    raise ToolSoftError(f"HTTP error during search: {str(e)}")
                    
        finally:
            client.close()

        raise ToolSoftError("Failed to get search results after all attempts")

class SearchTool(Tool[str]):
    """Searches the internet to find answers to the search query provided.."""

    id: str = "search_tool"
    name: str = "Search Tool"
    description: str = (
        "Searches the internet (using Tavily) to find answers to the search query provided and "
        "returns those answers, including images, links and a natural language answer. "
        "The search tool has access to general information but can not return specific "
        "information on users or information not available on the internet."
    )
    args_schema: type[BaseModel] = SearchToolSchema
    output_schema: tuple[str, str] = ("str", "str: output of the search results")
    should_summarize: bool = True

    def run(self, _: ToolRunContext, search_query: str) -> str:
        """Run the Search Tool."""
        api_key = os.getenv("TAVILY_API_KEY")
        if not api_key or api_key == "":
            raise ToolHardError("TAVILY_API_KEY is required to use search")

        url = "https://api.tavily.com/search"
        headers = {"Content-Type": "application/json"}
        payload = { 
            "query": search_query,
            "include_answer": True,
            "api_key": api_key,
        }

    
        try:
            # Try the request with retries
            for attempt in range(3):
                try:
                    response = httpx.post(url, headers=headers, json=payload, timeout=30)
                    response.raise_for_status()
                    json_response = response.json()
                    
                    if "answer" in json_response:
                        results = json_response["results"]
                        return results[:MAX_RESULTS]
                    else:
                        raise ToolSoftError(f"Failed to get answer to search: {json_response}")
                        
                except (httpx.ReadTimeout, httpx.ConnectTimeout) as e:
                    if attempt == 2:  # Last attempt
                        raise ToolSoftError(f"Search timed out after {attempt + 1} attempts: {str(e)}")
                    continue
                except httpx.HTTPError as e:
                    raise ToolSoftError(f"HTTP error during search: {str(e)}")
                    
        finally:
            raise ToolSoftError(f"Failed to get answer to search: {json_response}")

        raise ToolSoftError("Failed to get search results after all attempts")
