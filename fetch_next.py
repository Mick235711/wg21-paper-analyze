#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Fetch next versions """

# Library
import json
import requests
from functools import partial
from io import BytesIO
from tqdm import tqdm
from bs4 import BeautifulSoup
from pypdf import PdfReader


def fetch_single(json_dict: dict[str, dict], keys: tuple[str, str | None]) -> str:
    """ Fetch single document """
    key, orig_key = keys
    req = requests.get(f"https://wg21.link/{key}", allow_redirects=True)
    if req.status_code == 200:
        if orig_key is None:
            if "html" in req.headers["content-type"]:
                html = BeautifulSoup(req.text, "lxml")
                if html.title is None:
                    title = ""
                else:
                    title = " " + html.title.text.replace("\n", " ")
            elif "pdf" in req.headers["content-type"]:
                reader = PdfReader(BytesIO(req.content))
                if reader.metadata.title is not None:
                    title = " " + reader.metadata.title.replace("\n", " ")
                else:
                    title = " " + reader.pages[0].extract_text(0).split("\n")[0].strip()
            else:
                title = ""
            tqdm.write(f"New paper available: {key}{title}")
        else:
            tqdm.write(f"Next revision {key} available for {orig_key}: " + json_dict[orig_key]["title"])
    return key


def main() -> None:
    """ Main function """
    json_dict = json.load(open("index.json", "r"))
    last_version = {}
    max_num = -1
    for key, data in json_dict.items():
        if data["category"] != "P" or "R" not in key or "04116" in key:
            continue
        basic = key[:key.find("R")]
        revision = int(key[key.find("R") + 1:])
        if basic not in last_version or revision > last_version[basic]:
            last_version[basic] = revision
        num = int(basic[1:])
        if num != 4000 and num > max_num:
            max_num = num

    worker = []
    # for basic, revision in last_version.items():
    #     worker.append((f"{basic}R{revision + 1}", f"{basic}R{revision}"))
    for new_num in range(max_num + 1, max_num + 100):
        worker.append((f"P{new_num}R0", None))

    with tqdm(total=len(worker)) as bar:
        for result in map(partial(fetch_single, json_dict), worker):
            bar.set_description(result)
            bar.update()


# Call main
if __name__ == "__main__":
    from fetch_next import fetch_single
    main()
