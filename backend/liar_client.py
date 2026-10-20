import os
import json
import requests
from typing import Any, Dict

from backend.config import LIAR_RPC_ENDPOINT, LIAR_API_KEY

class LiarClient:
    """Simple JSON‑RPC client for the external LIAR blockchain network.
    The LIAR network expects JSON‑RPC 2.0 POST requests with an optional
    ``Authorization: Bearer <API_KEY>`` header.
    """

    def __init__(self, endpoint: str = None, api_key: str = None):
        self.endpoint = endpoint or LIAR_RPC_ENDPOINT
        self.api_key = api_key or LIAR_API_KEY
        self.session = requests.Session()
        if self.api_key:
            self.session.headers.update({"Authorization": f"Bearer {self.api_key}"})
        self.session.headers.update({"Content-Type": "application/json"})

    def _post(self, method: str, params: Any = None) -> Dict[str, Any]:
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": method,
            "params": params or {}
        }
        response = self.session.post(self.endpoint, data=json.dumps(payload), timeout=10)
        response.raise_for_status()
        data = response.json()
        if "error" in data:
            raise RuntimeError(f"LIAR RPC error: {data['error']}")
        return data.get("result")

    def get_latest_block(self) -> Dict[str, Any]:
        """Fetch the latest block from the LIAR chain."""
        return self._post("eth_getBlockByNumber", ["latest", True])

    def submit_block(self, block_data: Dict[str, Any]) -> str:
        """Submit a forensic block to the LIAR network.
        The exact RPC method depends on the network contract; here we use a generic
        ``liar_submitBlock`` placeholder that the project can adapt.
        """
        return self._post("liar_submitBlock", block_data)
