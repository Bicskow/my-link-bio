import logging
import os
import secrets
from datetime import datetime, timezone
from uuid import uuid4

import requests
from bs4 import BeautifulSoup
from flask import Flask, abort, flash, jsonify, redirect, render_template, request, url_for

logging.basicConfig(level=logging.INFO)

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY") or secrets.token_hex(32)

links = [
    {"name": "Google", "url": "https://www.google.com"},
    {"name": "GitHub", "url": "https://github.com"},
    {"name": "Wikipedia", "url": "https://www.wikipedia.org"},
]
for link in links:
    link["id"] = uuid4().hex
    link.update(title="Not Available", description="Not Available", image_url="Not Available")


def fetch_metadata(url):
    metadata = dict.fromkeys(("title", "description", "image_url"), "Not Available")
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
    except requests.RequestException as error:
        logging.warning("Request failed for %s: %s", url, error)
        return metadata

    soup = BeautifulSoup(response.content, "html.parser")
    for field, property_name in (
        ("title", "og:title"),
        ("description", "og:description"),
        ("image_url", "og:image"),
    ):
        tag = soup.find("meta", attrs={"property": property_name})
        if tag and tag.get("content", "").strip():
            metadata[field] = tag["content"].strip()
    return metadata


@app.route("/")
def index():
    return render_template("index.html", links=links)


@app.route("/health")
def health():
    return jsonify(status="ok", time=datetime.now(timezone.utc).isoformat()), 200


@app.route("/add", methods=["POST"])
def add_link():
    name = request.form["name"]
    url = request.form["url"]
    metadata = fetch_metadata(url)
    if all(metadata[field] == "Not Available" for field in ("title", "description", "image_url")):
        logging.warning("Metadata could not be retrieved for %s", url)
        flash("We saved your link but could not retrieve a preview for that URL.", "warning")
    links.append({
        "id": uuid4().hex,
        "name": name,
        "url": url,
        **metadata,
    })
    logging.info("Added new link %s: %s", name, url)
    return redirect(url_for("index"))


@app.route("/delete/<link_id>", methods=["POST"])
def delete_link(link_id):
    for link in links:
        if link["id"] == link_id:
            links.remove(link)
            return redirect(url_for("index"))
    abort(404)


@app.route("/edit/<link_id>", methods=["GET", "POST"])
def edit_link(link_id):
    link = next((link for link in links if link["id"] == link_id), None)
    if link is None:
        abort(404)
    if request.method == "POST":
        name = request.form["name"]
        url = request.form["url"]
        if url != link["url"]:
            link.update(fetch_metadata(url))
        link.update(name=name, url=url)
        return redirect(url_for("index"))
    return render_template("edit.html", link=link)


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")


@app.errorhandler(404)
def page_not_found(error):
    return render_template("404.html"), 404


@app.errorhandler(500)
def internal_server_error(error):
    if request.endpoint == "health":
        return jsonify(status="error"), 500
    return render_template("500.html"), 500


if __name__ == "__main__":
    app.run()
