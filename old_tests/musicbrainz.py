#!/usr/bin/python


import requests
import os

def fetch_album_cover(artist_name, album_title, output_dir="covers"):
	"""
	Fetches the album cover for a given artist and album title using MusicBrainz API and Cover Art Archive.

	Args:
		artist_name (str): Name of the artist.
		album_title (str): Title of the album.
		output_dir (str): Directory to save the downloaded album cover.
	"""
	# Search for the album on MusicBrainz
	musicbrainz_url = "https://musicbrainz.org/ws/2/release/"
	query_params = {
		"query": f'artist:"{artist_name}" release:"{album_title}"',
		"fmt": "json",
	}

	print("Searching for album on MusicBrainz...")
	response = requests.get(musicbrainz_url, params=query_params)
	if response.status_code != 200:
		print(f"Error: Unable to connect to MusicBrainz API (status code {response.status_code})")
		return

	results = response.json().get("releases", [])
	if not results:
		print("No results found for the given artist and album title.")
		return

	# Get the first release's MBID (MusicBrainz Identifier)
	release_mbid = results[0]["id"]

	# Fetch the cover art from the Cover Art Archive
	cover_art_url = f"https://coverartarchive.org/release/{release_mbid}/front"
	print(f"Fetching cover art from: {cover_art_url}...")
	cover_response = requests.get(cover_art_url)
	
	if cover_response.status_code == 404:
		print("No cover art found for this release.")
		return
	elif cover_response.status_code != 200:
		print(f"Error: Unable to fetch cover art (status code {cover_response.status_code})")
		return

	# Save the cover art to the output directory
	if not os.path.exists(output_dir):
		os.makedirs(output_dir)

	file_path = os.path.join(output_dir, f"{artist_name}_{album_title}.jpg")
	with open(file_path, "wb") as f:
		f.write(cover_response.content)

	print(f"Album cover saved to: {file_path}")


# Example usage
if __name__ == "__main__":
	artist = input("Enter artist name: ").strip()
	album = input("Enter album title: ").strip()
	fetch_album_cover(artist, album)
