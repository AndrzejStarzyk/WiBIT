from typing import Union, List, Tuple, Pattern, Match
import re
import pl_core_news_md
from spacy.matcher import Matcher

from recommending_v3.day_parameters import ScheduleParameters

period_patterns = [[
        {"POS": {"IN": ["ADJ", "NUM"]},  "OP": "?"},
        {"POS": "NOUN", "ENT_TYPE": "date", "LOWER": {"REGEX": "(?:stycz|lut|mar|kwie|maj|czerw|lip|sierp|wrze|październik|listopad|grud)[a-z]*"}},
        {"LOWER": {"IN": ["-", "do", "i"]}},
        {"POS": {"IN": ["ADJ", "NUM"]}, "OP": "?"},
        {"POS": "NOUN", "LOWER": {"REGEX": "(?:stycz|lut|mar|kwie|maj|czerw|lip|sierp|wrze|październik|listopad|grud)[a-z]*"}}
], [
        {"POS": {"IN": ["ADJ", "NUM"]}, "ENT_TYPE": "date"},
        {"POS": "NOUN",  "OP": "?", "LOWER": {"REGEX": "(?:stycz|lut|mar|kwie|maj|czerw|lip|sierp|wrze|październik|listopad|grud)[a-z]*"}},
        {"LOWER": {"IN": ["-", "do", "i"]}},
        {"POS": {"IN": ["ADJ", "NUM"]}},
        {"POS": "NOUN",  "OP": "?", "LOWER": {"REGEX": "(?:stycz|lut|mar|kwie|maj|czerw|lip|sierp|wrze|październik|listopad|grud)[a-z]*"}}
]]

date_patterns = [[
    {"ENT_TYPE": "date", "OP": "?"},
    {"POS": "NOUN", "ENT_TYPE": "date", "LOWER": {"REGEX": "(?:stycz|lut|mar|kwie|maj|czerw|lip|sierp|wrze|październik|listopad|grud)[a-z]*"}}
]]

period_regex: Pattern[str] = re.compile(
    "^([0-9]{1,2})?\s*([a-zA-Z]+)?\s*(?:-| do | i )?\s*([0-9]{1,2})?\s*([a-zA-Z]+)?$")

month_subjects = ["stycz", "lut", "mar", "kwie", "maj", "czerw", "lip", "sierp", "wrze", "październik", "listopad",
                  "grud"]
month_regexes = [re.compile(f"^{subject}\w*$") for subject in month_subjects]

date_regex = re.compile("^([0-9]{1,2}?)?\s*(\w+)$")


def parse_date_text(text: str) -> ScheduleParameters:
    text = " " + text + " "
    day_parameters = ScheduleParameters()
    nlp = pl_core_news_md.load()
    matcher = Matcher(nlp.vocab)
    matcher.add("PeriodPhrase", period_patterns)
    doc = nlp(text)

    matches = matcher(doc)
    print(matches)
    for _, start, end in matches:
        print(doc[start:end])
    continue_matching = True
    if len(matches) > 0:
        unique_matches = only_unique_matches(matches)
        for start, end in unique_matches:
            print(doc[start:end])
        if len(unique_matches) == 1:
            continue_matching = parse_period_text(str(doc[unique_matches[0][0]:unique_matches[0][1]]), day_parameters)
    if continue_matching:
        date_matcher = Matcher(nlp.vocab)
        date_matcher.add("DatePhrase", date_patterns)
        matches = date_matcher(doc)

        matches = only_unique_matches(matches)
        for start, end in matches:
            print(doc[start:end])

        if len(matches) == 0:
            pass
        elif len(matches) == 1:
            parse_date(str(doc[matches[0][0]:matches[0][1]]), True, day_parameters)
            parse_date(str(doc[matches[0][0]:matches[0][1]]), False, day_parameters)
        elif len(matches) == 2:
            parse_date(str(doc[matches[0][0]:matches[0][1]]), True, day_parameters)
            parse_date(str(doc[matches[1][0]:matches[1][1]]), False, day_parameters)
        else:
            parse_date(str(doc[matches[0][0]:matches[0][1]]), True, day_parameters)
            parse_date(str(doc[matches[-1][0]:matches[-1][1]]), False, day_parameters)

    day_parameters.assume_missing_info()
    return day_parameters


def only_unique_matches(matches: List[Tuple[int, int, int]]) -> List[Tuple[int, int]]:
    if len(matches) == 0:
        return []
    curr_start = matches[0][1]
    curr_end = matches[0][2]
    res = []

    matches.sort(key=lambda x: x[2])
    matches.sort(key=lambda x: x[1])
    print(matches)
    for match in matches[1:]:
        if match[1] == curr_start and curr_end < match[2]:
            curr_start = match[1]
            curr_end = match[2]
        elif match[1] < curr_start and match[2] == curr_end:
            curr_start = match[1]
            curr_end = match[2]
        elif curr_start < match[1] and curr_end < match[2]:
            res.append((curr_start, curr_end))
            curr_start = match[1]
            curr_end = match[2]

    res.append((curr_start, curr_end))
    return res


def parse_period_text(text: str, day_parameters: ScheduleParameters) -> bool:
    match = period_regex.match(text)
    if match is None:
        return True
    print("x ", match.group(1), match.group(2), match.group(3), match.group(4))
    if match.group(1) is not None:
        day_parameters.start_day = int(match.group(1))
    if match.group(2) is not None:
        day_parameters.start_month = recognise_month(match.group(2))
    if match.group(3) is not None:
        day_parameters.end_day = int(match.group(3))
    if match.group(4) is not None:
        day_parameters.end_month = recognise_month(match.group(4))

    if match.group(1) is None and match.group(2) is None and match.group(3) is None and match.group(4) is None:
        return True
    return False


def parse_date(text: str, is_start_date: bool, day_parameters: ScheduleParameters):
    match = date_regex.match(text)
    if match is None:
        return
    print(match.group(1), match.group(2))
    if is_start_date:
        if match.group(1) is not None:
            day_parameters.start_day = int(match.group(1))
        if match.group(2) is not None:
            day_parameters.start_month = recognise_month(match.group(2))
    else:
        if match.group(1) is not None:
            day_parameters.end_day = int(match.group(1))
        if match.group(2) is not None:
            day_parameters.end_month = recognise_month(match.group(2))


def recognise_month(text: str) -> Union[None, int]:
    for i in range(len(month_regexes)):
        match = month_regexes[i].match(text)
        if match is not None:
            return i + 1
    return None


if __name__ == '__main__':
    sp = parse_date_text("lipca i sierpnia rok 2025")
    print(sp.start_date, sp.end_date)
