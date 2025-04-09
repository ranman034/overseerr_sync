import requests
import logging
import os
from datetime import datetime
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO)
load_dotenv()

# Define the API endpoints and API keys
overseerr_url = os.getenv("OVERSEERR_URL") 
overseerr_api_key = os.getenv("OVERSEERR_API_KEY")
default_radarr_url = os.getenv("DEFAULT_RADARR_URL")
default_radarr_api_key = os.getenv("DEFAULT_RADARR_API_KEY")
uhd_radarr_url = os.getenv("UHD_RADARR_URL")
uhd_radarr_api_key = os.getenv("UHD_RADARR_API_KEY")
hd_profile = os.getenv("HD_PROIFILE_ID", "HD-1080p")
uhd_profile = os.getenv("UHD_PROIFILE_ID", "Ultra-HD")
root_folder_path = os.getenv("ROOT_FOLDER_PATH", "/movies")

# Function to get requests from Overseerr
def get_overseerr_requests():
    headers = {"X-Api-Key": overseerr_api_key}
    response = requests.get(f"{overseerr_url}/request?take=200", headers=headers)
    response.raise_for_status()  # Raise an error for bad status codes
    return response.json()["results"]

# Function to filter requests since Jan 1 2024
def filter_requests_since_date(requests, since_date = None):
    if since_date is None:
        since_date = datetime(2024, 1, 1)
    filtered_requests = []
    for request in requests:
        request_date = datetime.strptime(request["createdAt"], "%Y-%m-%dT%H:%M:%S.%fZ")
        is_approved = request["status"] == 2
        if request_date >= since_date and is_approved:
            filtered_requests.append(request)
    default_filtered_requests, uhd_filtered_requests = [], []
    for filtered_request in filtered_requests:
        if "type" in filtered_request and filtered_request["type"] != "movie":
            continue
        if "is4k" in filtered_request and filtered_request["is4k"] and uhd_radarr_api_key is not None:
            uhd_filtered_requests.append(filtered_request)
        else:
            default_filtered_requests.append(filtered_request)
    return default_filtered_requests, uhd_filtered_requests

# Function to fetch movie details from Radarr
def get_movie_details_from_radarr(tmdb_id, is_uhd_radarr = False):
    api_key = default_radarr_api_key
    url = default_radarr_url
    if is_uhd_radarr:
        api_key = uhd_radarr_api_key
        url = uhd_radarr_url
    headers = {"X-Api-Key": api_key}
    response = requests.get(f"{url}/movie/lookup/tmdb?tmdbId={tmdb_id}", headers=headers)
    logging.info("Radarr Lookup Response Status Code: %s", response.status_code)
    logging.debug("Radarr Lookup Response Content: %s", response.text)
    response.raise_for_status()  # Raise an error for bad status codes
    return response.json()  # Assuming the response is a single movie object

# Function to add a movie to Radarr
def add_movie_to_radarr(movie, profile_id, is_uhd_radarr = False):
    api_key = default_radarr_api_key
    url = default_radarr_url
    if is_uhd_radarr:
        api_key = uhd_radarr_api_key
        url = uhd_radarr_url
    headers = {"X-Api-Key": api_key, "Content-Type": "application/json"}
    payload = {
        "title": movie["title"],
        "qualityProfileId": profile_id,
        "titleSlug": movie["titleSlug"],
        "images": movie["images"],
        "tmdbId": movie["tmdbId"],
        "year": movie["year"],
        "rootFolderPath": root_folder_path,
        "monitored": True,
        "addOptions": {"searchForMovie": False}
    }
    response = requests.post(f"{url}/movie", json=payload, headers=headers)
    logging.info(f"Adding movie {movie['title']} to Radarr. Status Code: {response.status_code}")
    # logging.info(f"response text {response.text}")
    return response.status_code == 201

def sync_radarr(requests, profile_id, is_uhd_radarr = False):
    for request in requests:
        tmdb_id = request["media"]["tmdbId"]
        movie_details = get_movie_details_from_radarr(tmdb_id, is_uhd_radarr)
        if add_movie_to_radarr(movie_details, profile_id, is_uhd_radarr):
            logging.info(f"Added {movie_details['title']} to Radarr")
        else:
            logging.error(f"Failed to add {movie_details['title']} to Radarr")

def get_radarr_qualityprofile_id(profile_name, is_uhd_radarr = False):
    api_key = default_radarr_api_key
    url = default_radarr_url
    if is_uhd_radarr:
        api_key = uhd_radarr_api_key
        url = uhd_radarr_url
    headers = {"X-Api-Key": api_key}
    response = requests.get(f"{url}/qualityprofile", headers=headers)
    data = response.json()
    profile_id = None
    for profile in data:
        if profile["name"] == profile_name:
            profile_id = profile.get('id')
            break
    return profile_id

# Main function to check requests in Overseerr and add them to Radarr
def main():
    try:
        requests = get_overseerr_requests()
        hd_profile_id = get_radarr_qualityprofile_id(hd_profile)
        uhd_profile_id = get_radarr_qualityprofile_id(uhd_profile, is_uhd_radarr=True)
        default_filtered_requests, uhd_filtered_requests = filter_requests_since_date(requests)
        sync_radarr(default_filtered_requests, hd_profile_id)
        sync_radarr(uhd_filtered_requests, uhd_profile_id, is_uhd_radarr=True)

    except Exception as e:
        logging.error("An error occurred: %s", e)

# Run the main function
if __name__ == "__main__":
    main()