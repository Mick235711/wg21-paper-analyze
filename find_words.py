#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Find certain words in all the working drafts """

# Library
import os
import json
import sys
import re
import argparse
from pypdf import PdfReader


def main() -> None:
    """ Main function """
    parser = argparse.ArgumentParser()
    parser.add_argument("--update", action="store_true", help="Update for new working drafts")
    args = parser.parse_args()

    # Read indexes
    with open("word_output.json" if os.path.exists("word_output.json") else "wd_index.json", "r") as fp:
        wd_dict = json.load(fp)

    if args.update and os.path.exists("word_output.json"):
        words = list(list(wd_dict.values())[0]["words_count"].keys())
    else:
        words = []
    new_words = [x.strip() for x in sys.stdin]
    words = words + new_words

    # Find words
    orig_dict = json.load(open("wd_index.json", "r"))
    for code in (orig_dict.keys() if args.update else wd_dict.keys()):
        if args.update and code in wd_dict and \
                "words_count" in wd_dict[code] and len(new_words) == 0:
            print(f"Skipping {code}...", flush=True)
            continue
        print(f"Searching {code}...", end="", flush=True)
        reader = PdfReader(f"working-drafts/{code}.pdf")
        total = {word: 0 for word in words}
        total["total"] = 0
        for page in reader.pages:
            text = page.extract_text()
            total["total"] += len(re.findall(r'\w+', text))
            for word in words:
                total[word] += sum(1 for _ in re.finditer(fr'\b{re.escape(word)}\b', text))

        print(" Done! " + ", ".join([f"{k} = {v}" for k, v in total.items()]), flush=True)
        if code not in wd_dict:
            wd_dict[code] = orig_dict[code]
            if "sections" in wd_dict[code]:
                del wd_dict[code]["sections"]
        if "words_count" not in wd_dict[code]:
            wd_dict[code]["words_count"] = {}
        wd_dict[code]["words_count"].update(total)

    # Write to file
    with open("word_output.json", "w") as fp:
        json.dump(wd_dict, fp, indent=4)
        print(f"Write {len(wd_dict)} entries to word_output.json.")


# Call main
if __name__ == "__main__":
    main()
