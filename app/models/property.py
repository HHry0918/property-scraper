import uuid
from typing import Optional
from pydantic import BaseModel, Field


class PropertyListing(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    source: str
    address: str
    suburb: str
    state: str
    postcode: str
    price: str = "Contact Agent"
    bedrooms: int = 0
    bathrooms: int = 0
    car_spaces: int = 0
    url: str
