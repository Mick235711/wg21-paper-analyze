#!/usr/bin/env python3

""" Download all WG21 papers """

import os
import json
import requests
from io import BytesIO
from bs4 import BeautifulSoup
from http.cookiejar import MozillaCookieJar
from tqdm import tqdm
from pypdf import PdfReader
from pypdf.errors import PdfReadError


store_dir = "docs/"


def main() -> None:
    """ Main function """
    os.makedirs(store_dir, exist_ok=True)
    index_dict = json.load(open("index.json", "r"))
    total_length = len([
        name for name, data in index_dict.items()
        if data["type"] in ["paper", "standing-document"] and
        "long_link" in data
    ]) - len(os.listdir(store_dir))
    cookies = MozillaCookieJar("wg21-cookie.txt")
    cookies.load()

    new_files = []
    with tqdm(desc="Downloading Papers", total=total_length) as bar:
        for name, data in index_dict.items():
            if data["type"] not in ["paper", "standing-document"]:
                continue
            if "long_link" in data:
                link = data["long_link"]
                ext = link[link.rfind("."):].lower()
                if data["type"] == "standing-document":
                    ext = ".html"
                if ext in [".ps"] or (
                    data["type"] == "paper" and
                    link.rfind(".") <= link.rfind("/")
                ):
                    bar.write(f"Link for {name} leads to invalid file!")
                    continue
                elif ext in [".asc"]:
                    ext = ".txt"
                if ext not in [".pdf", ".htm", ".html", ".md", ".txt"]:
                    bar.write(f"Unknown extension {ext} for {name}!")
                    return
            else:
                bar.write(f"No link exist for {name}!")
                continue
            file_name = name + ext
            if not file_name.startswith("SD") and os.path.exists(
                os.path.join(store_dir, file_name)
            ):
                bar.write(f"Skipping {file_name}...")
                continue
            bar.update()
            bar.set_description(f"Downloading {file_name}")
            req = requests.get(link, cookies=cookies, allow_redirects=True)
            if req.status_code != 200:
                bar.write(f"{file_name}: Error: {req}")
                continue
            if ext == ".pdf":
                try:
                    with BytesIO(req.content) as fp:
                        PdfReader(fp)
                except PdfReadError:
                    bar.write(f"{file_name}: Invalid PDF!")
                    continue
            elif ext == ".html" or ext == ".htm":
                soup = BeautifulSoup(req.content, "html.parser")
                if soup.title is not None and "Foswiki login" in soup.title.text:
                    bar.write(f"{file_name}: HTML Require login!")
                    continue
            with open(os.path.join(store_dir, file_name), "wb") as fp:
                for chunk in req.iter_content(chunk_size=128):
                    fp.write(chunk)
            new_files.append(file_name)

    print("\nTotal downloaded files:", len(new_files))
    print("Names:", ", ".join(new_files))


if __name__ == "__main__":
    main()
