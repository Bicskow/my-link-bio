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
        columns = page.select(".link-metadata")[-1]
        self.assertEqual([tag.text for tag in columns.select("dt")],
                         ["Title", "Description", "Image URL"])
        self.assertEqual([tag.text for tag in columns.select("dd")],
                         [links[-1][key] for key in ("title", "description", "image_url")])

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
