from flask import Flask, render_template

app = Flask(__name__)


@app.route("/")
def index():
    links = [
        {"name": "Google", "url": "https://www.google.com"},
        {"name": "GitHub", "url": "https://github.com"},
        {"name": "Wikipedia", "url": "https://www.wikipedia.org"},
    ]
    return render_template("index.html", links=links)


@app.route("/about")
def about():
    return render_template("about.html")


if __name__ == "__main__":
    app.run()
