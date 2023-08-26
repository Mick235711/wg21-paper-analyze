#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Get the index file """

# Libraries
import json
import requests


def main() -> None:
    """ Main function """
    req = requests.get("https://wg21.link/index.json")
    json_dict = req.json()
    json_dict_new = {}

    # Add several useful values
    for code, value in json_dict.items():
        digit_index = len(code)
        for index, char in enumerate(code):
            if char.isdigit():
                digit_index = index
                break
        value["category"] = code[:digit_index]
        code_left = code[digit_index:].strip()
        if "R" in code_left:
            r_index = code_left.rfind("R")
            value["number"] = int(code_left[:r_index])
            value["revision"] = int(code_left[r_index + 1:])
        else:
            value["number"] = int(code_left)

        if value["type"] == "paper":
            if "subgroup" in value:
                value["subgroup"] = [x.strip() for x in value["subgroup"].split(",")]

            if "author" in value:
                value["author"] = [x.strip() for x in value["author"].split(",")]
        elif value["type"] == "issue":
            if "section" in value:
                section = value["section"]
                value["section_number"] = section[:section.rfind("[")].strip()
                value["section_stable"] = section[section.rfind("[") + 1:section.rfind("]")].strip()

            if "submitter" in value:
                value["submitter"] = [x.strip() for x in value["submitter"].split(",")]
        elif value["type"] == "editorial":
            title = value["title"]
            if title.startswith("["):
                value["section_stable"] = title[1:title.find("]")].strip()
        elif value["type"] == "standing-document":
            pass
        else:
            assert False, (code, value)

        json_dict_new[code] = value

    # Write to file
    with open("index.json", "w") as fp:
        json.dump(json_dict_new, fp, indent=4)
        print(f"Write {len(json_dict_new)} entries to index.json.")


# Call main
if __name__ == "__main__":
    main()
