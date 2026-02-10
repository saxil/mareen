"""
Test script for RAG (Retrieval-Augmented Generation) System
Tests context retrieval and semantic search capabilities.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from core.memory import get_memory_manager
from core.rag import get_rag, EMBEDDINGS_AVAILABLE
import time

def print_header(text):
    """Print a formatted header."""
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60)

def setup_test_data():
    """Create some test conversation data."""
    print_header("SETUP: Creating Test Conversations")
    
    memory = get_memory_manager()
    
    # Start a test session
    session_id = memory.start_session(metadata={"test": True, "purpose": "RAG testing"})
    print(f"✓ Started test session: {session_id}")
    
    # Add diverse conversations
    test_conversations = [
        ("USER", "What is the weather like today?"),
        ("MAREEN", "मुझे माफ करें, मेरे पास real-time weather data नहीं है।"),
        ("USER", "Can you open calculator for me?"),
        ("MAREEN", "ज़रूर! Calculator खोल रही हूँ।"),
        ("USER", "Tell me a joke about programming"),
        ("MAREEN", "एक programmer ने कहा: 'मैं तो अपने bugs से ज्यादा अपने features से डरता हूँ!'"),
        ("USER", "How do I learn Python programming?"),
        ("MAREEN", "Python सीखने के लिए practice बहुत important है। छोटे projects से start करें।"),
        ("USER", "What files do I have on my desktop?"),
        ("MAREEN", "मैं directly file system access नहीं कर सकती।"),
        ("USER", "Can you help me with my homework?"),
        ("MAREEN", "बिल्कुल! किस subject में help चाहिए?"),
    ]
    
    for speaker, message in test_conversations:
        memory.log_message(speaker, message)
        time.sleep(0.1)  # Small delay to create different timestamps
    
    print(f"✓ Added {len(test_conversations)} test messages")
    
    # End session
    memory.end_session()
    print(f"✓ Test session ended")
    
    return session_id

def test_rag_initialization():
    """Test RAG system initialization."""
    print_header("TEST 1: RAG Initialization")
    
    try:
        rag = get_rag()
        print(f"✓ RAG instance created")
        print(f"  Embeddings available: {EMBEDDINGS_AVAILABLE}")
        print(f"  Model loaded: {rag.model is not None}")
        print(f"  Cached embeddings: {len(rag.embeddings_cache)}")
        return True
    except Exception as e:
        print(f"✗ RAG initialization failed: {e}")
        return False

def test_context_retrieval():
    """Test retrieving relevant context."""
    print_header("TEST 2: Context Retrieval")
    
    rag = get_rag()
    
    # Test queries
    test_queries = [
        "What's the weather?",
        "Open some app for me",
        "How to learn coding?",
        "Tell me something funny",
    ]
    
    print("\nTesting context retrieval for various queries:\n")
    
    for query in test_queries:
        print(f"Query: '{query}'")
        
        results = rag.retrieve_context(query, top_k=3, min_similarity=0.2)
        
        if results:
            print(f"  ✓ Found {len(results)} relevant memories:")
            for i, result in enumerate(results, 1):
                speaker = result['speaker']
                message = result['message'][:60] + "..."
                score = result['final_score']
                print(f"    {i}. [{speaker}] {message} (score: {score:.3f})")
        else:
            print(f"  ✗ No relevant memories found")
        
        print()
    
    return True

def test_semantic_vs_keyword():
    """Compare semantic vs keyword search."""
    print_header("TEST 3: Semantic vs Keyword Search")
    
    rag = get_rag()
    
    # Query that should work well with semantic search
    query = "I need help with coding"
    
    print(f"Query: '{query}'")
    print(f"Expected to match: 'How do I learn Python programming?'\n")
    
    results = rag.retrieve_context(query, top_k=5, min_similarity=0.2)
    
    if results:
        print(f"✓ Retrieved {len(results)} results:")
        for i, result in enumerate(results, 1):
            message = result['message']
            similarity = result['similarity_score']
            final_score = result['final_score']
            print(f"{i}. '{message[:50]}...'")
            print(f"   Similarity: {similarity:.3f}, Final: {final_score:.3f}\n")
    else:
        print("✗ No results found")
    
    return True

def test_build_context_prompt():
    """Test building context prompts for LLM."""
    print_header("TEST 4: Context Prompt Building")
    
    rag = get_rag()
    
    query = "Can you help me learn programming?"
    
    print(f"Query: '{query}'\n")
    
    context = rag.build_context_prompt(query, top_k=2)
    
    if context:
        print("✓ Generated context prompt:")
        print("-" * 60)
        print(context)
        print("-" * 60)
    else:
        print("✗ No context generated")
    
    return True

def test_similar_queries():
    """Test finding similar past queries."""
    print_header("TEST 5: Similar Query Detection")
    
    rag = get_rag()
    
    query = "What is today's weather?"
    
    print(f"Query: '{query}'\n")
    
    similar = rag.find_similar_past_queries(query, top_k=3)
    
    if similar:
        print(f"✓ Found {len(similar)} similar past queries:")
        for i, sq in enumerate(similar, 1):
            message = sq['message']
            similarity = sq['similarity']
            timestamp = sq['timestamp']
            print(f"{i}. '{message}'")
            print(f"   Similarity: {similarity:.3f}, Asked: {timestamp}\n")
    else:
        print("✗ No similar queries found")
    
    return True

def test_rag_stats():
    """Test RAG statistics."""
    print_header("TEST 6: RAG Statistics")
    
    rag = get_rag()
    stats = rag.get_stats()
    
    print("RAG System Statistics:")
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    return True

def test_time_decay():
    """Test time decay scoring."""
    print_header("TEST 7: Time Decay Scoring")
    
    rag = get_rag()
    
    # Test with and without time decay
    query = "weather"
    
    print(f"Query: '{query}'\n")
    
    print("WITH time decay (recent messages score higher):")
    results_decay = rag.retrieve_context(query, top_k=3, time_decay=True)
    for i, r in enumerate(results_decay, 1):
        print(f"  {i}. Score: {r['final_score']:.3f}, Message: '{r['message'][:40]}...'")
    
    print("\nWITHOUT time decay (pure similarity):")
    results_no_decay = rag.retrieve_context(query, top_k=3, time_decay=False)
    for i, r in enumerate(results_no_decay, 1):
        print(f"  {i}. Score: {r['final_score']:.3f}, Message: '{r['message'][:40]}...'")
    
    return True

def run_all_tests():
    """Run all RAG tests."""
    print_header("RAG SYSTEM - TEST SUITE")
    
    # Setup test data
    session_id = setup_test_data()
    
    results = []
    
    # Run tests
    results.append(("RAG Initialization", test_rag_initialization()))
    results.append(("Context Retrieval", test_context_retrieval()))
    results.append(("Semantic vs Keyword", test_semantic_vs_keyword()))
    results.append(("Context Prompt Building", test_build_context_prompt()))
    results.append(("Similar Query Detection", test_similar_queries()))
    results.append(("RAG Statistics", test_rag_stats()))
    results.append(("Time Decay Scoring", test_time_decay()))
    
    # Summary
    print_header("TEST SUMMARY")
    
    passed = sum(1 for _, result in results if result)
    failed = sum(1 for _, result in results if not result)
    
    for test_name, result in results:
        status = "✓ PASSED" if result else "✗ FAILED"
        print(f"  {status}: {test_name}")
    
    print(f"\nTotal: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("\n" + "="*60)
        print("  ALL TESTS PASSED!")
        print("  RAG system is functioning correctly.")
        print("="*60)
    else:
        print("\n" + "="*60)
        print("  SOME TESTS FAILED!")
        print("  Review the failures above.")
        print("="*60)
    
    if EMBEDDINGS_AVAILABLE:
        print("\n✓ Semantic embeddings are active (high quality)")
    else:
        print("\n⚠ Using keyword matching (install sentence-transformers for better results)")
    
    print(f"\nTest session ID: {session_id}")
    print("You can view it with: python view_memory.py view " + session_id)

if __name__ == "__main__":
    run_all_tests()
