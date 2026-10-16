import unittest
from copy import deepcopy
from unittest.mock import Mock, patch

import requests
from bs4 import BeautifulSoup

from app import app, links


class LinkMetadataTests(unittest.TestCase):
    def setUp(self):
        self.original_links = deepcopy(links)
        self.client = app.test_client()

    def tearDown(self):
        links[:] = self.original_links

    @patch("app.requests.get")
    def test_add_stores_and_displays_open_graph_metadata(self, get):
        get.return_value = Mock(content=b'''
            <meta property="og:title" content="Example &amp; More">
            <meta property="og:description" content="A sample description">
            <meta property="og:image" content="https://example.com/image.png">
        ''')
        response = self.client.post("/add", data={
            "name": "Example", "url": "https://example.com"
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.headers["Location"], "/")
        get.assert_called_once_with("https://example.com", timeout=5)
        self.assertEqual(links[-1]["title"], "Example & More")
        self.assertEqual(links[-1]["description"], "A sample description")
        self.assertEqual(links[-1]["image_url"], "https://example.com/image.png")
        page = BeautifulSoup(self.client.get("/").data, "html.parser")
        card = page.select(".link-card")[-1]
        self.assertEqual(card.select_one("img")["src"], links[-1]["image_url"])
        self.assertEqual(card.select_one(".card-title").text, links[-1]["title"])
        self.assertEqual(card.select_one(".card-description").text, links[-1]["description"])
        self.assertEqual(card.select_one(".card-url")["href"], links[-1]["url"])
        self.assertEqual(card.select_one(".card-url").text, links[-1]["url"])
        self.assertEqual(card.find_all(recursive=False)[-1]["class"], ["card-link", "card-url"])

    def test_unavailable_metadata_keeps_static_card(self):
        page = BeautifulSoup(self.client.get("/").data, "html.parser")
        card = page.select_one(".link-card")
        self.assertIsNone(card.find("img"))
        self.assertEqual(card.select_one(".card-link").text, links[0]["name"])
        self.assertEqual([dd.text for dd in card.select("dd")], ["Not Available"] * 3)
        self.assertIsNotNone(card.select_one(".edit-button"))
        self.assertIsNotNone(card.select_one(".delete-button"))

    def test_partial_metadata_does_not_render_placeholder_as_image(self):
        links[0]["title"] = "A title"
        for missing in ("Not Available", "", None):
            with self.subTest(missing=missing):
                links[0]["image_url"] = missing
                page = BeautifulSoup(self.client.get("/").data, "html.parser")
                card = page.select_one(".link-card")
                self.assertIsNone(card.find("img"))
                self.assertEqual(card.select_one(".card-title").text, "A title")
                self.assertIn("Image: Not Available", card.text)
                self.assertIsNotNone(card.select_one(".card-url"))

    @patch("app.requests.get")
    def test_missing_empty_and_contentless_tags_use_fallback(self, get):
        for html in (b"<html></html>", b'''
            <meta property="og:title" content="  ">
            <meta property="og:description">
        '''):
            with self.subTest(html=html):
                get.return_value = Mock(content=html)
                self.client.post("/add", data={"name": "Empty", "url": "https://example.com"})
                for field in ("title", "description", "image_url"):
                    self.assertEqual(links[-1][field], "Not Available")

    @patch("app.requests.get")
    def test_fetch_failure_still_adds_link(self, get):
        for error in (requests.Timeout(), requests.HTTPError()):
            with self.subTest(error=type(error).__name__):
                get.side_effect = error
                response = self.client.post("/add", data={
                    "name": "Offline", "url": "https://example.com"
                })
                self.assertEqual(response.status_code, 302)
                for field in ("title", "description", "image_url"):
                    self.assertEqual(links[-1][field], "Not Available")

    @patch("app.requests.get")
    def test_editing_url_refreshes_metadata(self, get):
        get.return_value = Mock(content=b'<meta property="og:title" content="Updated">')
        link = links[0]
        response = self.client.post(f'/edit/{link["id"]}', data={
            "name": "Updated", "url": "https://example.com/new"
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(link["title"], "Updated")
        self.assertEqual(link["description"], "Not Available")
        get.reset_mock()
        self.client.post(f'/edit/{link["id"]}', data={
            "name": "Renamed", "url": link["url"]
        })
        get.assert_not_called()


if __name__ == "__main__":
    unittest.main()
