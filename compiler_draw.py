#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Draw computer support graph """

# Libraries
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from compiler_support import analyze_web


CPP_VERSIONS: dict[str, tuple[str | None, str]] = {
    "17": ("2017-03-21", "solid"),
    "20": ("2020-04-01", "dashed"),
    "23": ("2023-05-10", "dashdot"),
    "26": ("2024-10-16", "dotted")
}
COMPILER_VERSIONS = {
    "gcc": {
        "compiler_name": "GCC",
        "library_name": "GCC libstdc++",
        "versions": {
            "5.1": "2015-04-22",
            "6.1": "2016-04-27",
            "7.1": "2017-05-02",
            "8.1": "2018-05-02",
            "9.1": "2019-05-03",
            "10.1": "2020-05-07",
            "11.1": "2021-04-27",
            "12.1": "2022-05-06",
            "13.1": "2023-04-26",
            "14.1": "2024-05-06",
            "15.1": datetime.now().date().isoformat()
        },
        "color": "tab:blue"
    },
    "clang": {
        "compiler_name": "Clang",
        "library_name": "Clang libc++",
        "versions": {
            "3.5.1": "2015-01-20",
            "3.6.0": "2015-02-27",
            "3.7.0": "2015-09-01",
            "3.8.0": "2016-03-08",
            "3.9.0": "2016-09-02",
            "4.0.0": "2017-03-13",
            "5.0.0": "2017-09-07",
            "6.0.0": "2018-03-08",
            "7.0.0": "2018-09-19",
            "8.0.0": "2019-03-20",
            "9.0.0": "2019-09-19",
            "10.0.0": "2020-03-24",
            "11.0.0": "2020-10-12",
            "12.0.0": "2021-04-14",
            "13.0.0": "2021-10-04",
            "14.0.0": "2022-03-25",
            "15.0.0": "2022-09-06",
            "16.0.0": "2023-03-17",
            "17.0.1": "2023-09-06",
            "18.1.0": "2024-03-05",
            "19.1.0": "2024-09-17",
            "20.0.0": datetime.now().date().isoformat()
        },
        "color": "tab:orange"
    },
    "msvc": {
        "compiler_name": "MSVC",
        "library_name": "MSVC STL",
        "versions": {
            "19.0": "2015-07-20",
            "19.10": "2017-03-07",
            "19.11": "2017-08-29",
            "19.12": "2017-12-14",
            "19.13": "2018-03-05",
            "19.14": "2018-05-08",
            "19.16": "2018-11-15",
            "19.20": "2019-04-02",
            "19.21": "2019-06-04",
            "19.22": "2019-08-20",
            "19.23": "2019-10-01",
            "19.24": "2019-12-03",
            "19.25": "2020-03-24",
            "19.26": "2020-06-09",
            "19.27": "2020-08-05",
            "19.28": "2020-11-12",
            "19.29": "2021-08-25",
            "19.30": "2021-11-16",
            "19.31": "2022-03-31",
            "19.32": "2022-05-24",
            "19.33": "2022-09-13",
            "19.34": "2022-11-15",
            "19.35": "2023-02-21",
            "19.36": "2023-05-22",
            "19.37": "2023-08-08",
            "19.38": "2023-11-14",
            "19.39": "2024-02-21",
            "19.40": "2024-05-29",
            "19.41": "2024-08-20",
            "20": datetime.now().date().isoformat()
        },
        "color": "tab:green"
    }
}


def get_url(version: str) -> str:
    """ Return cppreference URL """
    return f"https://en.cppreference.com/w/cpp/compiler_support/{version}"


def main() -> None:
    """ Main function """
    plt.figure(figsize=(18, 10))
    ax1 = plt.subplot(211)
    ax2 = plt.subplot(212)

    for ax, using in zip([ax1, ax2], ["Compiler", "Library"]):
        for cpp_version, (cpp_date_str, cpp_style) in CPP_VERSIONS.items():
            compiler, library = analyze_web(get_url(cpp_version))
            if using == "Compiler":
                table = compiler
                using_key = "compiler_name"
            else:
                table = library
                using_key = "library_name"

            if cpp_date_str is not None:
                cpp_date = datetime.fromisoformat(cpp_date_str)
                ax.axvline(cpp_date,
                           linestyle=cpp_style, color="tab:red")
                ax.annotate(
                    f"C++{cpp_version} Final WD"
                    if cpp_version < "26" else "Current",
                    (cpp_date, 1), annotation_clip=False,
                    xytext=(-3, 0), textcoords="offset points",
                    horizontalalignment="center",
                    verticalalignment="bottom"
                )

            for vendor_key, vendor_data in COMPILER_VERSIONS.items():
                vendor = vendor_data[using_key]
                draw_data: list[tuple[datetime, float]] = []
                for version, version_date in vendor_data["versions"].items():
                    draw_data.append((
                        datetime.fromisoformat(version_date),
                        table.support_score(vendor, version)
                    ))
                ax.plot([x[0] for x in draw_data],
                        [100 * x[1] for x in draw_data],
                        color=vendor_data["color"], linestyle=cpp_style)

        ax.margins(x=0)
        ax.set_xlabel("Release Date")
        ax.set_ylabel("Supported Feature %")
        ax.set_ylim(0, 100)
        ax.set_title(using)

    # Calculate legends
    legend_lines = []
    legend_labels = []
    for cpp_version, (_, cpp_style) in CPP_VERSIONS.items():
        legend_lines.append(
            Line2D([0], [0], color="black", linestyle=cpp_style)
        )
        legend_labels.append(f"C++{cpp_version}")
    for vendor_key, vendor_data in COMPILER_VERSIONS.items():
        legend_lines.append(
            Line2D([0], [0], color=vendor_data["color"])
        )
        legend_labels.append(vendor_data["compiler_name"])
    plt.figlegend(legend_lines, legend_labels, loc="upper left")
    plt.tight_layout()
    plt.show()


# Call main
if __name__ == "__main__":
    main()
