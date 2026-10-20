# my-link-bio

## Project Overview

A personal link page built with Python and Flask that displays saved URLs as styled cards.

## Features

- Add, edit, and delete links, with Open Graph previews when available. Links are stored in memory and reset when the app restarts.
- Submit a site name and URL through the homepage form (`POST /add`, fields `name` and `url`). The app fetches the page's Open Graph title, description, and image, then redirects to the homepage. Missing fields display as `Not Available`.
- If all three preview fields are unavailable, the link is still saved and a one-time warning appears: “We saved your link but could not retrieve a preview for that URL.” Cards with missing fields use a dashed amber border and a **Preview unavailable** or **Preview incomplete** label.
- Application logs include successful link additions at INFO level and metadata failures at WARNING level. Failed requests include the URL and error message.
- View the About page at `/about`.
- Open **Contact** from the homepage or About page to see a short message and clickable email address. `GET /contact` requires no inputs; for example, visit `http://127.0.0.1:5000/contact`.

## Setup

```sh
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Visit `http://127.0.0.1:5000`. Replace the placeholder `hello@example.com` in both the displayed text and `mailto:` link in `templates/contact.html` with your contact address. The contact page needs no additional configuration or dependencies.

Set the `SECRET_KEY` environment variable to a stable random secret when deploying so flash messages work across workers and restarts. Local runs generate a temporary key automatically.

Generate a key with the following command, then save its output as `SECRET_KEY` in your hosting provider's environment settings. Use the same value for all workers and keep it private.

```sh
python -c "import secrets; print(secrets.token_hex(32))"
```

## Dependencies

Install dependencies using `requirements.txt`:

- Flask 3.1.2: web application and templates.
- gunicorn 26.2.0: production server (`gunicorn app:app`).
- requests 2.34.2: retrieve linked pages.
- beautifulsoup4 4.15.0: extract Open Graph metadata.
