"""
Test script for audio recording functionality.

This script tests the complete audio recording flow:
1. Upload audio file endpoint
2. Retrieve audio file endpoint
3. File storage and retrieval

Run this script with:
    python test_audio_recording.py
"""

import asyncio
import sys
from pathlib import Path
import io

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from fastapi.testclient import TestClient
from src.api.main import app

client = TestClient(app)


def create_mock_audio_file(size_kb: int = 100) -> io.BytesIO:
    """Create a mock audio file for testing."""
    # Create a simple mock MP3-like file
    mock_data = b"ID3" + b"\x00" * (size_kb * 1024 - 3)
    return io.BytesIO(mock_data)


def test_audio_upload():
    """Test audio upload endpoint."""
    print("\n🧪 TEST 1: Audio Upload")
    print("-" * 50)
    
    room_name = "test_room_audio_001"
    
    # Create mock audio file
    audio_file = create_mock_audio_file(100)  # 100KB mock file
    
    # Upload audio
    response = client.post(
        f"/api/v1/rooms/{room_name}/upload-audio",
        files={"audio": ("test_audio.mp3", audio_file, "audio/mpeg")}
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ PASS: Audio uploaded successfully")
        print(f"   - Filename: {data.get('filename')}")
        print(f"   - File Size: {data.get('fileSize')}")
        return True
    else:
        print(f"❌ FAIL: Upload failed")
        return False


def test_audio_retrieval():
    """Test audio retrieval endpoint."""
    print("\n🧪 TEST 2: Audio Retrieval")
    print("-" * 50)
    
    # First upload a file
    room_name = "test_room_audio_002"
    audio_file = create_mock_audio_file(50)
    
    upload_response = client.post(
        f"/api/v1/rooms/{room_name}/upload-audio",
        files={"audio": ("test_audio.mp3", audio_file, "audio/mpeg")}
    )
    
    if upload_response.status_code != 200:
        print("❌ FAIL: Could not upload test file")
        return False
    
    print("✅ Test file uploaded")
    
    # Try to retrieve the file
    response = client.get(f"/api/v1/rooms/{room_name}/audio")
    
    print(f"Status Code: {response.status_code}")
    print(f"Content Type: {response.headers.get('content-type')}")
    print(f"Content Length: {len(response.content)} bytes")
    
    if response.status_code == 200 and response.headers.get('content-type') == 'audio/mpeg':
        print(f"✅ PASS: Audio retrieved successfully")
        return True
    else:
        print(f"❌ FAIL: Retrieval failed")
        return False


def test_audio_not_found():
    """Test audio retrieval for non-existent room."""
    print("\n🧪 TEST 3: Audio Not Found")
    print("-" * 50)
    
    room_name = "nonexistent_room_12345"
    
    response = client.get(f"/api/v1/rooms/{room_name}/audio")
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 404:
        print(f"✅ PASS: Correctly returns 404 for non-existent audio")
        return True
    else:
        print(f"❌ FAIL: Should return 404")
        return False


def test_directory_structure():
    """Test that audio directory exists and has correct structure."""
    print("\n🧪 TEST 4: Directory Structure")
    print("-" * 50)
    
    backend_dir = Path(__file__).parent
    audio_dir = backend_dir / "recordings" / "audio"
    
    print(f"Checking: {audio_dir}")
    
    if audio_dir.exists() and audio_dir.is_dir():
        print(f"✅ PASS: Audio directory exists")
        
        # List files
        files = list(audio_dir.glob("*.mp3"))
        print(f"   - Found {len(files)} MP3 files")
        
        if files:
            for f in files[:5]:  # Show first 5
                size_mb = f.stat().st_size / (1024 * 1024)
                print(f"   - {f.name} ({size_mb:.2f}MB)")
        
        return True
    else:
        print(f"❌ FAIL: Audio directory does not exist")
        return False


def test_file_size_limits():
    """Test upload with large file."""
    print("\n🧪 TEST 5: Large File Upload")
    print("-" * 50)
    
    room_name = "test_room_large"
    
    # Create a 5MB mock file
    audio_file = create_mock_audio_file(5000)  # 5MB
    
    print("Uploading 5MB file...")
    response = client.post(
        f"/api/v1/rooms/{room_name}/upload-audio",
        files={"audio": ("large_audio.mp3", audio_file, "audio/mpeg")}
    )
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ PASS: Large file uploaded successfully")
        print(f"   - File Size: {data.get('fileSize')}")
        return True
    else:
        print(f"❌ FAIL: Large file upload failed")
        return False


def cleanup_test_files():
    """Clean up test files."""
    print("\n🧹 Cleaning up test files...")
    print("-" * 50)
    
    backend_dir = Path(__file__).parent
    audio_dir = backend_dir / "recordings" / "audio"
    
    if audio_dir.exists():
        test_files = list(audio_dir.glob("test_room_*.mp3"))
        
        for f in test_files:
            f.unlink()
            print(f"   Deleted: {f.name}")
        
        print(f"✅ Cleaned up {len(test_files)} test files")
    else:
        print("   No cleanup needed")


def run_all_tests():
    """Run all tests."""
    print("\n" + "=" * 50)
    print("🚀 AUDIO RECORDING TEST SUITE")
    print("=" * 50)
    
    tests = [
        ("Audio Upload", test_audio_upload),
        ("Audio Retrieval", test_audio_retrieval),
        ("Audio Not Found", test_audio_not_found),
        ("Directory Structure", test_directory_structure),
        ("Large File Upload", test_file_size_limits),
    ]
    
    results = []
    
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n❌ ERROR in {name}: {e}")
            import traceback
            traceback.print_exc()
            results.append((name, False))
    
    # Cleanup
    try:
        cleanup_test_files()
    except Exception as e:
        print(f"⚠️ Cleanup error: {e}")
    
    # Print summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {name}")
    
    print("-" * 50)
    print(f"Total: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED!")
        return 0
    else:
        print(f"\n⚠️ {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    exit_code = run_all_tests()
    sys.exit(exit_code)

