"""
Memory Management System for Mareen
Logs all conversations and sessions to a SQLite database for persistent memory.
"""

import sqlite3
import os
import json
from datetime import datetime
from typing import List, Dict, Optional, Tuple

# Database file location
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'memory.db')

class MemoryManager:
    def __init__(self):
        """Initialize the memory manager and create database if it doesn't exist."""
        self.db_path = DB_PATH
        self.current_session_id = None
        self._init_database()
    
    def _init_database(self):
        """Create the database schema if it doesn't exist."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create sessions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY,
                start_time TEXT NOT NULL,
                end_time TEXT,
                total_messages INTEGER DEFAULT 0,
                metadata TEXT
            )
        ''')
        
        # Create conversations table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                speaker TEXT NOT NULL,
                message TEXT NOT NULL,
                intent TEXT,
                response_time REAL,
                FOREIGN KEY (session_id) REFERENCES sessions(session_id)
            )
        ''')
        
        # Create index for faster queries
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_session_id 
            ON conversations(session_id)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_timestamp 
            ON conversations(timestamp)
        ''')
        
        conn.commit()
        conn.close()
        print(f"Memory database initialized at: {self.db_path}")
    
    def start_session(self, metadata: Optional[Dict] = None) -> str:
        """
        Start a new conversation session.
        
        Args:
            metadata: Optional dictionary with session metadata
            
        Returns:
            session_id: Unique identifier for the session
        """
        session_id = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        start_time = datetime.now().isoformat()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO sessions (session_id, start_time, metadata)
            VALUES (?, ?, ?)
        ''', (session_id, start_time, json.dumps(metadata) if metadata else None))
        
        conn.commit()
        conn.close()
        
        self.current_session_id = session_id
        print(f"Started new session: {session_id}")
        return session_id
    
    def end_session(self):
        """End the current session."""
        if not self.current_session_id:
            print("No active session to end.")
            return
        
        end_time = datetime.now().isoformat()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Update session end time
        cursor.execute('''
            UPDATE sessions 
            SET end_time = ?
            WHERE session_id = ?
        ''', (end_time, self.current_session_id))
        
        # Update total messages count
        cursor.execute('''
            UPDATE sessions 
            SET total_messages = (
                SELECT COUNT(*) 
                FROM conversations 
                WHERE session_id = ?
            )
            WHERE session_id = ?
        ''', (self.current_session_id, self.current_session_id))
        
        conn.commit()
        conn.close()
        
        print(f"Ended session: {self.current_session_id}")
        self.current_session_id = None
    
    def log_message(self, speaker: str, message: str, intent: Optional[str] = None, 
                    response_time: Optional[float] = None):
        """
        Log a message to the current session.
        
        Args:
            speaker: "USER" or "MAREEN"
            message: The actual message text
            intent: Optional intent classification
            response_time: Optional response time in seconds
        """
        if not self.current_session_id:
            print("Warning: No active session. Starting a new one.")
            self.start_session()
        
        timestamp = datetime.now().isoformat()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO conversations 
            (session_id, timestamp, speaker, message, intent, response_time)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (self.current_session_id, timestamp, speaker, message, intent, response_time))
        
        conn.commit()
        conn.close()
    
    def get_session_history(self, session_id: Optional[str] = None, 
                           limit: Optional[int] = None) -> List[Dict]:
        """
        Retrieve conversation history for a specific session.
        
        Args:
            session_id: Session ID to retrieve (uses current session if None)
            limit: Maximum number of messages to retrieve
            
        Returns:
            List of conversation messages
        """
        if session_id is None:
            session_id = self.current_session_id
        
        if not session_id:
            return []
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = '''
            SELECT timestamp, speaker, message, intent, response_time
            FROM conversations
            WHERE session_id = ?
            ORDER BY timestamp ASC
        '''
        
        if limit:
            query += f' LIMIT {limit}'
        
        cursor.execute(query, (session_id,))
        rows = cursor.fetchall()
        conn.close()
        
        history = []
        for row in rows:
            history.append({
                'timestamp': row[0],
                'speaker': row[1],
                'message': row[2],
                'intent': row[3],
                'response_time': row[4]
            })
        
        return history
    
    def get_all_sessions(self, limit: Optional[int] = None) -> List[Dict]:
        """
        Retrieve all sessions.
        
        Args:
            limit: Maximum number of sessions to retrieve
            
        Returns:
            List of session information
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = '''
            SELECT session_id, start_time, end_time, total_messages, metadata
            FROM sessions
            ORDER BY start_time DESC
        '''
        
        if limit:
            query += f' LIMIT {limit}'
        
        cursor.execute(query)
        rows = cursor.fetchall()
        conn.close()
        
        sessions = []
        for row in rows:
            sessions.append({
                'session_id': row[0],
                'start_time': row[1],
                'end_time': row[2],
                'total_messages': row[3],
                'metadata': json.loads(row[4]) if row[4] else None
            })
        
        return sessions
    
    def search_conversations(self, query: str, limit: int = 50) -> List[Dict]:
        """
        Search through all conversations for a specific text.
        
        Args:
            query: Text to search for
            limit: Maximum number of results
            
        Returns:
            List of matching conversation messages with context
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT c.session_id, c.timestamp, c.speaker, c.message, s.start_time
            FROM conversations c
            JOIN sessions s ON c.session_id = s.session_id
            WHERE c.message LIKE ?
            ORDER BY c.timestamp DESC
            LIMIT ?
        ''', (f'%{query}%', limit))
        
        rows = cursor.fetchall()
        conn.close()
        
        results = []
        for row in rows:
            results.append({
                'session_id': row[0],
                'timestamp': row[1],
                'speaker': row[2],
                'message': row[3],
                'session_start': row[4]
            })
        
        return results
    
    def get_recent_context(self, num_messages: int = 10) -> List[Dict]:
        """
        Get recent conversation context from current session.
        
        Args:
            num_messages: Number of recent messages to retrieve
            
        Returns:
            List of recent messages
        """
        if not self.current_session_id:
            return []
        
        return self.get_session_history(limit=num_messages)
    
    def get_statistics(self) -> Dict:
        """
        Get memory statistics.
        
        Returns:
            Dictionary with various statistics
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Total sessions
        cursor.execute('SELECT COUNT(*) FROM sessions')
        total_sessions = cursor.fetchone()[0]
        
        # Total messages
        cursor.execute('SELECT COUNT(*) FROM conversations')
        total_messages = cursor.fetchone()[0]
        
        # User messages
        cursor.execute('SELECT COUNT(*) FROM conversations WHERE speaker = "USER"')
        user_messages = cursor.fetchone()[0]
        
        # Assistant messages
        cursor.execute('SELECT COUNT(*) FROM conversations WHERE speaker = "MAREEN"')
        assistant_messages = cursor.fetchone()[0]
        
        # Average session length
        cursor.execute('''
            SELECT AVG(total_messages) 
            FROM sessions 
            WHERE total_messages > 0
        ''')
        avg_session_length = cursor.fetchone()[0] or 0
        
        conn.close()
        
        return {
            'total_sessions': total_sessions,
            'total_messages': total_messages,
            'user_messages': user_messages,
            'assistant_messages': assistant_messages,
            'average_session_length': round(avg_session_length, 2),
            'database_path': self.db_path
        }
    
    def export_session(self, session_id: str, output_file: str):
        """
        Export a session to a JSON file.
        
        Args:
            session_id: Session to export
            output_file: Path to output JSON file
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get session info
        cursor.execute('''
            SELECT session_id, start_time, end_time, total_messages, metadata
            FROM sessions
            WHERE session_id = ?
        ''', (session_id,))
        
        session_row = cursor.fetchone()
        if not session_row:
            print(f"Session {session_id} not found.")
            return
        
        session_data = {
            'session_id': session_row[0],
            'start_time': session_row[1],
            'end_time': session_row[2],
            'total_messages': session_row[3],
            'metadata': json.loads(session_row[4]) if session_row[4] else None,
            'conversations': []
        }
        
        # Get conversations
        cursor.execute('''
            SELECT timestamp, speaker, message, intent, response_time
            FROM conversations
            WHERE session_id = ?
            ORDER BY timestamp ASC
        ''', (session_id,))
        
        for row in cursor.fetchall():
            session_data['conversations'].append({
                'timestamp': row[0],
                'speaker': row[1],
                'message': row[2],
                'intent': row[3],
                'response_time': row[4]
            })
        
        conn.close()
        
        # Write to file
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(session_data, f, indent=2, ensure_ascii=False)
        
        print(f"Session exported to: {output_file}")

# Global memory manager instance
_memory_manager = None

def get_memory_manager() -> MemoryManager:
    """Get the global memory manager instance (singleton pattern)."""
    global _memory_manager
    if _memory_manager is None:
        _memory_manager = MemoryManager()
    return _memory_manager
