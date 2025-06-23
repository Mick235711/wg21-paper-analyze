from dataclasses import dataclass
from datetime import date
from typing import Any
import json


@dataclass
class Meeting:
    start_date: date
    end_date: date
    location: str
    sponsor: list[str]

    def to_json_object(self) -> dict[str, Any]:
        return {
            "start_date": self.start_date.isoformat(),
            "end_date": self.end_date.isoformat(),
            "location": self.location,
            "sponsor": self.sponsor,
        }


def main() -> None:
    locations = []
    with open("meeting-locations.txt", "r") as fp:
        for line in fp:
            if line.startswith("(virtual)"):
                location = "(virtual)"
                line = line.removeprefix("(virtual)").strip()
                index1 = line.find(":")
                sponsor = "(none)"
            else:
                index1 = line.find(":")
                index2 = line.find(";", index1 + 1)
                location = line[index1 + 1:index2].strip()
                sponsor = [
                    x.strip() for x in line[index2 + 1:].strip().split(",")
                ]
            date_str = line[:index1].strip()
            if "to" in date_str:
                start_date_str, end_date_str = date_str.split(" to ")
                start_date = date.fromisoformat(start_date_str.strip())
                if "-" in end_date_str:
                    end_date = date.fromisoformat(
                        f"{start_date.year}-" + end_date_str.strip())
                else:
                    end_date = date.fromisoformat(
                        start_date_str.strip()[:-2] + end_date_str.strip())
            else:
                if len(date_str) == 7:
                    date_str += "-01"
                start_date = end_date = date.fromisoformat(date_str.strip())
            locations.append(Meeting(start_date, end_date, location, sponsor))

    with open("meeting-locations.json", "w") as fp:
        json.dump(
            [meeting.to_json_object() for meeting in locations],
            fp, indent=4, ensure_ascii=False
        )


if __name__ == "__main__":
    main()
