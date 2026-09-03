import urllib.parse
import requests

def format_title_for_omdb(title: str) -> str:
    """Cleans film title and converts it to a URL-encoded string for OMDB API."""
    cleaned_title = title.strip()
    return urllib.parse.quote_plus(cleaned_title)

def fetch_omdb_details(title: str, api_key :str) -> dict:
    """Fetches movie metadata including posters, plot, actors, and genre from OMDB API."""
    if not api_key:
        return None
        
    encoded_title = format_title_for_omdb(title)
    url = f"http://www.omdbapi.com/?t={encoded_title}&apikey={api_key}"
    
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get("Response") == "True":
                return {
                    "Title": data.get("Title", title),
                    "Year": data.get("Year", "N/A"),
                    "Genre": data.get("Genre", "N/A"),
                    "Actors": data.get("Actors", "N/A"),
                    "Plot": data.get("Plot", "No plot available."),
                    "Poster": data.get("Poster") if data.get("Poster") != "N/A" else "https://via.placeholder.com/300x450?text=No+Poster+Available"
                }
    except Exception as e:
        print(f"Error fetching OMDB data for {title}: {e}")
        
    return {
        "Title": title,
        "Year": "N/A",
        "Genre": "N/A",
        "Actors": "N/A",
        "Plot": "Metadata unavailable.",
        "Poster": "https://via.placeholder.com/300x450?text=No+Poster+Available"
    }