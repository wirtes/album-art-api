#!/usr/bin/python

from flask import Flask, request, jsonify, send_file
import requests
import os
import configparser
from io import BytesIO

# Configuration file to store the API key
CONFIG_FILE = "config.ini"

# Load API key from config file
def load_api_key():
	config = configparser.ConfigParser()
	if not os.path.exists(CONFIG_FILE):
		raise FileNotFoundError(f"Configuration file '{CONFIG_FILE}' not found.")
	config.read(CONFIG_FILE)
	return config["lastfm"]["api_key"]

# Initialize Flask app
app = Flask(__name__)

# Load API key
try:
	API_KEY = load_api_key()
except FileNotFoundError as e:
	print(e)
	exit(1)

# Last.fm API endpoint
LASTFM_API_URL = "http://ws.audioscrobbler.com/2.0/"

@app.route("/get_artwork", methods=["GET"])
def get_artwork():
	artist = request.args.get("artist")
	album = request.args.get("album")

	if not artist or not album:
		return jsonify({"error": "Missing 'artist' or 'album' parameter."}), 400

	params = {
		"method": "album.getinfo",
		"api_key": API_KEY,
		"artist": artist,
		"album": album,
		"format": "json",
		"autocorrect": "1"
	}

	response = requests.get(LASTFM_API_URL, params=params)

	if response.status_code != 200:
		return jsonify({"error": "Failed to fetch data from Last.fm API."}), 500

	data = response.json()

	if "error" in data:
		return jsonify({"error": data.get("message", "Unknown error from Last.fm API.")}), 400

	# Extract artwork URL
	try:
		artwork_url = data["album"]["image"][-1]["#text"]  # The last image typically has 600x600 resolution
		if not artwork_url:
			raise ValueError("No artwork URL available.")
		print(f"Artwork URL original: {artwork_url}")  # Log the artwork URL
		# artwork_url = artwork_url.replace("300x300", "1200x1200")
		# print(f"Artwork URL updated: {artwork_url}")  # Log the artwork URL
	except (KeyError, IndexError, ValueError):
		return jsonify({"error": "Artwork not found for the specified artist and album."}), 404

	# Download the artwork
	try:
		artwork_response = requests.get(artwork_url)
		artwork_response.raise_for_status()
	except requests.RequestException as e:
		return jsonify({"error": "Failed to download artwork."}), 500

	# Return the artwork as a file
	artwork_file = BytesIO(artwork_response.content)
	return send_file(artwork_file, mimetype="image/jpeg", as_attachment=True, download_name=f"{artist}_{album}_artwork.jpg")

if __name__ == "__main__":
	app.run(debug=True, port=5002)
