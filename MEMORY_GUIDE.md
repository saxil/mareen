# Mareen Memory System - Quick Reference

## What's New?
Your Mareen assistant now has **real memory**! Every conversation is automatically saved to a local database, so nothing is ever lost.

## Features

### 🔄 Automatic Memory
- Every message (yours and Mareen's) is logged automatically
- Each session (app launch to close) is tracked separately
- All data stored locally in `memory.db` - never leaves your computer

### 📊 What's Stored
For each conversation:
- Timestamp (when the message was sent)
- Speaker (USER or MAREEN)
- The actual message content
- Intent classification (if applicable)
- Response time (for Mareen's replies)

For each session:
- Unique session ID
- Start and end times
- Total message count
- Optional metadata

### 🔍 Viewing Your Memory

#### Quick Stats
```bash
python view_memory.py stats
```

#### List All Sessions
```bash
python view_memory.py sessions
```

#### View a Specific Session
```bash
python view_memory.py view <session_id>
```

#### Search All Conversations
```bash
python view_memory.py search "calculator"
```

#### Export Session to JSON
```bash
python view_memory.py export <session_id> my_conversation.json
```

#### Interactive Menu
```bash
python view_memory.py
```

## Technical Details

### Database Schema
- **Location**: `memory.db` (SQLite database in project root)
- **Tables**: 
  - `sessions` - Session metadata
  - `conversations` - Individual messages

### Memory Manager API
The memory system is available through `core.memory`:

```python
from core.memory import get_memory_manager

memory = get_memory_manager()

# Start a session
session_id = memory.start_session(metadata={"version": "3.1"})

# Log messages
memory.log_message("USER", "Hello!")
memory.log_message("MAREEN", "Hi there!", response_time=0.5)

# Retrieve history
history = memory.get_session_history()

# Search
results = memory.search_conversations("weather")

# Get statistics
stats = memory.get_statistics()

# End session
memory.end_session()
```

### Integration Points

The memory system is integrated at these points:

1. **Session Start**: When `main_loop()` starts in [main.py](src/main.py)
2. **User Messages**: When commands are processed in `process_command()`
3. **LLM Responses**: In `process_text()` in [llm.py](src/core/llm.py)
4. **System Commands**: When intent parser detects commands
5. **Session End**: When app exits or "stop" command is given

## Privacy & Security

✅ **Local Only**: All data stored on your machine  
✅ **No Cloud**: Never sent to external servers  
✅ **Full Control**: Delete `memory.db` anytime to clear history  
✅ **Transparent**: SQLite database - view with any SQLite browser  

## File Locations

```
mareen/
├── memory.db                   # SQLite database (auto-created)
├── view_memory.py              # Memory viewer utility
├── test_memory.py              # Test script
└── src/
    └── core/
        └── memory.py           # Memory management module
```

## Examples

### Example 1: View Today's Conversations
```bash
python view_memory.py sessions
# Copy the session_id you want
python view_memory.py view 20260210_180123_540602
```

### Example 2: Search for Specific Topics
```bash
python view_memory.py search "calculator"
python view_memory.py search "weather"
python view_memory.py search "namaste"
```

### Example 3: Backup Your Conversations
```bash
# Export latest session
python view_memory.py sessions  # Get session ID
python view_memory.py export <session_id> backup_2026_02_10.json

# Or backup the entire database
cp memory.db memory_backup.db
```

## Troubleshooting

**Q: Where is my conversation history?**  
A: Check `memory.db` in the project root. Run `python view_memory.py stats` to verify.

**Q: Can I delete old conversations?**  
A: Yes, you can delete `memory.db` or use SQLite tools to selectively remove data.

**Q: How much space does it use?**  
A: Minimal. Text is very efficient. Thousands of messages = a few MB.

**Q: Does this slow down the app?**  
A: No. Database operations are asynchronous and very fast.

## Advanced Usage

### Custom Queries
Open `memory.db` with any SQLite browser for custom queries:

```sql
-- Get all conversations from today
SELECT * FROM conversations 
WHERE date(timestamp) = date('now');

-- Count messages per session
SELECT session_id, COUNT(*) as msg_count 
FROM conversations 
GROUP BY session_id 
ORDER BY msg_count DESC;

-- Find longest sessions
SELECT session_id, total_messages, start_time, end_time 
FROM sessions 
WHERE total_messages > 0 
ORDER BY total_messages DESC 
LIMIT 10;
```

### Programmatic Access
```python
from core.memory import get_memory_manager
import sqlite3

# Direct database access
memory = get_memory_manager()
conn = sqlite3.connect(memory.db_path)
cursor = conn.cursor()

# Your custom queries here
cursor.execute("SELECT COUNT(*) FROM conversations")
print(f"Total messages: {cursor.fetchone()[0]}")

conn.close()
```

---

**Remember**: Your conversations are precious data. Back up `memory.db` regularly!
