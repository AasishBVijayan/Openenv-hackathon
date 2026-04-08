from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

class InventoryAction(BaseModel):
    action_type: str = Field(
        ..., 
        description="Must be one of: 'check_inventory', 'order_stock', 'update_price'"
    )
    sku: Optional[str] = Field(None, description="The product ID, e.g., 'SKU-101'")
    quantity: Optional[int] = Field(None, description="How many units to order")
    price: Optional[float] = Field(None, description="The new price to set")

class InventoryObservation(BaseModel):
    echoed_message: str = Field(..., description="Feedback from the system")
    inventory_data: Optional[Dict[str, Any]] = Field(None, description="Current stock and prices")

class EnvResult(BaseModel):
    observation: InventoryObservation
    reward: float
    done: bool
    info: dict = {}