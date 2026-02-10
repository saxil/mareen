"""
Test script for Memory System
Demonstrates the memory functionality without running the full application.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from core.memory import get_memory_manager
from datetime import datetime
import time

def test_memory_system():
    """Test the memory system functionality."""
    print("="*60)
    print("  MEMORY SYSTEM TEST")
    print("="*60)
    
    memory = get_memory_manager()
    
    # Test 1: Start a session
    print("\n[TEST 1] Starting a new session...")
    session_id = memory.start_session(metadata={
        "test": True,
        "version": "3.1"
    })
    print(f"✓ Session started: {session_id}")
    
    # Test 2: Log some messages
    print("\n[TEST 2] Logging messages...")
    memory.log_message("USER", "Hello, Mareen!")
    time.sleep(0.1)
    memory.log_message("MAREEN", "Namaste! How can I help you today?", response_time=0.5)
    time.sleep(0.1)
    memory.log_message("USER", "What is the weather like?")
    time.sleep(0.1)
    memory.log_message("MAREEN", "I apologize but I don't have access to real-time weather data.", response_time=0.8)
    time.sleep(0.1)
    memory.log_message("USER", "Open calculator", intent="system_command")
    time.sleep(0.1)
    memory.log_message("MAREEN", "Executed: calculator", intent="system_response", response_time=0.2)
    print(f"✓ Logged 6 messages")
    
    # Test 3: Get session history
    print("\n[TEST 3] Retrieving session history...")
    history = memory.get_session_history()
    print(f"✓ Retrieved {len(history)} messages")
    for i, msg in enumerate(history, 1):
        timestamp = datetime.fromisoformat(msg['timestamp']).strftime("%H:%M:%S")
        print(f"   {i}. [{timestamp}] {msg['speaker']}: {msg['message'][:50]}...")
    
    # Test 4: Search conversations
    print("\n[TEST 4] Searching for 'weather'...")
    results = memory.search_conversations("weather")
    print(f"✓ Found {len(results)} matching messages")
    for result in results:
        print(f"   - {result['speaker']}: {result['message'][:50]}...")
    
    # Test 5: Get statistics
    print("\n[TEST 5] Getting statistics...")
    stats = memory.get_statistics()
    print(f"✓ Statistics:")
    print(f"   Total Sessions: {stats['total_sessions']}")
    print(f"   Total Messages: {stats['total_messages']}")
    print(f"   User Messages: {stats['user_messages']}")
    print(f"   Assistant Messages: {stats['assistant_messages']}")
    print(f"   Average Session Length: {stats['average_session_length']}")
    
    # Test 6: Export session
    print("\n[TEST 6] Exporting session to JSON...")
    export_file = f"test_session_{session_id}.json"
    memory.export_session(session_id, export_file)
    print(f"✓ Exported to: {export_file}")
    
    # Test 7: End session
    print("\n[TEST 7] Ending session...")
    memory.end_session()
    print(f"✓ Session ended")
    
    # Test 8: Verify session was saved
    print("\n[TEST 8] Verifying session was saved...")
    all_sessions = memory.get_all_sessions(limit=5)
    print(f"✓ Total sessions in database: {len(all_sessions)}")
    if all_sessions:
        latest = all_sessions[0]
        print(f"   Latest Session ID: {latest['session_id']}")
        print(f"   Start Time: {latest['start_time']}")
        print(f"   End Time: {latest['end_time']}")
        print(f"   Total Messages: {latest['total_messages']}")
    
    print("\n" + "="*60)
    print("  ALL TESTS COMPLETED SUCCESSFULLY!")
    print("="*60)
    print(f"\nDatabase location: {memory.db_path}")
    print(f"Export file: {os.path.abspath(export_file)}")
    print("\nYou can now:")
    print("  1. Run 'python view_memory.py' to view all conversations")
    print("  2. Check the exported JSON file")
    print("  3. Start the main application and see memory in action")

if __name__ == "__main__":
    test_memory_system()
