#!/usr/bin/env python3

import os
import re
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_phone_extraction():
    """Test phone number extraction from sample text"""
    print("🧪 Testing Phone Number Extraction")
    print("=" * 50)
    
    # Sample text with various phone number formats
    sample_texts = [
        "Call us at +44 20 7123 4567 for delivery",
        "Phone: 020 7123 4567 or visit our website",
        "Contact: (020) 7123-4567 for orders",
        "Ring 0207 123 4567 to place your order",
        "Delivery hotline: +44 207 123 4567",
        "Pizza Palace - 020 7123 4567 - Best pizza in London"
    ]
    
    # Phone number patterns
    phone_patterns = [
        r'\+44\s*\d{2,4}\s*\d{3,4}\s*\d{3,4}',  # +44 format
        r'0\d{2,4}\s*\d{3,4}\s*\d{3,4}',        # UK format starting with 0
        r'\d{3,4}\s*\d{3,4}\s*\d{3,4}',         # General format
        r'\(\d{3,4}\)\s*\d{3,4}[-\s]*\d{3,4}'   # (xxx) xxx-xxxx format
    ]
    
    all_found_numbers = []
    
    for i, text in enumerate(sample_texts, 1):
        print(f"\n{i}. Text: {text}")
        found_in_text = []
        
        for pattern in phone_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                cleaned_phone = re.sub(r'[^\d+]', '', match)
                if len(cleaned_phone) >= 10:  # Valid phone number length
                    phone_info = {
                        "original": match.strip(),
                        "cleaned": cleaned_phone,
                        "formatted": format_uk_phone(cleaned_phone)
                    }
                    found_in_text.append(phone_info)
                    all_found_numbers.append(phone_info)
        
        if found_in_text:
            for phone in found_in_text:
                print(f"   📞 Found: {phone['original']} → {phone['formatted']}")
        else:
            print("   ❌ No phone numbers found")
    
    print(f"\n📊 Summary: Found {len(all_found_numbers)} phone numbers total")
    return all_found_numbers


def format_uk_phone(phone_number):
    """Format phone number to UK international format"""
    # Remove all non-digit characters except +
    cleaned = re.sub(r'[^\d+]', '', phone_number)
    
    # Convert to international format
    if cleaned.startswith("0"):
        return "+44" + cleaned[1:]
    elif not cleaned.startswith("+"):
        if len(cleaned) >= 10:
            return "+44" + cleaned
    
    return cleaned


def test_address_extraction():
    """Test address extraction from pizza order task"""
    print("\n🧪 Testing Address Extraction")
    print("=" * 50)
    
    test_tasks = [
        "Order a pepperoni pizza to 7 pearson square in W1 London",
        "Get pizza delivered to 123 Main Street, London W1",
        "Order food to flat 5, 42 Baker Street, W1H 5AA",
        "Pizza delivery at 10 Downing Street, Westminster"
    ]
    
    address_patterns = [
        r'to\s+([^,]+(?:,\s*[^,]+)*)',  # "to 7 pearson square, W1 London"
        r'at\s+([^,]+(?:,\s*[^,]+)*)',  # "at 123 main street"
        r'(\d+\s+[^,]+(?:,\s*[^,]+)*)'  # "123 main street, city"
    ]
    
    for i, task in enumerate(test_tasks, 1):
        print(f"\n{i}. Task: {task}")
        
        for pattern in address_patterns:
            match = re.search(pattern, task, re.IGNORECASE)
            if match:
                location = match.group(1).strip()
                search_query = f"pizza delivery restaurant phone number near {location} London"
                print(f"   📍 Extracted location: {location}")
                print(f"   🔍 Search query: {search_query}")
                break
        else:
            print("   ❌ No address pattern matched")


def test_task_analysis():
    """Test task requirement analysis"""
    print("\n🧪 Testing Task Analysis")
    print("=" * 50)
    
    test_tasks = [
        "Order a pepperoni pizza to 7 pearson square in W1 London",
        "Book a table at a restaurant for tonight",
        "Call the dentist to schedule an appointment",
        "Research the best pizza places in London and call to order"
    ]
    
    for i, task in enumerate(test_tasks, 1):
        print(f"\n{i}. Task: {task}")
        task_lower = task.lower()
        requirements = []
        
        # Pizza/food ordering requires research + phone call
        if any(keyword in task_lower for keyword in ["order", "pizza", "food", "delivery", "restaurant"]):
            requirements.extend(["research", "phone_call"])
        
        # Booking/reservation tasks
        if any(keyword in task_lower for keyword in ["book", "reserve", "appointment", "schedule"]):
            if "research" not in requirements:
                requirements.append("research")
            if "phone_call" not in requirements:
                requirements.append("phone_call")
        
        # General phone call requirement
        elif any(keyword in task_lower for keyword in ["call", "phone", "contact", "speak"]):
            requirements.append("phone_call")
        
        # Research requirement
        if any(keyword in task_lower for keyword in ["research", "find", "search", "information", "details"]):
            if "research" not in requirements:
                requirements.append("research")
        
        print(f"   📋 Requirements: {requirements}")


if __name__ == "__main__":
    print("🚀 Phone Number Discovery Test Suite")
    print("=" * 60)
    
    # Run tests
    test_phone_extraction()
    test_address_extraction()
    test_task_analysis()
    
    print("\n" + "=" * 60)
    print("✅ All tests completed!") 