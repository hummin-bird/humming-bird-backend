from pydantic import BaseModel
from typing import Optional, List, Dict, Any


class ProductSuggestion(BaseModel):
    id: str
    name: str
    description: str
    website_url: Optional[str]
    image_url: Optional[str]
