# modules/huggingface_ai.py
"""
Centralized module for handling Hugging Face model loading and inference.
This prevents loading the model into memory multiple times across different modules.
"""

from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM

class HuggingFaceAI:
    def __init__(self, model_name='Qwen/Qwen2.5-1.5B-Instruct'):
        """
        Initializes the tokenizer and model.
        
        Args:
            model_name (str): The name of the Hugging Face model to use.
        """
        print(f"Loading model: {model_name}")
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModelForCausalLM.from_pretrained(
                model_name,
                device_map="cpu",
                torch_dtype="auto"
            )
            self.pipeline = pipeline(
                'text-generation',
                model=self.model,
                tokenizer=self.tokenizer
            )
            print("Model loaded successfully.")
        except Exception as e:
            print(f"Error loading Hugging Face model: {e}")
            self.pipeline = None

    def generate(self, prompt: str, max_length: int = 100) -> str:
        """
        Generates text using the loaded Hugging Face model.
        
        Args:
            prompt (str): The input prompt for the model.
            max_length (int): The maximum length of the generated text.
            
        Returns:
            str: The generated text.
        """
        if not self.pipeline:
            return "Error: AI model is not available."
            
        try:
            # Optimized parameters for faster Qwen inference on CPU
            sequences = self.pipeline(
                prompt,
                max_new_tokens=min(max_length, 80),  # Limit tokens for speed
                do_sample=False,  # Greedy decoding is faster
                num_beams=1,  # No beam search - much faster
                repetition_penalty=1.2,
                return_full_text=False,  # Only return generated text, not the prompt
                pad_token_id=self.tokenizer.eos_token_id  # Prevent warnings
            )
            
            generated_text = sequences[0]['generated_text']
            
            # Clean up the response (remove any remaining prompt artifacts)
            if prompt in generated_text:
                generated_text = generated_text.replace(prompt, '').strip()
            
            # Remove Qwen chat template artifacts if present
            generated_text = generated_text.split('<|im_end|>')[0].strip()
            
            return generated_text
        except Exception as e:
            print(f"Error during text generation: {e}")
            return "Error generating AI response."

# Example usage (for testing)
if __name__ == '__main__':
    ai = HuggingFaceAI()
    
    # Test case 1: Intent recognition
    intent_prompt = """
    Based on the user message, what is their intent?
    Message: "add a customer named John Doe from Acme Inc."
    Choose from: get_customer_info, add_note, get_sales_report, add_customer, search_knowledge_base, greeting, goodbye.
    Intent:
    """
    intent = ai.generate(intent_prompt, max_length=20)
    print(f"Test Intent Recognition: {intent}")

    # Test case 2: Entity extraction
    entity_prompt = """
    Based on the message 'add a customer named John Doe from Acme Inc.', extract the following information as a JSON object: name, company, email, phone.
    JSON:
    """
    entities = ai.generate(entity_prompt, max_length=50)
    print(f"Test Entity Extraction: {entities}")

    # Test case 3: General text generation
    insight_prompt = "Summarize the following customer interaction: Called customer to follow up on quote. Customer is interested but needs approval from manager. Follow up next week."
    insight = ai.generate(insight_prompt, max_length=50)
    print(f"Test Insight Generation: {insight}")
