import requests
import logging

logger = logging.getLogger(__name__)

class BitcoinAPI:
    def __init__(self):
        self.base_url = "https://blockchain.info"
        
    def get_address_info(self, address):
        """Get balance and transaction info for a Bitcoin address"""
        try:
            response = requests.get(f"{self.base_url}/rawaddr/{address}")
            if response.status_code == 200:
                data = response.json()
                return {
                    "balance": float(data.get("final_balance", 0)) / 100000000,  # Convert satoshis to BTC
                    "total_received": float(data.get("total_received", 0)) / 100000000,
                    "total_sent": float(data.get("total_sent", 0)) / 100000000,
                    "tx_count": data.get("n_tx", 0)
                }
            else:
                logger.error(f"Failed to fetch address info: {response.status_code}")
                return {
                    "balance": 0.0,
                    "total_received": 0.0,
                    "total_sent": 0.0,
                    "tx_count": 0
                }
        except Exception as e:
            logger.error(f"Error fetching address info: {e}")
            return {
                "balance": 0.0,
                "total_received": 0.0,
                "total_sent": 0.0,
                "tx_count": 0
            }

    def decode_transaction(self, tx_hex):
        """Decode a raw transaction hex"""
        try:
            response = requests.post(
                f"{self.base_url}/rawtx/decode", 
                data={"tx": tx_hex}
            )
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Failed to decode transaction: {response.status_code}")
                return None
        except Exception as e:
            logger.error(f"Error decoding transaction: {e}")
            return None

    def get_transaction(self, txid):
        """Get transaction details by txid"""
        try:
            response = requests.get(f"{self.base_url}/rawtx/{txid}")
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Failed to fetch transaction: {response.status_code}")
                return None
        except Exception as e:
            logger.error(f"Error fetching transaction: {e}")
            return None 