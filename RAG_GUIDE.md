# RAG System Guide - Retrieval-Augmented Generation

## Overview

The **RAG (Retrieval-Augmented Generation)** system gives Mareen the ability to remember and use past conversations to provide contextual, personalized responses. Instead of treating each query in isolation, Mareen can now refer to your conversation history to give more relevant answers.

## What is RAG?

RAG is a technique that enhances AI responses by:
1. **Retrieving** relevant information from a knowledge base (your memory)
2. **Augmenting** the LLM prompt with this context
3. **Generating** responses that are informed by past interactions

## How It Works

### Traditional Conversation
```
User: "How do I learn Python?"
Mareen: "Python सीखने के लिए practice important है।"

User (later): "What resources did you recommend?"
Mareen: "मुझे याद नहीं है।" ❌
```

### With RAG
```
User: "How do I learn Python?"
Mareen: "Python सीखने के लिए practice important है।"
[Saved to memory]

User (later): "What resources did you recommend?"
[RAG retrieves: "How do I learn Python?" conversation]
Mareen: "Maine Python के लिए practice suggest की थी।" ✅
```

## Architecture

```
┌─────────────────┐
│   User Query    │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────┐
│  RAG Context Retrieval      │
│  1. Generate query embedding│
│  2. Search memory database  │
│  3. Rank by similarity      │
│  4. Apply time decay        │
└────────┬────────────────────┘
         │
         ▼
┌─────────────────────────────┐
│  Top 3 Relevant Memories    │
│  - Past conversation 1      │
│  - Past conversation 2      │
│  - Past conversation 3      │
└────────┬────────────────────┘
         │
         ▼
┌─────────────────────────────┐
│  Context-Augmented Prompt   │
│  [Context from memory]      │
│  [Current query]            │
└────────┬────────────────────┘
         │
         ▼
┌─────────────────────────────┐
│    LLM (Ollama)             │
│    Generates response       │
│    aware of context         │
└────────┬────────────────────┘
         │
         ▼
┌─────────────────────────────┐
│  Contextual Response        │
└─────────────────────────────┘
```

## Features

### 1. Semantic Search

**With sentence-transformers** (recommended):
- Uses AI embeddings to understand meaning
- Finds conceptually similar conversations
- Example: "weather" matches "rain forecast" and "temperature"

**Without embeddings** (fallback):
- Uses keyword matching (Jaccard similarity)
- Still effective for exact word matches
- Example: "weather" matches "weather" but not "rain"

### 2. Time Decay

Recent conversations are weighted higher:
```python
Score = (Similarity × 0.7) + (Recency × 0.3)
```

- Today's conversation: High recency score
- Last week's conversation: Medium recency score  
- Last month's conversation: Low recency score

This ensures Mareen remembers recent context better.

### 3. Smart Context Selection

Only top 3 most relevant memories are included:
- Prevents overwhelming the LLM with too much context
- Focuses on quality over quantity
- Keeps token usage efficient

### 4. Embedding Cache

Embeddings are cached to disk:
- First query: Generate embedding (slow)
- Subsequent queries: Load from cache (fast)
- Automatic cache management
- Saved in `embeddings_cache.pkl`

## Usage

### Automatic Operation

RAG works automatically - no user action needed:
```python
# When you use Mareen normally
User: "Tell me about Python"
# RAG automatically retrieves relevant past conversations
# and injects them as context
```

### Testing RAG

```bash
# Run comprehensive tests
python test_rag.py
```

Expected output:
```
✓ RAG Initialization
✓ Context Retrieval  
✓ Semantic vs Keyword
✓ Context Prompt Building
✓ Similar Query Detection
✓ RAG Statistics
✓ Time Decay Scoring

Total: 7 passed, 0 failed
```

### Checking RAG Status

```python
from core.llm import get_rag_stats

stats = get_rag_stats()
print(stats)
```

Output:
```python
{
    'embeddings_available': True,  # sentence-transformers installed
    'model_loaded': True,          # Model is ready
    'cached_embeddings': 145,      # 145 phrases cached
    'total_conversations': 892,    # 892 messages in memory
    'cache_file': 'A:/mareen/embeddings_cache.pkl'
}
```

### Enable/Disable RAG

