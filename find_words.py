#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Find certain words in all the working drafts """

# Library
import json
import sys
import re
from pypdf import PdfReader


def main() -> None:
    """ Main function """
    # Read indexes
    with open("wd_index.json", "r") as fp:
        wd_dict = json.load(fp)

    if len(sys.argv) == 1:
        print("No words provided!")
        sys.exit(1)
    words = [x.strip() for x in sys.argv[1:]]

    # Find words
    for code in wd_dict.keys():
        print(f"Searching {code}...", end="", flush=True)
        reader = PdfReader(f"working-drafts/{code}.pdf")
        total = {word: 0 for word in words}
        for page in reader.pages:
            text = page.extract_text()
            for word in words:
                total[word] += sum(1 for _ in re.finditer(fr'\b{re.escape(word)}\b', text))

        print(" Done! " + ", ".join([f"{k} = {v}" for k, v in total.items()]), flush=True)
        wd_dict[code]["words_count"] = total

    # Write to file
    with open("word_output.json", "w") as fp:
        json.dump(wd_dict, fp, indent=4)
        print(f"Write {len(wd_dict)} entries to wd_index.json.")


# Call main
if __name__ == "__main__":
    main()
