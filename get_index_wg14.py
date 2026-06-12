#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Get the WG14 index file """

# Libraries
from datetime import date, datetime
from bs4 import BeautifulSoup
import json
import requests


def regularize_date(date_str: str) -> date | None:
    """ Regularize date strings """
    # Formats: 11 Sep 86, 07-Nov-96, 19-Apr-2001, 2005/08/29
    if "/" in date_str:
        if date_str == "2020/03/38":
            date_str = "2020/03/28"

        # try to parse as yyyy/mm/dd
        date_str = date_str.replace("/", "")
        assert date_str.isdigit(), date_str
        return date.fromisoformat(date_str)
    if "-" in date_str:
        # try to parse as dd-mmm-yy[yy]
        if date_str.startswith("00-"):
            print(f"Warning: Correcting {date_str} to first day")
            date_str = "01-" + date_str[3:]
        try:
            return datetime.strptime(date_str, "%d-%b-%y").date()
        except ValueError:
            return datetime.strptime(date_str, "%d-%b-%Y").date()

    # try to parse as dd mmm yy[yy]
    if date_str.startswith("00 "):
        print(f"Warning: Correcting {date_str} to first day")
        date_str = "01 " + date_str[3:]
    try:
        return datetime.strptime(date_str, "%d %b %y").date()
    except ValueError:
        return datetime.strptime(date_str, "%d %b %Y").date()


def main() -> None:
    """ Main function """
    req = requests.get("https://www.open-std.org/jtc1/sc22/wg14/www/wg14_document_log")
    assert req.status_code == 200, req
    soup = BeautifulSoup(req.text, "lxml")
    lines = [x.strip() for x in soup.body.text.splitlines()]
    lines = [x for x in lines if x.startswith("N")]
    links = list(soup.body.find_all("a"))

    # Add several useful values
    json_dict_new = {}
    for line in lines:
        line = line.replace("\t", " ").replace("  ", " ")
        code = line[:line.index(" ")].strip()
        line = line[line.index(" ") + 1:].strip()
        value = {"type": "paper"}
        if line.lower() == "not assigned.":
            continue

        digit_index = len(code)
        for index, char in enumerate(code):
            if char.isdigit():
                digit_index = index
                break
        value["category"] = code[:digit_index]
        code_left = code[digit_index:].strip()
        value["number"] = int(code_left)

        date_index = line.index(" ")
        if line[:date_index].strip().isdigit():
            # Assume dd mmm yy
            date_index = line.index(" ", date_index + 1)
            date_index = line.index(" ", date_index + 1)
        value["date"] = str(regularize_date(line[:date_index].strip()))
        line = line[date_index + 1:].strip()

        # Assume first comma is author
        if "," not in line:
            print(f"Warning: {code} does not have author listed")
            value["title"] = line.strip()
        else:
            first_comma = line.index(",")
            authors = line[:first_comma].strip()
            value["title"] = line[first_comma + 1:].strip()
            if "&" in authors:
                value["author"] = [x.strip() for x in authors.split("&")]
            elif "/" in authors:
                value["author"] = [x.strip() for x in authors.split("/")]
            else:
                value["author"] = [authors]

        # Fetch link
        long_links = [x for x in links if code in x.text]
        if len(long_links) >= 1:
            value["long_link"] = "https://www.open-std.org/jtc1/sc22/wg14/www/" + long_links[0].attrs["href"]

        json_dict_new[code] = value

    # Write to file
    with open("index-wg14.json", "w") as fp:
        json.dump(json_dict_new, fp, indent=4)
        print(f"Write {len(json_dict_new)} entries to index-wg14.json.")


# Call main
if __name__ == "__main__":
    main()
