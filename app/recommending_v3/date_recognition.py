from typing import Union
import re
import pl_core_news_md
from spacy.matcher import Matcher

from recommending_v3.day_parameters import ScheduleParameters

patterns = [[
    {"ENT_TYPE": "date"},
    {"LOWER": "-", "OP": "?"},
    {"POS": 'ADJ', "OP": "?"},
    {"POS": "NOUN", "ENT_TYPE": "date"}
],
    [
        {"POS": 'ADJ', "ENT_TYPE": "date"},
        {"LOWER": "do", "OP": "?"},
        {"POS": 'ADJ', "OP": "?"},
        {"POS": "NOUN", "ENT_TYPE": "date"}
    ]
]

period_regex = re.compile("^([0-9]{1,2})\s*(\w+)?\s*(?:-|(?:do))\s*([0-9]{1,2})\s*(\w+)?$")

month_subjects = ["stycz", "lut", "mar", "kwie", "maj", "czerw", "lip", "sierp", "wrze", "październik", "listopad",
                  "grud"]
month_regexes = [re.compile(f"^{subject}\w*$") for subject in month_subjects]


def parse_date_text(text: str):
    print(text)
    day_parameters = ScheduleParameters()
    nlp = pl_core_news_md.load()
    matcher = Matcher(nlp.vocab)
    matcher.add("PeriodPhrase", patterns)
    doc = nlp(text)

    matches = matcher(doc)

    if len(matches) == 1:
        parse_period_text(str(doc[matches[0][1]:matches[0][2]]), day_parameters)

    day_parameters.assume_missing_info()
    return day_parameters


def parse_period_text(text: str, day_parameters: ScheduleParameters):
    print(text)
    match = period_regex.match(text)

    if match.group(1) is not None:
        day_parameters.start_day = int(match.group(1))
    if match.group(2) is not None:
        day_parameters.start_month = recognise_month(match.group(2))
    if match.group(3) is not None:
        day_parameters.end_day = int(match.group(3))
    if match.group(4) is not None:
        day_parameters.end_month = recognise_month(match.group(4))

    print(day_parameters.start_day)
    print(day_parameters.start_month)
    print(day_parameters.end_day)
    print(day_parameters.end_month)


def recognise_month(text: str) -> Union[None, int]:
    for i in range(len(month_regexes)):
        match = month_regexes[i].match(text)
        if match is not None:
            return i+1
    return None


if __name__ == '__main__':
    parse_period_text("29 do 6 grudnia", ScheduleParameters())
