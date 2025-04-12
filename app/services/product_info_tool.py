from pathlib import Path
import pandas as pd
import json
from pydantic import BaseModel, Field
from portia.tool import Tool, ToolRunContext

ProductInfo = {"Target Audience": "",
               "Product Purpose and Goals": "",
               "Features and Functionality": "",
               "Budget and Resources": "",
               "Market Research": ""}


class ProductInfoToolSchema(BaseModel):
    """Schema defining the inputs for the ProductInfoTool."""

    target_audience: str = Field(
        default="",
        description="The Target Audience for the product",
    )
    product_purpose: str = Field(
        default="",
        description="The Product Purpose and Goals",
    )
    features: str = Field(
        default="",
        description="The Features and Functionality",
    )
    budget: str = Field(
        default="",
        description="The Budget and Resources",
    )
    market_research: str = Field(
        default="",
        description="The Market Research",
    )


class ProductInfoTool(Tool[str]):
    """Updates the ProductInfo dictionary with information from previous steps."""

    id: str = "product_info_tool"
    name: str = "product info tool"
    description: str = "Fill up the product information dictionary with values from previous steps"
    args_schema: type[BaseModel] = ProductInfoToolSchema
    output_schema: tuple[str, str] = ("str", "A JSON string of the updated product information")

    def run(self, _: ToolRunContext, **kwargs) -> dict[str, any]:       
        """Run the ProductInfoTool to update the product information dictionary."""
        # Create a copy of the ProductInfo dictionary to avoid modifying the global one
        product_info = ProductInfo
        
        # Update the dictionary with values from the inputs
        if "target_audience" in kwargs:
            ProductInfo["Target Audience"] += kwargs["target_audience"]
        
        if "product_purpose" in kwargs:
            ProductInfo["Product Purpose and Goals"] += kwargs["product_purpose"]
        
        if "features" in kwargs:
            ProductInfo["Features and Functionality"] += kwargs["features"]
        
        if "budget" in kwargs:
            ProductInfo["Budget and Resources"] += kwargs["budget"]
        
        if "market_research" in kwargs:
            ProductInfo["Market Research"] += kwargs["market_research"]

        # Check if the dictionary is full
        if all(value != "" for value in ProductInfo.values()):
            ProductInfo["clarification_flag"] = True
        else:
            ProductInfo["clarification_flag"] = False
        
        return ProductInfo
    


        