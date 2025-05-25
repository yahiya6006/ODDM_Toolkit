# MIT License
# 
# Copyright (c) 2025 Yahiya Mulla
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import os
import uuid
import base64
import hashlib
from cryptography.fernet import Fernet
import json
import platform
import subprocess
from pathlib import Path

def _generate_encryption_key():
    """Generate a unique encryption key based on the system's UUID."""
    machine_id = str(uuid.getnode()).encode()  # Get the machine's UUID
    hashed_uuid = hashlib.sha256(machine_id).digest()[:32]  # Hash the UUID
    _key = base64.urlsafe_b64encode(hashed_uuid) # Convert to base64 to make it a valid Fernet key
    return Fernet(_key)  # Return the encryption key

def find_project_root(folder_name="ODDM_Toolkit") -> Path:
    """Walks up from the current file or cwd to locate the project root."""
    path = Path(__file__).resolve().parent

    for parent in [path] + list(path.parents):
        if parent.name == folder_name:
            return parent

    raise FileNotFoundError(f"Could not find root directory named '{folder_name}' from path {path}")

def create_oddm_setup_file(data: dict):
    """Creates the ODDM Toolkits first time setup file."""

    if not isinstance(data, dict):
        return {"success": False, "error":"Credentials must be a dictionary." }
    
    try:
        config_dir = find_project_root()
    except FileNotFoundError as e:
        return {"success": False, "error": str(e)}
    
    config_file = config_dir / ".oddm_setup_config"
    print(f"Config file path: {config_file}")

    gen_key = _generate_encryption_key()
    json_data = json.dumps(data).encode()
    encrypted_data = gen_key.encrypt(json_data)

    if os.path.exists(config_file):
        os.remove(config_file)
    with open(config_file, "wb") as file:
        file.write(encrypted_data)
    if platform.system() == "Windows":
        subprocess.call(["attrib", "+h", config_file])  # Hide file on Windows
    
    return {"success": True, "message": "ODDM Toolkit setup file created."}

def get_oddm_setup_credentials():
    """Get the ODDM Toolkit setup credentials."""

    try:
        config_dir = find_project_root()
    except FileNotFoundError as e:
        return {"success": False, "error": str(e)}
    
    config_file = config_dir / ".oddm_setup_config"
    print(f"Config file path: {config_file}")

    if not os.path.exists(config_file):
        return {"success": False, "error": "ODDM Toolkit setup file does not exist."}

    gen_key = _generate_encryption_key()
    with open(config_file, "rb") as file:
        encrypted_data = file.read()
    decrypted_data = gen_key.decrypt(encrypted_data)

    return {"success": True, "data":json.loads(decrypted_data) }

def check_if_oddm_setup_file_exists():
    """Check if the ODDM Toolkit setup file exists."""
    
    try:
        config_dir = find_project_root()
    except FileNotFoundError as e:
        return {"success": False, "error": str(e)}
    
    config_file = config_dir / ".oddm_setup_config"
    print(f"Config file path: {config_file}")

    if os.path.exists(config_file):
        return {"success": True, "message": "ODDM Toolkit setup file exists."}
    else:
        return {"success": False, "error": "ODDM Toolkit setup file does not exist."}