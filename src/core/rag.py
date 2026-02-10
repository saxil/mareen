"""
RAG (Retrieval-Augmented Generation) System for Mareen
Uses conversation memory to provide contextual responses based on past interactions.
"""

import numpy as np
from typing import List, Dict, Optional, Tuple
import json
import pickle
import os
from datetime import datetime, timedelta

# Try to import sentence transformers, fallback to basic similarity
try:
    from sentence_transformers import SentenceTransformer
    EMBEDDINGS_AVAILABLE = True
except ImportError:
    EMBEDDINGS_AVAILABLE = False
    print("Warning: sentence-transformers not available. Using basic keyword matching.")

from core.memory import get_memory_manager

# Cache file for embeddings
EMBEDDINGS_CACHE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'embeddings_cache.pkl')

class RAG:
    """Retrieval-Augmented Generation system for contextual responses."""
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize RAG system.
        
        Args:
            model_name: Sentence transformer model name (small and fast by default)
        """
        self.memory = get_memory_manager()
        self.embeddings_cache = {}
        self.model = None
        
        if EMBEDDINGS_AVAILABLE:
            try:
                print(f"Loading sentence transformer model: {model_name}")
                self.model = SentenceTransformer(model_name)
                print("✓ RAG system initialized with embeddings")
            except Exception as e:
                print(f"Failed to load sentence transformer: {e}")
                self.model = None
        
        # Load cached embeddings
        self._load_cache()
    
    def _load_cache(self):
        """Load embeddings cache from disk."""
        if os.path.exists(EMBEDDINGS_CACHE):
            try:
                with open(EMBEDDINGS_CACHE, 'rb') as f:
                    self.embeddings_cache = pickle.load(f)
                print(f"✓ Loaded {len(self.embeddings_cache)} cached embeddings")
            except Exception as e:
                print(f"Warning: Could not load embeddings cache: {e}")
                self.embeddings_cache = {}
    
    def _save_cache(self):
        """Save embeddings cache to disk."""
        try:
            with open(EMBEDDINGS_CACHE, 'wb') as f:
                pickle.dump(self.embeddings_cache, f)
        except Exception as e:
            print(f"Warning: Could not save embeddings cache: {e}")
    
    def _get_embedding(self, text: str) -> Optional[np.ndarray]:
        """
        Get embedding for text, using cache if available.
        
        Args:
            text: Text to embed
            
        Returns:
            Numpy array of embedding or None
        """
        if not self.model:
            return None
        
        # Check cache
        if text in self.embeddings_cache:
            return self.embeddings_cache[text]
        
        # Generate new embedding
        try:
            embedding = self.model.encode(text, convert_to_numpy=True)
            self.embeddings_cache[text] = embedding
            
            # Save cache periodically (every 10 new embeddings)
            if len(self.embeddings_cache) % 10 == 0:
                self._save_cache()
            
            return embedding
        except Exception as e:
            print(f"Error generating embedding: {e}")
            return None
    
    def _cosine_similarity(self, a: np.ndarray, b: np.ndarray) -> float:
        """Calculate cosine similarity between two vectors."""
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
    
    def _keyword_similarity(self, query: str, text: str) -> float:
        """
        Fallback keyword-based similarity when embeddings not available.
        
        Args:
            query: Query text
            text: Text to compare against
            
        Returns:
            Similarity score (0-1)
        """
        query_lower = query.lower()
        text_lower = text.lower()
        
        # Split into words
        query_words = set(query_lower.split())
        text_words = set(text_lower.split())
        
        if not query_words or not text_words:
            return 0.0
        
        # Calculate Jaccard similarity
        intersection = query_words.intersection(text_words)
        union = query_words.union(text_words)
        
        return len(intersection) / len(union) if union else 0.0
    
    def retrieve_context(self, query: str, top_k: int = 5, 
                        time_decay: bool = True,
                        min_similarity: float = 0.3) -> List[Dict]:
        """
        Retrieve relevant conversation context for a query.
        
        Args:
            query: User's current query
            top_k: Number of relevant memories to retrieve
            time_decay: Apply time-based decay to scores (recent = higher)
            min_similarity: Minimum similarity threshold
            
        Returns:
            List of relevant conversation entries with scores
        """
        # Get all conversations from memory
        all_conversations = self._get_all_conversations()
        
        if not all_conversations:
            return []
        
        # Get query embedding
        query_embedding = self._get_embedding(query)
        
        # Score each conversation
        scored_conversations = []
        
        for conv in all_conversations:
            message = conv['message']
            
            # Calculate similarity
            if query_embedding is not None:
                # Use semantic similarity
                msg_embedding = self._get_embedding(message)
                if msg_embedding is not None:
                    similarity = self._cosine_similarity(query_embedding, msg_embedding)
                else:
                    similarity = self._keyword_similarity(query, message)
            else:
                # Use keyword similarity
                similarity = self._keyword_similarity(query, message)
            
            # Apply time decay if enabled
            if time_decay:
                time_score = self._calculate_time_decay(conv['timestamp'])
                final_score = similarity * 0.7 + time_score * 0.3
            else:
                final_score = similarity
            
            # Only include if above threshold
            if final_score >= min_similarity:
                scored_conversations.append({
                    **conv,
                    'similarity_score': similarity,
                    'final_score': final_score
                })
        
        # Sort by final score
        scored_conversations.sort(key=lambda x: x['final_score'], reverse=True)
        
        # Return top_k results
        return scored_conversations[:top_k]
    
    def _get_all_conversations(self, max_age_days: int = 30) -> List[Dict]:
        """
        Get all conversations from memory within a time window.
        
        Args:
            max_age_days: Only retrieve conversations from last N days
            
        Returns:
            List of conversation dictionaries
        """
        # Get all sessions (recent first)
        sessions = self.memory.get_all_sessions(limit=50)
        
        conversations = []
        cutoff_date = datetime.now() - timedelta(days=max_age_days)
        
        for session in sessions:
            # Check if session is within time window
            session_start = datetime.fromisoformat(session['start_time'])
            if session_start < cutoff_date:
                continue
            
            # Get conversations from this session
            session_history = self.memory.get_session_history(session['session_id'])
            
            for conv in session_history:
                conversations.append({
                    'session_id': session['session_id'],
                    'timestamp': conv['timestamp'],
                    'speaker': conv['speaker'],
                    'message': conv['message'],
                    'intent': conv.get('intent'),
                })
        
        return conversations
    
    def _calculate_time_decay(self, timestamp: str) -> float:
        """
        Calculate time decay score (recent = higher score).
        
        Args:
            timestamp: ISO format timestamp
            
        Returns:
            Score between 0 and 1
        """
        try:
            msg_time = datetime.fromisoformat(timestamp)
            now = datetime.now()
            
            # Calculate hours difference
            hours_diff = (now - msg_time).total_seconds() / 3600
            
            # Exponential decay: score = e^(-hours/24)
            # Recent messages (< 1 day) get high scores
            # Older messages decay exponentially
            decay_score = np.exp(-hours_diff / 24)
            
            return max(0.0, min(1.0, decay_score))
        except:
            return 0.5  # Default middle score if parsing fails
    
    def build_context_prompt(self, query: str, top_k: int = 3) -> str:
        """
        Build a context-aware prompt by retrieving relevant memories.
        
        Args:
            query: User's current query
            top_k: Number of memories to include
            
        Returns:
            Formatted context string to prepend to conversation
        """
        relevant_memories = self.retrieve_context(query, top_k=top_k)
        
        if not relevant_memories:
            return ""
        
        # Build context string
        context_parts = ["[Relevant past interactions for context:]"]
        
        for i, memory in enumerate(relevant_memories, 1):
            timestamp = datetime.fromisoformat(memory['timestamp']).strftime("%Y-%m-%d")
            speaker = memory['speaker']
            message = memory['message'][:150] + "..." if len(memory['message']) > 150 else memory['message']
            
            context_parts.append(f"{i}. [{timestamp}] {speaker}: {message}")
        
        context_parts.append("[End of context. Respond to current query below:]")
        
        return "\n".join(context_parts)
    
    def get_conversation_summary(self, session_id: Optional[str] = None) -> str:
        """
        Get a summary of a conversation session.
        
        Args:
            session_id: Session to summarize (current if None)
            
        Returns:
            Summary string
        """
        history = self.memory.get_session_history(session_id)
        
        if not history:
            return "No conversation history."
        
        user_messages = [h for h in history if h['speaker'] == 'USER']
        assistant_messages = [h for h in history if h['speaker'] == 'MAREEN']
        
        summary = f"Conversation summary:\n"
        summary += f"- Total exchanges: {min(len(user_messages), len(assistant_messages))}\n"
        summary += f"- Topics discussed: "
        
        # Extract key topics (simple keyword extraction)
        all_text = " ".join([h['message'] for h in history])
        # This is a simple approach - could be enhanced with RAKE or similar
        
        return summary
    
    def find_similar_past_queries(self, query: str, top_k: int = 3) -> List[Dict]:
        """
        Find similar questions asked in the past.
        
        Args:
            query: Current user query
            top_k: Number of similar queries to find
            
        Returns:
            List of similar past queries with responses
        """
        # Get only USER messages
        all_conversations = self._get_all_conversations()
        user_queries = [c for c in all_conversations if c['speaker'] == 'USER']
        
        if not user_queries:
            return []
        
        query_embedding = self._get_embedding(query)
        scored_queries = []
        
        for user_query in user_queries:
            message = user_query['message']
            
            # Calculate similarity
            if query_embedding is not None:
                msg_embedding = self._get_embedding(message)
                if msg_embedding is not None:
                    similarity = self._cosine_similarity(query_embedding, msg_embedding)
                else:
                    similarity = self._keyword_similarity(query, message)
            else:
                similarity = self._keyword_similarity(query, message)
            
            if similarity > 0.4:  # Higher threshold for similar queries
                scored_queries.append({
                    **user_query,
                    'similarity': similarity
                })
        
        scored_queries.sort(key=lambda x: x['similarity'], reverse=True)
        return scored_queries[:top_k]
    
    def clear_embeddings_cache(self):
        """Clear the embeddings cache (useful if model changes)."""
        self.embeddings_cache = {}
        if os.path.exists(EMBEDDINGS_CACHE):
            os.remove(EMBEDDINGS_CACHE)
        print("✓ Embeddings cache cleared")
    
    def get_stats(self) -> Dict:
        """Get RAG system statistics."""
        return {
            'embeddings_available': EMBEDDINGS_AVAILABLE,
            'model_loaded': self.model is not None,
            'cached_embeddings': len(self.embeddings_cache),
            'total_conversations': len(self._get_all_conversations()),
            'cache_file': EMBEDDINGS_CACHE
        }

# Global RAG instance
_rag_instance = None

def get_rag() -> RAG:
    """Get the global RAG instance (singleton pattern)."""
    global _rag_instance
    if _rag_instance is None:
        _rag_instance = RAG()
    return _rag_instance

def enable_rag_context(enabled: bool = True):
    """Enable or disable RAG context injection globally."""
    global _rag_enabled
    _rag_enabled = enabled

# Flag to enable/disable RAG
_rag_enabled = True

def is_rag_enabled() -> bool:
    """Check if RAG is currently enabled."""
    return _rag_enabled
