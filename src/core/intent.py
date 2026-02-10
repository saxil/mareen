def basic_intent_parser(text):
    text = text.lower()
    
    # Specific file/folder intents
    if "open explorer" in text or "open file manager" in text or "open my pc" in text:
        return "explorer"
        
    if "pick a file" in text or "select a file" in text or "open a file" in text:
        return "pick_file"
        
    # Find/Search files
    if text.startswith("find file ") or text.startswith("search for ") or text.startswith("where is "):
        keyword = ""
        if text.startswith("find file "):
            keyword = text.replace("find file ", "").strip()
        elif text.startswith("search for "):
            keyword = text.replace("search for ", "").strip()
        elif text.startswith("where is "):
            keyword = text.replace("where is ", "").strip()
            
        if keyword:
            return f"find_file:{keyword}"
    
    # Handle "open [app name]" with more flexibility
    # Strip common prefixes
    clean_text = text
    for prefix in ["can you ", "please ", "jarvis ", "could you "]:
        if clean_text.startswith(prefix):
            clean_text = clean_text.replace(prefix, "", 1).strip()

    if clean_text.startswith("open ") or clean_text.startswith("launch ") or clean_text.startswith("start "):
        # Remove the verb
        app_name = clean_text.split(" ", 1)[1].strip()
        if app_name:
            return f"open:{app_name}"
            
    if "open calculator" in text:
        return "open:calculator"
    if "open notepad" in text:
        return "open:notepad"
    return None
