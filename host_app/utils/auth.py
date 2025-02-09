import os
import uuid
import base64
import hashlib
from cryptography.fernet import Fernet
import json
import platform
import subprocess

def _generate_encryption_key():
    """Generate a unique encryption key based on the system's UUID."""
    machine_id = str(uuid.getnode()).encode()  # Get the machine's UUID
    hashed_uuid = hashlib.sha256(machine_id).digest()[:32]  # Hash the UUID
    _key = base64.urlsafe_b64encode(hashed_uuid) # Convert to base64 to make it a valid Fernet key
    return Fernet(_key)  # Return the encryption key

def create_oddm_setup_file(data: dict):
    """Creates the ODDM Toolkits first time setup file."""

    if not isinstance(data, dict):
        return {"success": False, "error":"Credentials must be a dictionary." }

    gen_key = _generate_encryption_key()
    json_data = json.dumps(data).encode()
    encrypted_data = gen_key.encrypt(json_data)
    if os.path.exists(".oddm_setup_config"):
        os.remove(".oddm_setup_config")
    with open(".oddm_setup_config", "wb") as file:
        file.write(encrypted_data)
    if platform.system() == "Windows":
        subprocess.call(["attrib", "+h", ".oddm_setup_config"])  # Hide file on Windows
    
    return {"success": True, "message": "ODDM Toolkit setup file created."}

def get_oddm_setup_credentials():
    """Get the ODDM Toolkit setup credentials."""

    if not os.path.exists(".oddm_setup_config"):
        return {"success": False, "error": "ODDM Toolkit setup file does not exist."}

    gen_key = _generate_encryption_key()
    with open(".oddm_setup_config", "rb") as file:
        encrypted_data = file.read()
    decrypted_data = gen_key.decrypt(encrypted_data)

    return {"success": True, "data":json.loads(decrypted_data) }