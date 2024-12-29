#!/usr/bin/python


from flask import Flask, request, Response, jsonify
import requests

app = Flask(__name__)

MUSICBRAINZ_API = "https://musicbrainz.org/ws/2"
COVER_ART_ARCHIVE_API = "https://coverartarchive.org/release"

@app.route("/get_album_cover", methods=["GET"])
def get_album_cover():
	artist = request.args.get("artist")
	album = request.args.get("album")

	if not artist or not album:
		return jsonify({"error": "Both 'artist' and 'album' parameters are required."}), 400

	try:
		# Search for the release on MusicBrainz
		query = f"artist:{artist} AND release:{album}"
		response = requests.get(f"{MUSICBRAINZ_API}/release/", params={"query": query, "fmt": "json"})
		response.raise_for_status()
		results = response.json()

		if not results.get("releases"):
			return jsonify({"error": "Album not found."}), 404

		# Get the first release ID
		release_id = results["releases"][0]["id"]

		# Fetch the album cover from the Cover Art Archive
		cover_response = requests.get(f"{COVER_ART_ARCHIVE_API}/{release_id}")

		if cover_response.status_code == 404:
			return jsonify({"error": "Album cover not found."}), 404

		cover_response.raise_for_status()
		cover_data = cover_response.json()

		# Get the front cover image URL
		front_cover_url = next(
			(image["image"] for image in cover_data.get("images", []) if image.get("front")),
			None
		)

		if not front_cover_url:
			return jsonify({"error": "Front cover not available."}), 404

		# Fetch the image as binary
		image_response = requests.get(front_cover_url)
		image_response.raise_for_status()

		return Response(image_response.content, content_type=image_response.headers["Content-Type"])

	except requests.exceptions.RequestException as e:
		return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
	app.run(debug=True, port=5005)
