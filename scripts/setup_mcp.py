"""
Title: setup_mcp.py Script
Description: Script for setup_mcp.
"""

import sys
import os
import json

# Ensure we can import from parent directory
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from bithub.bithub_auth import BithubAuth

def main():
    print("=== Discourse MCP Setup ===")
    
    # 1. Ask for Site URL
    default_url = "https://hub.bitwiki.org"
    try:
        site_url = input(f"Enter Site URL [{default_url}]: ").strip()
    except EOFError:
        site_url = ""
        
    if not site_url:
        site_url = default_url
    
    # 2. Generate RSA keys
    print("\n[+] Generating RSA Key Pair...")
    auth = BithubAuth()
    auth.generate_key_pair()
    
    # 3. Print Auth URL
    app_name = "Agent Zero MCP"
    scopes = "read,write,push,notifications,session_info,chat"
    link = auth.generate_auth_link(site_url, app_name, scopes)
    
    print("\n" + "="*60)
    print("ACTION REQUIRED: Open this URL in your browser:")
    print(link)
    print("="*60 + "\n")
    
    # 4. Ask user to paste payload
    print("After authorizing, you will receive a payload string.")
    try:
        encrypted_payload = input("Paste the payload here: ").strip()
    except EOFError:
        print("[-] No input received. Aborting.")
        return
    
    if not encrypted_payload:
        print("[-] No payload entered. Aborting.")
        return

    # 5. Decrypt payload
    try:
        print("\n[+] Decrypting payload...")
        decrypted_json_str = auth.decrypt_payload(encrypted_payload)
        payload_data = json.loads(decrypted_json_str)
        
        api_key = payload_data.get("key")
        if not api_key:
            print("[-] Error: 'key' not found in decrypted payload.")
            print(f"Payload content: {decrypted_json_str}")
            return
            
        print(f"[+] API Key extracted successfully.")
        
    except Exception as e:
        print(f"[-] Decryption error: {e}")
        return

    # 6. Save agent-profile.json
    profile_data = {
        "url": site_url,
        "key": api_key
    }
    
    output_file = "agent-profile.json"
    with open(output_file, "w") as f:
        json.dump(profile_data, f, indent=2)
        
    print(f"[+] Configuration saved to {output_file}")
    print("Setup complete!")

if __name__ == "__main__":
    main()
