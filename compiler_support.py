#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Analyze a compiler support page on cppreference """

# Libraries
from typing import Any
import requests
from bs4 import BeautifulSoup


class Support:
    """ Represents a compiler support status """

    # Support entry: version, is_partial
    def __init__(self, vendor: str, support: list[tuple[str, bool]]) -> None:
        """ Constructor """
        self.vendor = vendor
        self.support = support

    def __repr__(self) -> str:
        """ String representation """
        return f"<{self.vendor} [" + ", ".join(
            version + (" <partial>" if is_partial else "")
            for version, is_partial in self.support
        ) + "]>"

    def empty(self) -> bool:
        """ Return true if no support """
        return len(self.support) == 0


class Feature:
    """ Represents a feature """

    def __init__(self, name: str, papers: list[str],
                 support: dict[str, Support]) -> None:
        """ Constructor """
        self.name = name
        self.papers = papers
        self.support = support

    def __repr__(self) -> str:
        """ String representation """
        return f"{self.name} (" + ", ".join(self.papers) + "): " + ", ".join(
            repr(s)[1:-1] for s in self.support.values() if not s.empty()
        )


class FeatureTable:
    """ Represents a feature table """

    def __init__(self, title: str, vendors: list[str],
                 features: list[Feature]) -> None:
        """ Constructor """
        self.title = title
        self.vendors = vendors
        self.features = features

    def __repr__(self) -> str:
        """ String representation """
        return f"{self.title} (" + ", ".join(self.vendors) + ")\n" + "\n".join(
            repr(f) for f in self.features
        )

    def support_score(self, vendor: str,
                      max_version: str | None = None) -> float:
        """ Calculate the support score """
        score = 0.0
        for feature in self.features:
            support = feature.support
            if vendor not in support:
                continue
            inner = support[vendor].support
            score += calculate_score(inner, max_version)
        return score / len(self.features)


def version_tuple(version: str) -> list[int]:
    """ Return the version tuple for a string, like 14.0.0 """
    version = version.strip()
    if version.startswith("Update"):
        version = version[6:].strip()
    if version.endswith(")"):
        index = version.rfind("(")
        return version_tuple(version[:index]) +\
            version_tuple(version[index + 1:-1])
    return [int(x.strip()) for x in version.split(".")]


def calculate_score(
    support: list[tuple[str, bool]], max_version: str | None = None
) -> float:
    """ Calculate support score for a single vendor """
    if len(support) == 0:
        return 0.0
    if support[0][0] in ["N/A", "Yes"]:
        assert len(support) == 1, support
        return 0.5 if support[0][1] else 1.0

    max_vt = None if max_version is None else version_tuple(max_version)
    prev_support = 0
    for version, _ in support:
        vt = version_tuple(version)
        if max_vt is None or vt <= max_vt:
            prev_support += 1
    total_support = len(support)
    if all(x[1] for x in support):
        total_support += 1
    return prev_support / total_support


def analyze_support(vendor: str, cell: list[str]) -> Support:
    """ Analyze a single cell of support """
    cell = [x.strip().rstrip("*").strip() for x in cell if x.strip() != ""]
    cell = [x.replace("yes", "Yes") for x in cell]
    if len(cell) == 0:
        return Support(vendor, [])
    if cell == ["partial"]:
        return Support(vendor, [("Yes", True)])

    final_partial = cell[-1].endswith("partial)")
    if cell[-1] == ")" and cell[-2] == "partial":
        final_partial = True
    new_cell: list[str] = []
    for single in cell:
        if single.endswith(")") or "(" in single:
            single = single[:single.rfind("(")].strip()
        if single == "" or single == "partial":
            continue
        new_cell.append(single)
    support: list[tuple[str, bool]] = []
    for i, single in enumerate(new_cell):
        support.append((single, i != len(new_cell) - 1 or final_partial))
    return Support(vendor, support)


def analyze_table(title: str, table: Any) -> FeatureTable:
    """ Analyze a single feature table """
    rows = table.find_all("tr")[:-1]
    table_head, rows = rows[0], rows[1:]

    # Parse table head
    head_cols = table_head.find_all("th")
    vendors = [
        [
            s.strip() for s in c.strings if s.strip() != ""
        ][0].rstrip("*").strip()
        for c in head_cols[2:-1]
    ]

    # Main loop
    features: list[Feature] = []
    for row in rows:
        cells = row.find_all("td")
        name = "".join(list(cells[0].strings)).strip().replace("\n", " ")
        papers = [s.strip() for s in cells[1].strings if s.strip() != ""]
        supports: dict[str, Support] = {}
        for vendor, cell in zip(vendors, cells[2:]):
            support = analyze_support(vendor, list(cell.strings))
            supports[vendor] = support
        features.append(Feature(name, papers, supports))

    return FeatureTable(title, vendors, features)


def analyze_web(url: str) -> tuple[FeatureTable, FeatureTable]:
    """ Analyze and return the language and library feature table """
    req = requests.get(url)
    soup = BeautifulSoup(req.text, "lxml")
    compiler = soup.find("table", class_="t-compiler-support-top")
    library = soup.find("table", class_="t-standard-library-support-top")
    c_title, l_title = [
        list(x.strings)[-1].strip()
        for x in compiler.parent.find_all("h3")  # type: ignore
    ]
    return analyze_table(c_title, compiler), analyze_table(l_title, library)


def get_support_score_dict(table: FeatureTable) -> dict[str, float]:
    """ Get sorted support score dict """
    return dict(sorted(
        [(v, table.support_score(v)) for v in table.vendors],
        key=lambda x: x[1], reverse=True
    ))


def main() -> None:
    """ Main function """
    compiler, library = analyze_web(
        "https://en.cppreference.com/w/cpp/compiler_support/26"
    )

    print(compiler)
    print("\nCompiler Support Ranking:")
    print("\n".join(
        f"{k}: {v:.3f}" for k, v in get_support_score_dict(compiler).items()))

    print()
    print(library)
    print("\nLibrary Support Ranking:")
    print("\n".join(
        f"{k}: {v:.3f}" for k, v in get_support_score_dict(library).items()))


# Call main
if __name__ == "__main__":
    main()
