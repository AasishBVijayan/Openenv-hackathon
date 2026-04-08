import sys
import os
import uvicorn
from openenv_core.env_server import create_app

# Point it to the root directory
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from env import InventoryEnv
from models import InventoryAction, InventoryObservation

# Create the FastAPI application
app = create_app(
    InventoryEnv,
    InventoryAction,
    InventoryObservation,
)

# The validator strictly requires this exact function and naming
def main():
    uvicorn.run("server.app:app", host="0.0.0.0", port=8000)

if __name__ == "__main__":
    main()