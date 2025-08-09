import os
import google.generativeai as genai
from dotenv import load_dotenv
from pathlib import Path
import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
env_path = Path(__file__).parent / ".env"
load_dotenv(env_path)

# Get API key
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("❌ GEMINI_API_KEY not found in .env file")

# Configure Gemini
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")


def get_ai_response(prompt: str) -> str:
    """
    Get complete response from Gemini AI with proper streaming
    """
    try:
        logger.info(f"Processing query: {prompt}")

        # Use streaming for complete responses
        response = model.generate_content(
            prompt,
            stream=True,  # Enable streaming for longer responses
            generation_config={
                "max_output_tokens": 2000,
                "temperature": 0.7
            }
        )

        # Collect all chunks of the response
        full_response = []
        for chunk in response:
            if chunk.text:
                full_response.append(chunk.text)

        complete_response = " ".join(full_response)

        if not complete_response:
            logger.warning("Received empty response from Gemini")
            return "I didn't receive a response. Could you please ask again?"

        logger.info(f"Full response length: {len(complete_response)} characters")
        return complete_response

    except Exception as e:
        logger.error(f"Gemini API error: {str(e)}")
        return "Sorry, I encountered an error processing your request."