```python
from core.llm import toggle_rag

# Disable RAG temporarily
toggle_rag(False)

# Re-enable RAG
toggle_rag(True)
```

## Configuration

### Adjusting Context Amount

Edit [src/core/llm.py](src/core/llm.py):

```python
# Change top_k to retrieve more/fewer memories
context_prompt = rag.build_context_prompt(text, top_k=5)  # Default: 3
```

### Changing Similarity Threshold

Edit [src/core/rag.py](src/core/rag.py):

```python
def retrieve_context(self, query: str, top_k: int = 5,
                     min_similarity: float = 0.2):  # Default: 0.3
```

Lower = more permissive (more results)  
Higher = more strict (fewer, better results)

### Adjusting Time Decay

Edit the weight distribution:

```python
# In _calculate_time_decay or retrieve_context
final_score = similarity * 0.8 + time_score * 0.2  # More weight to similarity
# OR
final_score = similarity * 0.5 + time_score * 0.5  # Equal weight
```

### Changing Memory Time Window

```python
# In _get_all_conversations
conversations = self._get_all_conversations(max_age_days=60)  # Default: 30
```

Retrieve from last 60 days instead of 30.

## API Reference

### RAG Class

```python
from core.rag import get_rag

rag = get_rag()  # Get singleton instance
```

#### Methods

**retrieve_context(query, top_k=5, time_decay=True, min_similarity=0.3)**
- Retrieve relevant conversation context
- Returns: List of scored conversation entries

**build_context_prompt(query, top_k=3)**
- Build formatted context for LLM
- Returns: String to prepend to prompt

**find_similar_past_queries(query, top_k=3)**
- Find similar questions from the past
- Returns: List of similar queries with responses

**get_stats()**
- Get RAG system statistics
- Returns: Dictionary with metrics

**clear_embeddings_cache()**
- Clear the embeddings cache
- Useful if changing models

### Integration with LLM

Located in [src/core/llm.py](src/core/llm.py):

```python
def process_text(text):
    # ... soul protection ...
    
    # RAG retrieval
    if RAG_AVAILABLE and is_rag_enabled():
        rag = get_rag()
        context_prompt = rag.build_context_prompt(text, top_k=3)
        user_message = f"{context_prompt}\n\nCurrent query: {text}"
    else:
        user_message = text
    
    # ... send to LLM ...
```

## Installation

### Basic (Keyword Matching)

Already included! No additional installation.
```bash
# RAG works out of the box with keyword matching
python test_rag.py
```

### Advanced (Semantic Embeddings)

For better context matching:
```bash
# Install sentence-transformers
pip install sentence-transformers

# Restart Mareen
python src/main.py
```

First run will download the model (~80MB):
- Model: `all-MiniLM-L6-v2`
- Size: Small and fast
- Quality: Good for most use cases

## Performance

### Speed

| Operation | Time (Keyword) | Time (Semantic) |
|-----------|----------------|-----------------|
| First query | ~1ms | ~100ms (download model) |
| Cached query | ~1ms | ~5ms |
| Search 100 msgs | ~10ms | ~50ms |
| Search 1000 msgs | ~100ms | ~200ms |

### Memory Usage

| Component | Size |
|-----------|------|
| RAG module | ~1MB |
| Embedding model | ~80MB (one-time download) |
| Cache (100 phrases) | ~50KB |
| Cache (1000 phrases) | ~500KB |

### Accuracy

| Method | Exact Match | Semantic Match |
|--------|-------------|----------------|
| Keyword | ⭐⭐⭐⭐⭐ | ⭐⭐ |
| Semantic | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |

**Example:**
- Query: "How to code in Python?"
- Keyword: Matches "code" and "Python"
- Semantic: Also matches "programming" and "learn coding"

## Examples

### Example 1: Learning Continuity

```
Session 1:
User: "I want to learn Python"
Mareen: "Python सीखने के लिए practice important है।"

Session 2 (next day):
User: "What programming language should I start with?"
[RAG retrieves previous Python conversation]
Mareen: "आप Python सीखना चाहते थे। वो एक अच्छा choice है beginners के लिए।"
```

### Example 2: Preference Recall

```
Session 1:
User: "I prefer Hindi responses"
Mareen: "जी बिल्कुल! मैं Hindi में ही बात करूँगी।"

Session 2:
User: "Tell me a joke"
[RAG sees preference for Hindi]
Mareen: "ज़रूर! एक बार एक programmer..."
```

