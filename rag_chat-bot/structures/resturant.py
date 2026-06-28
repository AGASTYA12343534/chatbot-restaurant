from pydantic import BaseModel, Field
from typing import List, Optional
from bson import ObjectId

class Restaurant(BaseModel):
    name: str
    address: str
    phone_number: str
    menu_items: Optional[List[str]] = [] # list of MenuItem IDs (as strings for simplicity)
    rating: Optional[float] = None
    opening_hours: str
    dietary_options: Optional[List[str]] = []
    price_range: str
    cuisine: Optional[str] = []
    is_open: Optional[bool] = Field(default=True)