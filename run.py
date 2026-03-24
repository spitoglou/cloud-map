"""Uvicorn wrapper — start the Cloud Map web dashboard."""

import uvicorn

from cloud_map.config import load_inventory
from cloud_map.web import app, configure

HOST = "0.0.0.0"
PORT = 8000
REFRESH = 30
INVENTORY = "inventory.yaml"

inventory = load_inventory(INVENTORY)
configure(inventory, refresh=REFRESH)

if __name__ == "__main__":
    uvicorn.run(app, host=HOST, port=PORT, log_level="info")
