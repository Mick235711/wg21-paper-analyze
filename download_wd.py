#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Download all the working drafts """

# Library
import os
import json
import requests


def main() -> None:
    """ Main function """
    json_dict = json.load(open("index.json", "r"))
    wd_dict = {}
    for code, value in json_dict.items():
        if ("Working Draft, Standard for Programming Language C++" in value["title"] or
            "Working Draft, Programming Languages -- C++" in value["title"] or
            "Working Draft, Programming Languages \u2014 C++" in value["title"]) and not \
                "Editor's Report" in value["title"]:
            wd_dict[code] = value

    total_len = len(wd_dict)
    i = 1
    for code, value in wd_dict.items():
        print(f"[{i:>{len(str(total_len))}}/{total_len}] Downloading {code}...", end="", flush=True)
        i += 1
        if os.path.exists(f"working-drafts/{code}.pdf"):
            print(" Downloaded", flush=True)
            continue
        req = requests.get(value["long_link"], allow_redirects=True)
        if req.status_code != 200:
            print(" Failed!", flush=True)
            continue
        with open(f"working-drafts/{code}.pdf", "wb") as fp:
            fp.write(req.content)
        print(" Done!", flush=True)


# Call main
if __name__ == "__main__":
    main()
