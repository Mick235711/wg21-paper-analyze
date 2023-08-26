#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Analyze all the working drafts """

# Library
from glob import glob
import json
from pypdf import PdfReader
from get_index import regularize_date


def main() -> None:
    """ Main function """
    wd_dict = {}
    file_list = glob("working-drafts/*.pdf")
    for i, file in enumerate(sorted(file_list)):
        print(f"[{i + 1:>{len(str(len(file_list)))}}/{len(file_list)}] Parsing {file}...",
              end="", flush=True)
        reader = PdfReader(file)
        draft_name = file[file.find("/") + 1:file.rfind(".")].strip()
        pages = len(reader.pages)

        # Basic properties
        prop = {
            "name": draft_name,
            "pages": pages
        }

        # Fetch date
        front_text = "".join(reader.pages[0].extract_text().strip().split()).lower()
        if "date:" in front_text:
            front_text = front_text[front_text.find("date:") + 5:]
        else:
            front_text = front_text[front_text.find("edition") + 7:]
        index = 0
        while front_text[index].isdigit() or front_text[index] == "-":
            index += 1
        try:
            date = regularize_date(front_text[:index])
        except IndexError:
            while not (front_text[index:].startswith("revise") or
                       front_text[index:].startswith("reply")):
                index += 1
            date_str = front_text[:index]
            index = 0
            while not date_str[index].isdigit():
                index += 1
            index2 = date_str.find(",", index)
            date = regularize_date(" ".join([date_str[index:index2],
                                             date_str[:index].capitalize(), date_str[index2 + 1:]]))
        assert date is not None, front_text[:index]
        prop["date"] = str(date)

        if len(reader.outline) == 0:
            wd_dict[draft_name] = prop
            print(" No Outline", flush=True)
            continue

        # Fetch page count of core, library and annex
        # Core/Library separation is the "Library introduction" clause
        # Library/Annex separation is "A Grammar summary"
        start_page = -1
        lib_page = -1
        annex_page = -1
        end_page = -1
        for outline in (reader.outline if len(reader.outline) > 10 else reader.outline[-1]):
            if isinstance(outline, list):
                continue
            assert outline.title is not None, outline
            if outline.title[0].isdigit() and start_page == -1:
                start_page = reader.get_destination_page_number(outline)
            if "library intro" in outline.title.lower() and lib_page == -1:
                lib_page = reader.get_destination_page_number(outline)
            if start_page != -1 and not outline.title[0].isdigit() and annex_page == -1:
                annex_page = reader.get_destination_page_number(outline)
            if "bibliography" in outline.title.lower() and end_page == -1:
                end_page = reader.get_destination_page_number(outline)
            if outline.title.lower().startswith("cross") and end_page == -1:
                end_page = reader.get_destination_page_number(outline)
            if outline.title.lower().startswith("index") and end_page == -1:
                end_page = reader.get_destination_page_number(outline)
        if end_page == -1:
            end_page = pages
        assert 0 < start_page < lib_page < annex_page < end_page <= pages,\
            [start_page, lib_page, annex_page, end_page]
        prop["core"] = lib_page - start_page
        prop["library"] = annex_page - lib_page
        prop["annex"] = end_page - annex_page

        wd_dict[draft_name] = prop
        print(" Done!", flush=True)

    # Write to file
    with open("wd_index.json", "w") as fp:
        json.dump(wd_dict, fp, indent=4)
        print(f"Write {len(wd_dict)} entries to wd_index.json.")


# Call main
if __name__ == "__main__":
    main()
