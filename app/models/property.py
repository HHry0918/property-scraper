import uuid
from pydantic import BaseModel, Field

class PropertyListingExtraInfo(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4())) # must match the id of the PropertyListing it belongs to
    has_pool: bool = False # If True, the property has a swimming pool
    has_garage: bool = False # If True, the property has a garage
    has_garden: bool = False # If True, the property has a garden or backyard
    has_balcony: bool = False # If True, the property has a balcony
    has_air_conditioning: bool = False # If True, the property has air conditioning
    air_conditioning_type: str = "" # Type of air conditioning (e.g., split system, ducted, evaporative)
    has_heating: bool = False # If True, the property has heating
    has_fireplace: bool = False # If True, the property has a fireplace
    has_security_system: bool = False # If True, the property has a security system
    has_solar_panels: bool = False # If True, the property has solar panels
    has_study: bool = False # If True, the property has a study or office


class PropertyListingMultiLevelInfo(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4())) # must match the id of the PropertyListing it belongs to
    is_multi_level: bool = False # If True, the property has multiple levels or floors
    number_of_levels: int = 0 # Number of levels or floors in the property


class PropertyListingSellingInfo(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4())) # must match the id of the PropertyListing it belongs to
    price: float = 0.0 # Current price of the property
    is_sold: bool = False
    price_history: list = [] # List of previous prices and dates, if available
    is_price_hidden: bool = False # If True, the price is not displayed or require "Contact Agent" to view
    is_auction: bool = False # If True, the property is being sold via auction
    auction_date: str = "" # If is_auction is True, this field contains the auction date in ISO format (YYYY-MM-DD HH:MM)
    sell_history: list = [] # List of previous sale prices and dates, if available

    
class PropertyListing(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4())) # Unique identifier for the property listing
    source: str # domain or realestate source name
    address: str
    suburb: str
    state: str
    postcode: str
    price_info: PropertyListingSellingInfo = Field(default_factory=PropertyListingSellingInfo)
    bedrooms: int = 0
    bathrooms: int = 0
    car_spaces: int = 0
    property_type: str = "" # House, Townhouse, Apartment, Land, etc.
    is_duplex: bool = False # If True, the property is a duplex or multi-unit dwelling
    land_size: float = 0.0 # in square meter
    url: str
    multi_level_info: PropertyListingMultiLevelInfo = Field(default_factory=PropertyListingMultiLevelInfo)
    extra_info: PropertyListingExtraInfo = Field(default_factory=PropertyListingExtraInfo)
    note: str = "" # Additional notes or comments about the property