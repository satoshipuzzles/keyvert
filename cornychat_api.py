import os
import json
import secrets
import requests
from typing import Dict, List, Optional, Union
from dataclasses import dataclass
import sys
import asyncio
from flask import Flask, jsonify, request
from flask_cors import CORS
import logging

app = Flask(__name__)
CORS(app)

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

@dataclass
class CornyChatConfig:
    base_url: str = "https://cornychat.com/_/pantry/api/v1"
    auth_token: Optional[str] = None
    pubkey: Optional[str] = None
    signature: Optional[str] = None

class CornyChatAPI:
    def __init__(self, config: Optional[CornyChatConfig] = None):
        self.config = config or CornyChatConfig()
        self.base_url = self.config.base_url

    def _get_headers(self) -> dict:
        """Get headers for API requests."""
        headers = {"Content-Type": "application/json"}
        if self.config and self.config.pubkey and self.config.signature:
            headers.update({
                "X-Auth-Pubkey": self.config.pubkey,
                "X-Auth-Signature": self.config.signature
            })
        return headers

    def authenticate(self, pubkey: str, signature: str) -> Dict:
        """Authenticate a user with their public key and signature"""
        try:
            # Basic validation
            if not pubkey or not isinstance(pubkey, str):
                raise ValueError("Invalid pubkey format")
            if not signature or not isinstance(signature, str):
                raise ValueError("Invalid signature format")

            # Clean inputs
            pubkey = pubkey.strip()
            signature = signature.strip()

            # For generated test keypairs, verify that signature matches private key
            if pubkey.startswith("gen_"):
                if signature[:16] == pubkey[4:]:
                    self.config.pubkey = pubkey
                    self.config.signature = signature
                    return {"success": True, "message": "Authenticated successfully"}
                else:
                    raise ValueError("Invalid signature for generated keypair")

            # For real Nostr keypairs, verify with the API
            response = requests.post(
                f"{self.config.base_url}/auth",
                headers={"Content-Type": "application/json"},
                json={"pubkey": pubkey, "signature": signature}
            )
            response.raise_for_status()
            
            auth_data = response.json()
            if auth_data.get("success"):
                self.config.pubkey = pubkey
                self.config.signature = signature
                return auth_data
            else:
                raise ValueError(auth_data.get("error", "Authentication failed"))
            
        except requests.exceptions.HTTPError as e:
            logger.error(f"Authentication failed: {str(e)}")
            if e.response.status_code == 401:
                raise ValueError("Invalid credentials")
            elif e.response.status_code == 429:
                raise ValueError("Too many authentication attempts")
            else:
                raise ValueError(f"Authentication failed: {str(e)}")
        except Exception as e:
            logger.error(f"Error during authentication: {str(e)}")
            raise ValueError(f"Authentication error: {str(e)}")

    def get_active_rooms(self) -> List[Dict]:
        """Fetch all active rooms and their users"""
        response = requests.get(
            f"{self.config.base_url}/roomlist/",
            headers=self._get_headers()
        )
        response.raise_for_status()
        return response.json()

    def get_room_details(self, room_id: str) -> Dict:
        """Get room details including active users"""
        # First check active rooms
        rooms = self.get_active_rooms()
        room = next((r for r in rooms if r["roomId"] == room_id or r["name"] == room_id), None)
        
        if room:
            return room
            
        # If not found, try direct API call
        response = requests.get(
            f"{self.config.base_url}/rooms/{room_id}",
            headers=self._get_headers()
        )
        response.raise_for_status()
        return response.json()

    def create_room(self, room_data: Dict) -> Dict:
        """Create a new room"""
        try:
            if not room_data.get("name"):
                raise ValueError("Room name is required")
            
            # Normalize room name
            room_name = "".join(c for c in room_data["name"] if c.isalnum() or c in "_-")
            
            # Get the authenticated pubkey from config
            pubkey = self.config.pubkey if self.config and self.config.pubkey else "npub1test0123456789"
            
            # Add the creator as owner, moderator and speaker
            owners = [pubkey]
            moderators = [pubkey]
            speakers = [pubkey]
            
            # Prepare payload with default values
            payload = {
                "name": room_name,
                "description": room_data.get("description", ""),
                "logoURI": room_data.get("logoURI", ""),
                "speakers": speakers,
                "moderators": moderators,
                "presenters": [],
                "owners": owners,
                "roomSlides": room_data.get("slides", []),
                "roomLinks": room_data.get("roomLinks", []),
                "currentSlide": 0,
                "stageOnly": room_data.get("isStageOnly", False),
                "videoEnabled": False,
                "color": room_data.get("color", "default"),
                "customEmojis": room_data.get("customEmojis", ["🌽","🍻","🧡","🤣","🤔","🤯","😴","☠️","💩","⚡","👏","🤙","💯","🎻"]),
                "customColor": room_data.get("customColor", {
                    "background": "rgba(0,0,0,1)",
                    "text": {"light": "#f4f4f4", "dark": "#111111"},
                    "buttons": {"primary": "rgba(0,0,0,1)"},
                    "avatarBg": "rgba(0,0,0,1)",
                    "icons": {"light": "#f4f4f4", "dark": "#111111"}
                }),
                "videoCall": False,
                "isPrivate": room_data.get("isPrivate", False),
                "isProtected": room_data.get("isProtected", False),
                "isRecordingAllowed": False,
                "passphraseHash": ""
            }
            
            response = requests.post(
                f"{self.config.base_url}/rooms/{room_name}",
                headers=self._get_headers(),
                json=payload
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            logger.error(f"Failed to create room: {str(e)}")
            raise ValueError(f"Failed to create room: {str(e)}")
        except Exception as e:
            logger.error(f"Error creating room: {str(e)}")
            raise ValueError(f"Error creating room: {str(e)}")

    def update_room(self, room_id: str, room_data: dict) -> dict:
        """Update an existing room."""
        try:
            # Normalize room ID
            room_id = "".join(c for c in room_id if c.isalnum() or c in "_-")
            
            # Get the authenticated pubkey from config
            pubkey = self.config.pubkey if self.config and self.config.pubkey else "npub1test0123456789"
            
            # Add the authenticated user as owner, moderator and speaker
            owners = [pubkey]
            moderators = [pubkey]
            speakers = [pubkey]
            
            # Prepare payload with default values
            payload = {
                "name": room_id,  # Include the room name
                "description": room_data.get("description", ""),
                "logoURI": room_data.get("logoURI", ""),
                "speakers": speakers,
                "moderators": moderators,
                "presenters": [],
                "owners": owners,
                "roomSlides": room_data.get("roomSlides", []),
                "roomLinks": room_data.get("roomLinks", []),
                "currentSlide": 0,
                "stageOnly": room_data.get("isStageOnly", False),
                "videoEnabled": False,
                "color": room_data.get("color", "default"),
                "customEmojis": room_data.get("customEmojis", ["🌽","🍻","🧡","🤣","🤔","🤯","😴","☠️","💩","⚡","👏","🤙","💯","🎻"]),
                "customColor": room_data.get("customColor", {
                    "background": "rgba(0,0,0,1)",
                    "text": {"light": "#f4f4f4", "dark": "#111111"},
                    "buttons": {"primary": "rgba(0,0,0,1)"},
                    "avatarBg": "rgba(0,0,0,1)",
                    "icons": {"light": "#f4f4f4", "dark": "#111111"}
                }),
                "videoCall": False,
                "isPrivate": room_data.get("isPrivate", False),
                "isProtected": room_data.get("isProtected", False),
                "isRecordingAllowed": False,
                "passphraseHash": ""
            }
            
            base_url = self.config.base_url if self.config else self.base_url
            response = requests.put(
                f"{base_url}/rooms/{room_id}",
                headers=self._get_headers(),
                json=payload
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                raise ValueError(f"Room {room_id} not found")
            else:
                raise ValueError(f"Failed to update room: {e.response.text}")
        except Exception as e:
            raise ValueError(f"Failed to update room: {str(e)}")

    def get_zap_goal(self, emoji: str = "🌽") -> Dict:
        """Get zap goal for specified emoji"""
        response = requests.get(
            f"{self.config.base_url}/zapgoal/{emoji}",
            headers=self._get_headers()
        )
        response.raise_for_status()
        return response.json()

    def get_user_info(self, user_id: str) -> Dict:
        """Get user information including their lightning wallet and npub"""
        response = requests.get(
            f"{self.config.base_url}/users/{user_id}",
            headers=self._get_headers()
        )
        response.raise_for_status()
        return response.json()

    def get_total_active_users(self) -> int:
        """Get total number of active users across all rooms"""
        rooms = self.get_active_rooms()
        return sum(room.get("userCount", 0) for room in rooms)

    @staticmethod
    def generate_keypair() -> Dict[str, str]:
        """Generate a public/private key pair when no Nostr extension is available"""
        private_key = secrets.token_hex(32)
        public_key = f"gen_{private_key[:16]}"
        return {"privateKey": private_key, "publicKey": public_key}

# MCP Command Definitions
def mcp_cornychat_get_active_rooms():
    """Get list of all active CornyCHAT rooms"""
    api = CornyChatAPI()
    return api.get_active_rooms()

def mcp_cornychat_get_room_details(room_id: str):
    """Get detailed information about a specific room"""
    api = CornyChatAPI()
    return api.get_room_details(room_id)

def mcp_cornychat_create_room(name: str, description: str = "", logo_uri: str = "", 
                            is_stage_only: bool = False, is_protected: bool = False,
                            owner_pubkey: Optional[str] = None):
    """Create a new CornyCHAT room"""
    api = CornyChatAPI()
    
    if not owner_pubkey:
        keypair = api.generate_keypair()
        owner_pubkey = keypair["publicKey"]
        
    room_data = {
        "name": name,
        "description": description,
        "logoURI": logo_uri,
        "isStageOnly": is_stage_only,
        "isProtected": is_protected,
        "owner_pubkey": owner_pubkey
    }
    
    return api.create_room(room_data)

def mcp_cornychat_get_user_info(user_id: str):
    """Get user information including lightning wallet and npub"""
    api = CornyChatAPI()
    return api.get_user_info(user_id)

def mcp_cornychat_get_active_users():
    """Get total count and list of active users across all rooms"""
    api = CornyChatAPI()
    rooms = api.get_active_rooms()
    
    active_users = []
    for room in rooms:
        if room.get("userInfo"):
            for user in room["userInfo"]:
                if user not in active_users:  # Avoid duplicates
                    active_users.append(user)
    
    return {
        "total_count": len(active_users),
        "users": active_users
    }

async def handle_command(command_name: str, params: Dict) -> Dict:
    """Handle incoming MCP commands"""
    api = CornyChatAPI()
    
    if command_name == "mcp_cornychat_get_active_rooms":
        return {"result": api.get_active_rooms()}
    
    elif command_name == "mcp_cornychat_get_room_details":
        return {"result": api.get_room_details(params["room_id"])}
    
    elif command_name == "mcp_cornychat_create_room":
        return {"result": api.create_room(params)}
    
    elif command_name == "mcp_cornychat_get_user_info":
        return {"result": api.get_user_info(params["user_id"])}
    
    elif command_name == "mcp_cornychat_get_active_users":
        rooms = api.get_active_rooms()
        active_users = []
        for room in rooms:
            if room.get("userInfo"):
                for user in room["userInfo"]:
                    if user not in active_users:
                        active_users.append(user)
        return {
            "result": {
                "total_count": len(active_users),
                "users": active_users
            }
        }
    
    return {"error": f"Unknown command: {command_name}"}

async def main():
    """Main MCP server loop"""
    while True:
        try:
            line = await asyncio.get_event_loop().run_in_executor(None, sys.stdin.readline)
            if not line:
                break
                
            request = json.loads(line)
            command = request.get("command")
            params = request.get("params", {})
            
            response = await handle_command(command, params)
            print(json.dumps(response), flush=True)
            
        except Exception as e:
            print(json.dumps({"error": str(e)}), flush=True)

# Initialize API with config
config = CornyChatConfig()
api = CornyChatAPI(config)

@app.route("/roomlist/")
def get_rooms():
    """Get list of active rooms"""
    try:
        logger.debug("Fetching active rooms")
        rooms = api.get_active_rooms()
        logger.debug(f"Successfully fetched {len(rooms)} rooms")
        return jsonify(rooms)
    except Exception as e:
        logger.error(f"Error fetching rooms: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route("/rooms/<room_id>")
def get_room(room_id):
    """Get details for a specific room"""
    try:
        logger.debug(f"Fetching details for room {room_id}")
        room = api.get_room_details(room_id)
        logger.debug(f"Successfully fetched details for room {room_id}")
        return jsonify(room)
    except Exception as e:
        logger.error(f"Error fetching room {room_id}: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route("/rooms/<room_name>", methods=["POST"])
def create_room(room_name):
    """Create a new room"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400

        # Get auth headers
        pubkey = request.headers.get("X-Auth-Pubkey")
        signature = request.headers.get("X-Auth-Signature")
        
        # Add room name to data
        data["name"] = room_name
        
        logger.debug(f"Creating room {room_name}")
        result = api.create_room(data)
        logger.debug(f"Successfully created room {room_name}")
        return jsonify(result)
    except ValueError as e:
        logger.error(f"Error creating room: {str(e)}")
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logger.error(f"Error creating room: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/rooms/<room_id>', methods=['PUT'])
def update_room_endpoint(room_id):
    try:
        room_data = request.get_json()
        if not room_data:
            return jsonify({"error": "No update data provided"}), 400
            
        # Get auth headers
        pubkey = request.headers.get("X-Auth-Pubkey")
        signature = request.headers.get("X-Auth-Signature")
        
        if pubkey and signature:
            # Create new config with auth
            config = CornyChatConfig(pubkey=pubkey, signature=signature)
            api.config = config
            
        updated_room = api.update_room(room_id, room_data)
        return jsonify(updated_room)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"Failed to update room: {str(e)}"}), 500

@app.route("/users/active")
def get_active_users():
    """Get count of active users"""
    try:
        logger.debug("Fetching active users")
        rooms = api.get_active_rooms()
        total_users = sum(len(room.get("users", [])) for room in rooms)
        logger.debug(f"Found {total_users} active users")
        return jsonify({"active_users": total_users})
    except Exception as e:
        logger.error(f"Error fetching active users: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route("/auth", methods=["POST"])
def authenticate():
    """Handle user authentication"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
            
        pubkey = data.get("pubkey")
        signature = data.get("signature")
        
        if not pubkey or not signature:
            return jsonify({"error": "Missing pubkey or signature"}), 400
            
        # Basic validation
        if not isinstance(pubkey, str) or not pubkey.strip():
            return jsonify({"error": "Invalid pubkey format"}), 400
        if not isinstance(signature, str) or not signature.strip():
            return jsonify({"error": "Invalid signature format"}), 400
            
        try:
            result = api.authenticate(pubkey, signature)
            return jsonify(result)
        except ValueError as e:
            return jsonify({"error": str(e)}), 401
        except Exception as e:
            return jsonify({"error": str(e)}), 500
            
    except Exception as e:
        logger.error(f"Error in authentication route: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route("/generate-keypair", methods=["POST"])
def generate_keypair_endpoint():
    """Generate a new keypair for testing"""
    try:
        keypair = api.generate_keypair()
        return jsonify({
            "success": True,
            "keypair": keypair
        })
    except Exception as e:
        logger.error(f"Error generating keypair: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True) 