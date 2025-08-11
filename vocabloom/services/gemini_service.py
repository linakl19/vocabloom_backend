import google.generativeai as genai
from django.conf import settings
import logging
import json
import re

logger = logging.getLogger(__name__)

class GeminiService:
    def __init__(self):
        try:
            genai.configure(api_key=settings.GEMINI_API_KEY)
            self.model = genai.GenerativeModel(model_name="gemini-1.5-flash")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini: {e}")
            self.model = None


    def generate_user_example(self, word, context=None, difficulty_level="intermediate"):
        """
        Generate a user example sentence for a given word
        """
        if not self.model:
            return {"error": "Gemini service not available"}

        try:
            # Construct the prompt
            prompt = self._build_prompt(word, context, difficulty_level)
            
            logger.info(f"Generating example for word: '{word}' with Gemini")
            
            # Generate content
            response = self.model.generate_content(prompt)
            
            if not response.text:
                return {"error": "No response generated"}
            
            # Clean and validate the response
            example = self._clean_response(response.text)
            
            if not example:
                return {"error": "Invalid response format"}
            
            return {
                "success": True,
                "example": example,
                "word": word
            }
            
        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            return {"error": f"Failed to generate example: {str(e)}"}
    

    def _build_prompt(self, word, context, difficulty_level):
        """Build the prompt for Gemini"""
        difficulty_instructions = {
            "beginner": "Use simple vocabulary and basic sentence structure",
            "intermediate": "Use moderate vocabulary and varied sentence structure",
            "advanced": "Use sophisticated vocabulary and complex sentence structure"
        }
        
        difficulty_instruction = difficulty_instructions.get(difficulty_level, "Use moderate vocabulary")
        pos_instruction = f" in this context {context}" if context else ""
        
        prompt = f"""
        Create a natural, practical example sentence using the word "{word}"{pos_instruction}.
        
        Requirements:
        - {difficulty_instruction}
        - The sentence should be between 5-15 words long
        - Make it relatable to everyday life or common situations
        - The sentence is for english learners
        - The word should be used correctly and naturally
        - Return only the sentence, no explanations or additional text
        - Do not use quotation marks around the sentence
        """
        
        return prompt


    def _clean_response(self, text):
        """Clean and validate the response from Gemini"""
        if not text:
            return None
        
        # Remove quotes, extra whitespace, and newlines
        cleaned = text.strip().strip('"').strip("'").strip()
        
        # Remove any numbering (1., 2., etc.)
        cleaned = re.sub(r'^\d+\.\s*', '', cleaned)
        
        # Remove bullet points
        cleaned = re.sub(r'^[-•*]\s*', '', cleaned)
        
        # Ensure it ends with proper punctuation
        if cleaned and not cleaned[-1] in '.!?':
            cleaned += '.'
        
        return cleaned if cleaned else None