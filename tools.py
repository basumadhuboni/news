import validators
from newspaper import Article
import os
import requests
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def extract_article_text(url: str) -> str:
    """Extract main article text from a news URL."""
    url = url.strip().strip("'\"")  # Remove whitespace and quotes
    if not validators.url(url):
        return "Error: Invalid URL provided."
    logger.info(f"Extracting article from URL: {url}")
    try:
        article = Article(url)
        article.download()
        article.parse()
        return article.text
    except Exception as e:
        logger.error(f"Error extracting article: {str(e)}")
        return f"Error extracting article: {str(e)}"

def summarize_text(text: str) -> str:
    """Summarize text into bullet points."""
    sentences = text.split('.')
    bullet_points = ['• ' + sentence.strip() for sentence in sentences if sentence.strip()]
    return '\n'.join(bullet_points)

def translate_text(text: str, target_language: str) -> str:
    """Translate text into the desired language."""
    try:
        api_key = os.getenv("TRANSLATE_API")
        if not api_key:
            logger.error("TRANSLATE_API not found in environment variables")
            return "Error: TRANSLATE_API not found in environment variables."

        target_language = target_language.strip().lower()
        language_map = {
            'spanish': 'es',
            'french': 'fr',
            'german': 'de',
            'hindi': 'hi',
            'chinese (simplified)': 'zh-CN',
            'english': 'en'
        }
        target_code = language_map.get(target_language, target_language)

        url = "https://translation.googleapis.com/language/translate/v2"
        params = {
            'key': api_key,
            'q': text,
            'target': target_code,
            'format': 'text'
        }
        logger.info(f"Sending translation request for text to {target_code}")
        response = requests.get(url, params=params)  # Use GET with query parameters
        if response.status_code == 200:
            translated_text = response.json()['data']['translations'][0]['translatedText']
            logger.info("Translation successful")
            return translated_text
        else:
            logger.error(f"Translation API error: Status code {response.status_code}, Response: {response.text}")
            return f"Error: Translation API returned status code {response.status_code}: {response.text}"
    except Exception as e:
        logger.error(f"Error in translation: {str(e)}")
        return f"Error in translation: {str(e)}"