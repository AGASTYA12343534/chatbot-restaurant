from pydantic import BaseModel, Field
from typing import Dict, Union

class MenuItem(BaseModel):
    
    name: str  # Name of the menu item
    description: str = Field(default="")  # Description can be empty string, providing flexibility for optional details
    price: float  # Price of the menu item, typically a float to support decimal values
    attributes: Dict[str, Union[str, int]]  # Key-value pairs for item attributes (e.g., size, spice level, etc.)
    restaurant_id: str  # Foreign key reference to the restaurant; links the menu item to its restaurant
