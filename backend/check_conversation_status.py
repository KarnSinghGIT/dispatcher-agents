"""
Quick script to check conversation status from the saved JSON files.
Shows the latest conversation and how many turns it has.
"""

import json
from pathlib import Path
from datetime import datetime

def check_status():
    recordings_dir = Path(__file__).parent / "recordings"
    
    if not recordings_dir.exists():
        print("[X] No recordings directory found")
        return
    
    # Find all conversation JSON files
    json_files = sorted(recordings_dir.glob("conv_*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
    
    if not json_files:
        print("[ ] No conversation recordings found yet")
        return
    
    # Show latest conversation
    latest = json_files[0]
    
    try:
        with open(latest, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        room_name = data.get("room_name", "Unknown")
        timestamp = data.get("timestamp", "Unknown")
        message_count = data.get("message_count", 0)
        messages = data.get("messages", [])
        
        print("\n" + "=" * 60)
        print("LATEST CONVERSATION STATUS")
        print("=" * 60)
        print(f"Room: {room_name}")
        print(f"Time: {timestamp}")
        print(f"Turn count: {message_count}")
        print(f"Status: {'[OK] Completed' if message_count > 0 else '[..] In Progress'}")
        print("-" * 60)
        
        if messages:
            print("\nLast 5 messages:")
            for msg in messages[-5:]:
                speaker = msg.get("speaker", "Unknown")
                message = msg.get("message", "")
                print(f"  - {speaker}: {message}")
        
        print("\n" + "=" * 60)
        
        # Check for audio file
        audio_dir = recordings_dir / "audio"
        if audio_dir.exists():
            audio_files = list(audio_dir.glob(f"{room_name}*.mp3"))
            if audio_files:
                audio_file = audio_files[0]
                size_mb = audio_file.stat().st_size / (1024 * 1024)
                print(f"[AUDIO] {audio_file.name} ({size_mb:.2f}MB)")
            else:
                print("[..] Audio: Not yet saved")
        else:
            print("[!] Audio directory not found")
        
    except Exception as e:
        print(f"[ERROR] Error reading file: {e}")

if __name__ == "__main__":
    check_status()

