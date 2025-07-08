import os
import json
import re
import requests
from datetime import datetime
from typing import Dict, Any, Optional

try:
    from langchain_core.prompts import ChatPromptTemplate
    from langchain_google_genai import ChatGoogleGenerativeAI
    LANGCHAIN_AVAILABLE = True
except ImportError:
    print("⚠️ LangChain modules not available in phone_agent, using fallback mode")
    LANGCHAIN_AVAILABLE = False

# Initialize Gemini LLM
if LANGCHAIN_AVAILABLE:
    gemini_llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-pro",
        google_api_key=os.getenv("GOOGLE_API_KEY"),
        temperature=0.4
    )
else:
    gemini_llm = None


def extract_phone_numbers_from_text(content: str) -> list[Dict[str, str]]:
    """
    Extract phone numbers from text content using regex patterns.
    
    Args:
        content: Text content to search for phone numbers
        
    Returns:
        List of dictionaries containing found phone numbers
    """
    import re
    
    phone_numbers_found = []
    
    # Look for various phone number patterns
    phone_patterns = [
        r'\+44\s*\d{2,4}\s*\d{3,4}\s*\d{3,4}',  # +44 format
        r'0\d{2,4}\s*\d{3,4}\s*\d{3,4}',        # UK format starting with 0
        r'\d{3,4}\s*\d{3,4}\s*\d{3,4}',         # General format
        r'\(\d{3,4}\)\s*\d{3,4}[-\s]*\d{3,4}'   # (xxx) xxx-xxxx format
    ]
    
    for pattern in phone_patterns:
        matches = re.findall(pattern, content)
        for match in matches:
            cleaned_phone = re.sub(r'[^\d+]', '', match)
            if len(cleaned_phone) >= 10:  # Valid phone number length
                phone_numbers_found.append({
                    "number": match.strip(),
                    "cleaned": cleaned_phone
                })
    
    return phone_numbers_found


def format_phone_number_international(phone_number: str) -> str:
    """
    Convert phone number to international format.
    
    Args:
        phone_number: Raw phone number string
        
    Returns:
        Phone number in international format
    """
    # Remove all non-digit characters except +
    cleaned = re.sub(r'[^\d+]', '', phone_number)
    
    # Convert to international format if needed
    if cleaned.startswith("0"):
        return "+44" + cleaned[1:]
    elif not cleaned.startswith("+"):
        return "+44" + cleaned
    else:
        return cleaned 