import ollama
import time
from core.memory import get_memory_manager
from core.soul import get_soul_protector

# Try to import RAG, fallback gracefully if dependencies missing
try:
    from core.rag import get_rag, is_rag_enabled
    RAG_AVAILABLE = True
    print("✓ RAG system available")
except ImportError:
    RAG_AVAILABLE = False
    print("⚠ RAG system not available (install sentence-transformers)")

# Load system prompt from soul.md - THIS CANNOT BE OVERRIDDEN
soul_protector = get_soul_protector()
SYSTEM_PROMPT = soul_protector.get_system_prompt()

# Initialize conversation history with the protected system prompt
HISTORY = [{'role': 'system', 'content': SYSTEM_PROMPT}]

print(f"Soul loaded successfully. Protected by {len(soul_protector.injection_patterns)} injection patterns.")

def process_text(text):
    global HISTORY
    memory = get_memory_manager()
    soul = get_soul_protector()
    
    try:
        # SOUL PROTECTION: Check for prompt injection attempts
        is_injection, detected_pattern = soul.detect_injection(text)
        
        if is_injection:
            print(f"⚠️ INJECTION ATTEMPT DETECTED: '{detected_pattern}'")
            response = soul.get_injection_response(detected_pattern)
            
            # Log the attempt to memory
            memory.log_message("USER", text, intent="injection_attempt")
            memory.log_message("MAREEN", response, intent="injection_blocked", response_time=0.001)
            
            return response
        
        start_time = time.time()
        
        # Log user message to memory
        memory.log_message("USER", text, intent=None)
        
        # RAG: Retrieve relevant context from past conversations
        context_prompt = ""
        if RAG_AVAILABLE and is_rag_enabled():
            try:
                rag = get_rag()
                context_prompt = rag.build_context_prompt(text, top_k=3)
                if context_prompt:
                    print(f"📚 RAG: Retrieved {context_prompt.count('.]')} relevant memories")
            except Exception as e:
                print(f"RAG retrieval failed: {e}")
                context_prompt = ""
        
        # Build user message with context if available
        if context_prompt:
            user_message = f"{context_prompt}\n\nCurrent query: {text}"
        else:
            user_message = text
        
        # Append the user's input to history
        HISTORY.append({'role': 'user', 'content': user_message})
        
        response = ollama.chat(model='j2', messages=HISTORY)
        
        response_content = response['message']['content']
        
        # Calculate response time
        response_time = time.time() - start_time
        
        # Append the assistant's response to history (without RAG context)
        # This prevents context pollution in the conversation history
        HISTORY.pop()  # Remove the message with RAG context
        HISTORY.append({'role': 'user', 'content': text})  # Add clean user message
        HISTORY.append({'role': 'assistant', 'content': response_content})
        
        # Log assistant response to memory
        memory.log_message("MAREEN", response_content, intent=None, response_time=response_time)
        
        return response_content
    except Exception as e:
        error_msg = f"Error connecting to Ollama: {e}"
        memory.log_message("MAREEN", error_msg, intent="error")
        return error_msg

def get_soul_stats():
    """Get statistics about soul protection system."""
    soul = get_soul_protector()
    return soul.get_soul_stats()

def verify_soul():
    """Verify soul integrity."""
    soul = get_soul_protector()
    return soul.verify_soul_integrity()

def reload_soul():
    """Reload soul from file (useful after updates)."""
    from core.soul import reload_soul as reload_soul_func
    global SYSTEM_PROMPT, HISTORY, soul_protector
    
    soul_protector = reload_soul_func()
    SYSTEM_PROMPT = soul_protector.get_system_prompt()
    
    # Reinitialize history with new soul
    HISTORY = [{'role': 'system', 'content': SYSTEM_PROMPT}]
    
    print("Soul reloaded successfully!")
    return True

def get_rag_stats():
    """Get RAG system statistics."""
    if not RAG_AVAILABLE:
        return {"available": False, "error": "RAG dependencies not installed"}
    
    try:
        rag = get_rag()
        return rag.get_stats()
    except Exception as e:
        return {"available": False, "error": str(e)}

def toggle_rag(enabled: bool):
    """Enable or disable RAG context retrieval."""
    if not RAG_AVAILABLE:
        print("RAG system not available. Install sentence-transformers.")
        return False
    
    try:
        from core.rag import enable_rag_context
        enable_rag_context(enabled)
        status = "enabled" if enabled else "disabled"
        print(f"RAG context {status}")
        return True
    except Exception as e:
        print(f"Error toggling RAG: {e}")
        return False
