# modules/groq_ai.py
"""
AI module using Groq Cloud API for fast, intelligent responses.
Uses Qwen3 model via Groq SDK.
"""

import os
from groq import Groq

class GroqAI:
    def __init__(self, model_name='qwen/qwen3-32b'):
        """
        Initializes the Groq API client.
        
        Args:
            model_name (str): The Groq model to use (default: qwen/qwen3-32b)
        """
        self.model_name = model_name
        api_key = os.environ.get('GROQ_API_KEY')
        
        if not api_key:
            print("WARNING: GROQ_API_KEY not found in environment variables!")
            print("Please set it with: export GROQ_API_KEY='your_api_key_here'")
            print("Get your API key from: https://console.groq.com/keys")
            self.client = None
        else:
            self.client = Groq(api_key=api_key)
            print(f"✓ Groq API initialized with model: {model_name}")

    def generate(self, prompt: str, max_length: int = 300) -> str:
        """
        Generates text using Groq Cloud API.
        
        Args:
            prompt (str): The input prompt for the model.
            max_length (int): The maximum number of tokens to generate (default: 300).
            
        Returns:
            str: The generated text.
        """
        if not self.client:
            return "Error: Groq API key not configured. Please set GROQ_API_KEY environment variable."
            
        try:
            completion = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful CRM assistant. Provide concise, professional responses. Do not include thinking tags or internal reasoning - only provide the final answer."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_completion_tokens=max_length,
                top_p=0.9,
                stream=False
            )
            
            generated_text = completion.choices[0].message.content
            
            # Remove thinking tags if present
            import re
            generated_text = re.sub(r'<think>.*?</think>', '', generated_text, flags=re.DOTALL)
            
            return generated_text.strip()
            
        except Exception as e:
            print(f"Error during text generation: {e}")
            return "Error generating AI response."


# Example usage (for testing)
if __name__ == '__main__':
    ai = GroqAI()
    
    # Test case 1
    result = ai.generate("What is CRM?", max_length=50)
    print(f"Test: {result}")
