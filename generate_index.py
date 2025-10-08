#!/usr/bin/env python3

""" Generate SQLite index for WG21 docset """

import os
import glob
import json
import sqlite3


docset_name = "docSet.dsidx"


def main() -> None:
    """ Main function """
    if os.path.exists(docset_name):
        os.remove(docset_name)
    con = sqlite3.connect(docset_name)
    cur = con.cursor()
    cur.execute(
        "CREATE TABLE searchIndex(" +
        "id INTEGER PRIMARY KEY, name TEXT, type TEXT, path TEXT);"
    )
    cur.execute(
        "CREATE UNIQUE INDEX anchor ON searchIndex (name, type, path);"
    )

    index_dict = json.load(open("index.json", "r"))
    result_dict = []
    for file in glob.glob("docs/*"):
        filename = os.path.basename(file)
        name = filename[:filename.find(".")]
        assert name in index_dict, name
        result_dict.append({
            "name": f"{name}: " + index_dict[name]["title"],
            "type": {
                "D": "Directive",
                "N": "Notation",
                "P": "Procedure",
                "S": "Statement"
            }[name[0]],
            "path": filename
        })
    cur.executemany(
        "INSERT OR IGNORE INTO searchIndex(name, type, path) " +
        "VALUES (:name, :type, :path)", result_dict
    )
    con.commit()
    con.close()


if __name__ == "__main__":
    main()
