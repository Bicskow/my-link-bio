from flask import Flask, redirect, render_template, request, url_for

app = Flask(__name__)

links = [
    {"name": "Google", "url": "https://www.google.com"},
    {"name": "GitHub", "url": "https://github.com"},
    {"name": "Wikipedia", "url": "https://www.wikipedia.org"},
]


@app.route("/")
def index():
    return render_template("index.html", links=links)


@app.route("/add", methods=["POST"])
def add_link():
    links.append({"name": request.form["name"], "url": request.form["url"]})
    return redirect(url_for("index"))


@app.route("/about")
def about():
    return render_template("about.html")


if __name__ == "__main__":
    app.run()
