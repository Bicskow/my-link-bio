from uuid import uuid4

from flask import Flask, abort, redirect, render_template, request, url_for

app = Flask(__name__)

links = [
    {"name": "Google", "url": "https://www.google.com"},
    {"name": "GitHub", "url": "https://github.com"},
    {"name": "Wikipedia", "url": "https://www.wikipedia.org"},
]
for link in links:
    link["id"] = uuid4().hex


@app.route("/")
def index():
    return render_template("index.html", links=links)


@app.route("/add", methods=["POST"])
def add_link():
    links.append({
        "id": uuid4().hex,
        "name": request.form["name"],
        "url": request.form["url"],
    })
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
        link.update(name=name, url=url)
        return redirect(url_for("index"))
    return render_template("edit.html", link=link)


@app.route("/about")
def about():
    return render_template("about.html")


if __name__ == "__main__":
    app.run()
