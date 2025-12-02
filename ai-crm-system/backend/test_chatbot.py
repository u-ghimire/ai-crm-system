#!/usr/bin/env python3
"""Test script for the AI-powered chatbot"""

import sys
sys.path.insert(0, '/workspaces/ai-crm-system/ai-crm-system/backend')

from modules.huggingface_ai import HuggingFaceAI
from modules.chatbot import ChatBot
import json

print("Loading Qwen AI model...")
ai_model = HuggingFaceAI()

print("Initializing chatbot...")
chatbot = ChatBot(ai_model)

# Test 1: Simple greeting (should be instant)
print("\n" + "="*60)
print("TEST 1: Simple greeting")
print("="*60)
result = chatbot.process_message("hello")
print(f"User: hello")
print(f"Bot: {result['message']}")
print(f"Intent: {result['intent']}")
print(f"Action: {result['action']}")

# Test 2: Create customer with name and company
print("\n" + "="*60)
print("TEST 2: Create customer John Doe from Acme Corp")
print("="*60)
result = chatbot.process_message("Create customer named John Doe from Acme Corp")
print(f"User: Create customer named John Doe from Acme Corp")
print(f"Bot: {result['message']}")
print(f"Intent: {result['intent']}")
print(f"Action: {result['action']}")
print(f"Extracted Data: {json.dumps(result['extracted_data'], indent=2)}")

# Test 3: Create customer with email
print("\n" + "="*60)
print("TEST 3: Add customer John Smith, email john@example.com")
print("="*60)
result = chatbot.process_message("Add customer John Smith, email john@example.com")
print(f"User: Add customer John Smith, email john@example.com")
print(f"Bot: {result['message']}")
print(f"Intent: {result['intent']}")
print(f"Action: {result['action']}")
print(f"Extracted Data: {json.dumps(result['extracted_data'], indent=2)}")

# Test 4: Create customer with company and email
print("\n" + "="*60)
print("TEST 4: New customer from Tech Industries, contact info@tech.com")
print("="*60)
result = chatbot.process_message("New customer from Tech Industries, contact info@tech.com")
print(f"User: New customer from Tech Industries, contact info@tech.com")
print(f"Bot: {result['message']}")
print(f"Intent: {result['intent']}")
print(f"Action: {result['action']}")
print(f"Extracted Data: {json.dumps(result['extracted_data'], indent=2)}")

# Test 5: Question about CRM
print("\n" + "="*60)
print("TEST 5: Explain me what is crm")
print("="*60)
result = chatbot.process_message("Explain me what is crm")
print(f"User: Explain me what is crm")
print(f"Bot: {result['message']}")
print(f"Intent: {result['intent']}")
print(f"Action: {result['action']}")

print("\n" + "="*60)
print("ALL TESTS COMPLETED!")
print("="*60)
