# realtime_translation.py
import google.generativeai as genai

from config import GEMINI_API_KEY
from utility import tts, recognizer

# Configure Gemini API
genai.configure(api_key=GEMINI_API_KEY)

# Initialize the Gemini model
generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

model = genai.GenerativeModel(
    model_name="gemini-2.0-flash-exp",
    generation_config=generation_config,
)


def translate_text(text, target_language="en"):
    """
    Translates text to a specified target language.

    Parameters:
        text (str): The text to translate.
        target_language (str): The language code to translate the text to (e.g., "en" for English, "fr" for French).

    Returns:
        str: The translated text.
    """
    try:

        response = model.generate_content(f"""
        Translate the following text to {target_language}. Don't include the original text in the response. :
        {text}
        """)
        translated_text = response.text
        return translated_text

    except Exception as e:
        print(f"Error during translation: {e}")
        return None


# Voice Interaction
def translation_voice_interaction():
    """
    Main function to interact with the Real-Time Translation system.
    It listens for input in one language and translates it to another language.
    """
    tts.speak("Real-Time Translation - Say 'exit' to quit.")

    while True:
        tts.speak("Please say something to translate...")
        text_to_translate = recognizer.listen()

        if "exit" in text_to_translate.lower():
            tts.speak("Exiting Real-Time Translation.")
            break

        print(f"Original Text: {text_to_translate}")

        # Ask the user for the target language
        # tts.speak("Which language would you like to translate to? For example, say 'French', 'Spanish', or 'English'.")
        # target_language = "english"  # recognizer.listen().lower()

        # Map spoken language names to language codes
        # language_map = {
        #     "english": "en",
        #     "french": "fr",
        #     "spanish": "es",
        #     "german": "de",
        #     "italian": "it"
        # }

        language_code = "en "  # language_map.get(target_language, "en")

        translated_text = translate_text(text_to_translate, target_language=language_code)
        if translated_text:
            print("Translated Text :", translated_text)
            tts.speak(translated_text)
        else:
            tts.speak("Sorry, I couldn't translate that. Please try again.")
