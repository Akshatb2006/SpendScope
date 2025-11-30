from pydantic import BaseModel, ConfigDict
from typing import Optional, List

class CategoryCreate(BaseModel):
    name: str
    description: Optional[str] = None
    keywords: Optional[List[str]] = []
    merchants: Optional[List[str]] = []
    parent_category_id: Optional[int] = None

class CategoryResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    
    model_config = ConfigDict(from_attributes=True)