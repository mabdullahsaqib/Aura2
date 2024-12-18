# web_browsing.py
import webbrowser
import google.generativeai as genai
import requests
from utility import tts, recognizer
from config import GOOGLE_API_KEY, GOOGLE_CSE_ID, GEMINI_API_KEY

# Configure Gemini API
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

# Perform a web search using Google Custom Search API
def search_web(query, num_results=5):
    search_url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "key": GOOGLE_API_KEY,
        "cx": GOOGLE_CSE_ID,
        "q": query,
        "num": num_results
    }

    try:
        response = requests.get(search_url, params=params)
        response.raise_for_status()  # Raise an error for unsuccessful status codes
        results = response.json()

        if "items" not in results:
            print("No results found.")
            return []

        search_results = []
        for item in results["items"]:
            search_results.append({
                "title": item["title"],
                "link": item["link"],
                "snippet": item.get("snippet", "No description available.")
            })

        return search_results
    except requests.exceptions.RequestException as e:
        print(f"An error occurred while performing the search: {e}")
        return []

# Displays search results in a readable format
def display_results(results):
    print("\nSearch Results:")
    for i, result in enumerate(results, start=1):
        print(f"\nResult {i}:")
        print(f"Title: {result['title']}")
        print(f"Link: {result['link']}")
        print(f"Snippet: {result['snippet']}\n")

# Summarizes the snippets from search results using Gemini API
def summarize_results_with_gemini(results):
    snippets = " ".join([result["snippet"] for result in results])

    if snippets:
        # Send the snippets to Gemini for summarization
        response = model.generate_content("Summarize the following text: " + snippets)
        return response.text
    return "No content available for summarization."

# Opens a link from the search results
def open_link(results):
    for i, result in enumerate(results, start=1):
        print(f"{i}. {result['title']} - {result['link']}")
    tts.speak("Please select a link by saying the corresponding number.")
    choice = recognizer.listen()
    if choice.isdigit() and 1 <= int(choice) <= len(results):
        webbrowser.open(results[int(choice) - 1]["link"])
        print(f"Opening link: {results[int(choice) - 1]['link']}")
    else:
        print("No link selected.")

# Voice Interaction
def web_browsing_voice_interaction(query):
    if query:
        # Fetch search results
        tts.speak(f"Searching for {query}.")
        results = search_web(query)

        # Display results
        tts.speak("Here are the top search results.")
        display_results(results)

        # Summarize results with Gemini
        tts.speak("Would you like a summary of the results?")
        if "yes" in recognizer.listen().lower():
            summary = summarize_results_with_gemini(results)
            tts.speak("Here is a summary of the search results.")
            print("\nSummary of Search Results:\n", summary)

        # Open a link if requested
        tts.speak("Would you like to open any of these links?")
        response = recognizer.listen().lower()
        if "yes" in response:
            open_link(results)
        else:
            tts.speak("Returning to search query mode. Please provide another query or say 'exit' to quit.")
