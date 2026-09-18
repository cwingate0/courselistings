import json
import re
from pathlib import Path

def transform(entry):
    section_number = entry.get("class_id", "").split("-")[-1]

    course_field = entry.get("section_key", "")

    term_code = entry.get("section_key", "")[:5]  # e.g. 20243
    term_map = {"1": "Spring", "2": "Summer", "3": "Fall"}
    term = term_map.get(term_code[-1], "") + term_code[:4]

    instructor = entry.get("instructor") or ""

    call_number = entry.get("call_number", "")
    vergil_link = f"https://vergil.columbia.edu/vergil/class/{term_code}/{call_number}"

    return {
        "title": entry.get("course_title", ""),
        "course": course_field,
        "subject": entry.get("department", ""),
        "school": None,
        "term": term,
        "section_number": section_number,
        "instructor": instructor,
        "description": entry.get("course_descr") or "",
        "enrollment": "",   # you can fill this later
        "credits": entry.get("points", ""),
        "vergil_link": vergil_link,
    }


async def clean_imported(from_file: str, to_file: str):
    with open(f"../database/{from_file}", "r") as f:
        data = json.load(f)

    out = [transform(x) for x in data]

    with open(f"../database/{to_file}", "w") as f:
        json.dump(out, f, indent=4)
    
    return Path(to_file).name