### Example 3: Context Awareness

```
Session 1:
User: "Open calculator"
Mareen: "Calculator खोल रही हूँ।"

User: "Do that again"
[RAG retrieves "Open calculator" context]
Mareen: "Calculator फिर से खोल रही हूँ।"
```

## Troubleshooting

### RAG Not Finding Relevant Context

**Symptom**: Mareen doesn't remember past conversations

**Solutions**:
1. Check if RAG is enabled: `toggle_rag(True)`
2. Lower similarity threshold in `retrieve_context()`
3. Check memory has conversations: `python view_memory.py stats`
4. Install sentence-transformers for better matching

### Slow Response Times

**Symptom**: Queries take long to process

**Solutions**:
1. Embeddings are being generated - wait for cache to build
2. Reduce `top_k` to retrieve fewer memories
3. Reduce `max_age_days` to search less history
4. Clear and rebuild cache: `rag.clear_embeddings_cache()`

### Wrong Context Retrieved

**Symptom**: Irrelevant memories included

**Solutions**:
1. Increase `min_similarity` threshold
2. Check time decay settings
3. Install sentence-transformers for semantic matching
4. Review memory logs: `python view_memory.py view <session>`

### Model Download Fails

**Symptom**: Can't download sentence-transformers model

**Solutions**:
1. Check internet connection
2. Use keyword matching (automatic fallback)
3. Manually download model and place in cache
4. Set custom model path in code

## Best Practices

### For Users

1. **Have conversations** - More history = better context
2. **Be specific** - Clear queries get better matches
3. **Review memory** - Use `view_memory.py` to see what's remembered
4. **Clear old data** - Delete very old sessions if not needed

### For Developers

1. **Monitor cache size** - Clear periodically if too large
2. **Tune thresholds** - Adjust based on your use case
3. **Test changes** - Run `test_rag.py` after modifications
4. **Profile performance** - Monitor query times
5. **Backup cache** - Save `embeddings_cache.pkl` before big changes

## Advanced Features

### Custom Embeddings Model

```python
# In src/core/rag.py
rag = RAG(model_name="paraphrase-multilingual-MiniLM-L12-v2")
```

Better for Hindi/multilingual support but larger.

### Hybrid Search

Combine semantic and keyword:
```python
# Already implemented in retrieve_context
# Semantic similarity for broad matching
# + Time decay for recency
# = Best results
```

### Query Expansion

Add synonyms before search:
```python
# Expand query
if "weather" in query:
    query += " rain temperature forecast"
```

## Integration with Memory System

RAG builds on the memory system:

```
Memory System (storage)
    ↓
RAG System (retrieval)
    ↓
LLM System (generation)
```

All conversations logged by memory are available to RAG.

## Privacy & Security

### Data Location

- Embeddings cache: `embeddings_cache.pkl` (local)
- Conversation data: `memory.db` (local)
- Model files: `~/.cache/torch/sentence_transformers/` (local)

### Privacy Features

✓ All processing local (no cloud)  
✓ Embeddings generated on-device  
✓ No external API calls  
✓ Cache can be deleted anytime  

### Security Considerations

- RAG can expose past conversations in context
- Sensitive data in memory may appear in responses
- Clear memory regularly if needed
- Embeddings are not encrypted

## Future Enhancements

- [ ] Multi-modal RAG (images, audio)
- [ ] Conversation summarization
- [ ] Automatic topic clustering
- [ ] User-specific context profiles
- [ ] Temporal reasoning (know what happened when)
- [ ] Cross-session conversation threads
- [ ] Importance weighting (flag key conversations)
- [ ] Feedback loop (learn what context helps)

## Conclusion

RAG transforms Mareen from a stateless chatbot into a contextual assistant that remembers your conversations and provides personalized responses.

**Key Benefits:**
- 🧠 Better context awareness
- 💬 More natural conversations
- 📚 Learns from past interactions
- 🎯 Personalized responses
- 🔒 Fully private and local

---

**Questions?**
- Run `python test_rag.py` to see RAG in action
- Check [MEMORY_GUIDE.md](MEMORY_GUIDE.md) for memory system details
- Review [README.md](README.md) for general information
