# realtime_translation.py
from googletrans import Translator
from utility import tts, recognizer

# Initialize the translator
translator = Translator()

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
        # Detect the original language
        detected_language = translator.detect(text).lang
        print(f"Detected language: {detected_language}")

        # Translate the text to the target language
        translated = translator.translate(text, dest=target_language)
        print(f"Translated to {target_language}: {translated.text}")

        return translated.text

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

        if text_to_translate.lower() == "exit":
            tts.speak("Exiting Real-Time Translation.")
            break

        print(f"Original Text: {text_to_translate}")

        # Ask the user for the target language
        tts.speak("Which language would you like to translate to? For example, say 'French', 'Spanish', or 'English'.")
        target_language = recognizer.listen().lower()

        # Map spoken language names to language codes
        language_map = {
            "english": "en",
            "french": "fr",
            "spanish": "es",
            "german": "de",
            "italian": "it"
        }

        language_code = language_map.get(target_language, "en")

        translated_text = translate_text(text_to_translate, target_language=language_code)
        if translated_text:
            print("Translated Text :", translated_text)
            tts.speak(translated_text)
        else:
            tts.speak("Sorry, I couldn't translate that. Please try again.")
