#!/usr/bin/env python3
"""
Direct test of chatbot logic without AI model (testing pattern matching)
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

# Mock the AI model to avoid loading it
class MockAI:
    def generate(self, prompt, max_length=100):
        return '{"intent":"general","action":null,"response":"Test response"}'

# Import chatbot
from modules.chatbot import ChatBot

# Create chatbot with mock AI
chatbot = ChatBot(MockAI())

# Test cases
test_messages = [
    "How are you?",
    "Create a customer named John Doe from Acme Corp",
    "Add customer John Smith, email john@example.com",
    "New customer from Tech Industries, contact info@tech.com",
    "What is CRM?",
    "How much does it cost?"
]

print("=" * 70)
print("CHATBOT PATTERN MATCHING TEST (No AI)")
print("=" * 70)

for msg in test_messages:
    print(f"\n📨 User: {msg}")
    response = chatbot.process_message(msg)
    print(f"🤖 Intent: {response['intent']}")
    print(f"🎯 Action: {response['action']}")
    print(f"📊 Extracted: {response['extracted_data']}")
    print(f"💬 Response: {response['message']}")
    print("-" * 70)
