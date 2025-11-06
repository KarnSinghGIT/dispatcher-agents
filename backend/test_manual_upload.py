"""
Manual test to verify audio upload endpoint works.
"""

import requests
import sys
from pathlib import Path

API_URL = "http://localhost:8000"
ROOM_NAME = "test_room_manual"

# Create a small test audio file (WebM header)
test_audio = b"RIFF" + b"\x00" * 100  # Simple WebM-like header

print("[TEST] Starting manual upload test...")
print(f"[TEST] API: {API_URL}")
print(f"[TEST] Room: {ROOM_NAME}")
print(f"[TEST] File size: {len(test_audio)} bytes")

try:
    # Upload the test file
    files = {'audio': (f'{ROOM_NAME}.mp3', test_audio, 'audio/mpeg')}
    response = requests.post(f"{API_URL}/api/v1/rooms/{ROOM_NAME}/upload-audio", files=files)
    
    print(f"\n[TEST] Upload Response Status: {response.status_code}")
    print(f"[TEST] Response: {response.json()}")
    
    if response.status_code == 200:
        print("\n[TEST] ✓ Upload successful!")
        
        # Try to retrieve it
        print("\n[TEST] Trying to retrieve audio...")
        get_response = requests.get(f"{API_URL}/api/v1/rooms/{ROOM_NAME}/audio")
        print(f"[TEST] Retrieve Status: {get_response.status_code}")
        print(f"[TEST] Content-Type: {get_response.headers.get('content-type')}")
        print(f"[TEST] Data size: {len(get_response.content)} bytes")
        
        if get_response.status_code == 200:
            print("[TEST] ✓ Retrieval successful!")
    else:
        print(f"\n[TEST] ✗ Upload failed!")
        print(f"[TEST] Error: {response.text}")

except Exception as e:
    print(f"\n[TEST] ✗ Error: {e}")
    sys.exit(1)

print("\n[TEST] Done!")

