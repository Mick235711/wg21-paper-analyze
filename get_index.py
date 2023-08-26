#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Get the index file """

# Libraries
from collections import Counter
from datetime import date, datetime
from typing import Optional
import json
import requests


name_aliases: dict[str, list[str]] = {
    # Working Groups
    "WG14": [],
    "WG21": ["All", "All of WG21"],

    # Stage 2 & 3 Groups
    "CWG": ["Core"],
    "EWG": ["Evolution", "Posterity"],
    "LWG": ["Library"],
    "LEWG": ["Library Evolution", "Library Evoution"],

    # Stage 1 Groups
    "SG1": ["Concurrency", "Concurrency and Parallelism"],
    "SG2": ["Modules"],
    "SG3": ["Filesystem", "File System"],
    "SG4": ["Networking"],
    "SG5": ["Transaction Memory", "Transactional Memory"],
    "SG6": ["Numerics", "Numeric"],
    "SG7": ["Reflection"],
    "SG8": ["Concepts"],
    "SG9": ["Ranges"],
    "SG10": ["Feature Test", "Feature Testing"],
    "SG11": ["Databases", "Database"],
    "SG12": ["Undefined Behavior", "Undefined and Unspecified Behavior"],
    "SG13": ["I/O", "Graphics"],
    "SG14": ["Low Latency"],
    "SG15": ["Tooling"],
    "SG16": ["Unicode", "Text"],
    "SG17": ["EWGI", "EWG Incubator", "Evolution Incubator", "EWGI SG17: EWG Incubator"],
    "SG18": ["LEWGI", "LEWG Incubator", "Library Evolution Incubator",
             "LEWGI SG18: LEWG Incubator"],
    "SG19": ["Machine Learning"],
    "SG20": ["Education"],
    "SG21": ["Contracts"],
    "SG22": ["C/C++ Liaison", "WG14 Liason", "Compatability"],
    "SG23": ["Safety & Security", "Safety and Security"],

    # Others
    "Performance": [],
    "DG": ["Direction Group"]
}


def process_subgroup(subgroup_str: str) -> list[str]:
    """ Process subgroup string """
    # First split out different subgroups
    sg_list: list[str] = []
    for sg in [x.strip() for x in subgroup_str.split(",")]:
        if "/" in sg and "I/O" not in sg.upper() and "C/C++" not in sg.upper():
            sg_list = sg_list + [x.strip() for x in sg.split("/")]
        elif "." in sg:
            sg_list = sg_list + [x.strip() for x in sg.split(".")]
        elif "and" in sg and not sg.upper().startswith("SG1") and not sg.upper().startswith("SG23"):
            # SG1, SG12, SG23 excluded
            sg_list = sg_list + [x.strip() for x in sg.split("and")]
        else:
            sg_list.append(sg)

    # Construct reverse map
    sg_map: dict[str, str] = {}
    for code, aliases in name_aliases.items():
        sg_map[code.lower()] = code
        for alias in aliases:
            sg_map[alias.lower()] = code
            sg_map[f"{code} {alias}".lower()] = code

    # Filter through
    sg_list2 = []
    for sg in sg_list:
        if sg.strip() == "":
            continue
        sg = sg.rstrip("?")
        assert sg.lower() in sg_map, (subgroup_str, sg)
        sg_list2.append(sg_map[sg.lower()])

    return sorted(sg_list2)


def regularize_date(date_str: str) -> Optional[date]:
    """ Regularize date strings """
    if "unknown" == date_str.lower():
        return None
    if "-" in date_str:
        # try to parse as yyyy-mm-dd
        date_str = date_str.replace("-", "")
        assert date_str.isdigit(), date_str
        if int(date_str[4:6]) > 12:
            print(f"Warning: change {date_str} to ", end="")
            date_str = date_str[:4] + "0" + date_str[5:]
            print(date_str)
        return date.fromisoformat(date_str)

    # try to parse as dd mmm yyyy
    date_str = date_str.replace("Sept", "Sep").replace("Sepember", "Sep").replace(",", "")
    if not date_str[0].isdigit():
        try:
            return datetime.strptime(date_str, "%b %Y").date()
        except ValueError:
            return datetime.strptime(date_str, "%B %Y").date()
    try:
        return datetime.strptime(date_str, "%d %b %Y").date()
    except ValueError:
        return datetime.strptime(date_str, "%d %B %Y").date()


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

        if "date" in value:
            result = regularize_date(value["date"])
            if result is None:
                del value["date"]
            else:
                value["date"] = str(result)

        if value["type"] == "paper":
            if "subgroup" in value:
                value["subgroup"] = process_subgroup(value["subgroup"])

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

    # Give an occurrence count
    groups: list[str] = []
    for group_list in [v["subgroup"] for v in json_dict_new.values() if "subgroup" in v]:
        for group in group_list:
            groups.append(group)
    print("Subgroup occurrences:")
    for group, count in Counter(groups).most_common():
        print(f"{group} -> {count} papers")


# Call main
if __name__ == "__main__":
    main()
