"""
Memory Viewer Utility
Command-line tool to view and manage conversation memory.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from core.memory import get_memory_manager
from datetime import datetime
import json

def print_header(text):
    """Print a formatted header."""
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60)

def print_message(msg):
    """Print a formatted conversation message."""
    timestamp = datetime.fromisoformat(msg['timestamp']).strftime("%Y-%m-%d %H:%M:%S")
    speaker = msg['speaker'].ljust(10)
    message = msg['message'][:100] + "..." if len(msg['message']) > 100 else msg['message']
    print(f"[{timestamp}] {speaker}: {message}")
    if msg.get('response_time'):
        print(f"              Response Time: {msg['response_time']:.2f}s")

def show_statistics():
    """Display memory statistics."""
    memory = get_memory_manager()
    stats = memory.get_statistics()
    
    print_header("MEMORY STATISTICS")
    print(f"Total Sessions:        {stats['total_sessions']}")
    print(f"Total Messages:        {stats['total_messages']}")
    print(f"User Messages:         {stats['user_messages']}")
    print(f"Assistant Messages:    {stats['assistant_messages']}")
    print(f"Avg Session Length:    {stats['average_session_length']} messages")
    print(f"Database Location:     {stats['database_path']}")

def show_all_sessions():
    """Display all sessions."""
    memory = get_memory_manager()
    sessions = memory.get_all_sessions(limit=20)
    
    print_header("RECENT SESSIONS (Last 20)")
    if not sessions:
        print("No sessions found.")
        return
    
    for i, session in enumerate(sessions, 1):
        start = datetime.fromisoformat(session['start_time']).strftime("%Y-%m-%d %H:%M:%S")
        end = datetime.fromisoformat(session['end_time']).strftime("%H:%M:%S") if session['end_time'] else "In Progress"
        print(f"\n{i}. Session ID: {session['session_id']}")
        print(f"   Start Time: {start}")
        print(f"   End Time:   {end}")
        print(f"   Messages:   {session['total_messages']}")

def show_session_details(session_id):
    """Display details of a specific session."""
    memory = get_memory_manager()
    history = memory.get_session_history(session_id)
    
    if not history:
        print(f"No conversation history found for session: {session_id}")
        return
    
    print_header(f"SESSION: {session_id}")
    print(f"Total Messages: {len(history)}\n")
    
    for msg in history:
        print_message(msg)

def search_conversations(query):
    """Search through all conversations."""
    memory = get_memory_manager()
    results = memory.search_conversations(query, limit=50)
    
    print_header(f"SEARCH RESULTS FOR: '{query}'")
    if not results:
        print("No matching conversations found.")
        return
    
    print(f"Found {len(results)} matching messages:\n")
    
    for i, result in enumerate(results, 1):
        session_time = datetime.fromisoformat(result['session_start']).strftime("%Y-%m-%d")
        msg_time = datetime.fromisoformat(result['timestamp']).strftime("%H:%M:%S")
        print(f"\n{i}. [{session_time} {msg_time}] {result['speaker']}")
        print(f"   Session: {result['session_id']}")
        print(f"   Message: {result['message']}")

def export_session_to_json(session_id, output_file):
    """Export a session to JSON."""
    memory = get_memory_manager()
    memory.export_session(session_id, output_file)
    print(f"Session exported successfully to: {output_file}")

def show_menu():
    """Display interactive menu."""
    while True:
        print_header("MAREEN MEMORY VIEWER")
        print("1. Show Statistics")
        print("2. View All Sessions")
        print("3. View Session Details")
        print("4. Search Conversations")
        print("5. Export Session to JSON")
        print("6. Exit")
        print()
        
        choice = input("Enter your choice (1-6): ").strip()
        
        if choice == "1":
            show_statistics()
        
        elif choice == "2":
            show_all_sessions()
        
        elif choice == "3":
            session_id = input("Enter Session ID: ").strip()
            if session_id:
                show_session_details(session_id)
            else:
                print("Invalid session ID.")
        
        elif choice == "4":
            query = input("Enter search query: ").strip()
            if query:
                search_conversations(query)
            else:
                print("Please enter a search query.")
        
        elif choice == "5":
            session_id = input("Enter Session ID: ").strip()
            output_file = input("Enter output file path (e.g., session.json): ").strip()
            if session_id and output_file:
                export_session_to_json(session_id, output_file)
            else:
                print("Invalid input.")
        
        elif choice == "6":
            print("\nGoodbye!")
            break
        
        else:
            print("Invalid choice. Please enter 1-6.")
        
        input("\nPress Enter to continue...")

def main():
    """Main entry point."""
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "stats":
            show_statistics()
        
        elif command == "sessions":
            show_all_sessions()
        
        elif command == "view" and len(sys.argv) > 2:
            session_id = sys.argv[2]
            show_session_details(session_id)
        
        elif command == "search" and len(sys.argv) > 2:
            query = " ".join(sys.argv[2:])
            search_conversations(query)
        
        elif command == "export" and len(sys.argv) > 3:
            session_id = sys.argv[2]
            output_file = sys.argv[3]
            export_session_to_json(session_id, output_file)
        
        else:
            print("Usage:")
            print("  python view_memory.py                    # Interactive mode")
            print("  python view_memory.py stats              # Show statistics")
            print("  python view_memory.py sessions           # List all sessions")
            print("  python view_memory.py view <session_id>  # View session details")
            print("  python view_memory.py search <query>     # Search conversations")
            print("  python view_memory.py export <session_id> <output.json>  # Export session")
    
    else:
        # Interactive mode
        show_menu()

if __name__ == "__main__":
    main()
