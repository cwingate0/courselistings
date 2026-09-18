import json
import re
import pandas as pd
import numpy as np
import os
import sqlite3
from pathlib import Path

async def clean_for_calendar(raw_file: str):
    raw_data = pd.read_json(f"../database/{raw_file}")
    
    raw_data["clean_course"] = raw_data["course"].str.extract(r'([A-Z]{2,}[0-9]{4})')

    unique_courses = pd.Series(raw_data["clean_course"].dropna().unique())
    
    cleaned_df = pd.DataFrame(columns=["title", "terms_offered","course_code","course_num","subj_code","subject","school","description","credits","instructors","corequisites","prerequisites","course_culpa","instructor_culpas"])
    cleaned_df["course_code"] = unique_courses
    cleaned_df["course_num"] = unique_courses.str.extract(r'[A-Z]+([0-9]{4})')
    cleaned_df["subj_code"] = unique_courses.str.extract(r'([A-Z]+)[0-9]{4}')

    cleaned_df["title"] = cleaned_df["course_code"].map(raw_data
                                                         .drop_duplicates(subset="clean_course", keep="first")
                                                         .set_index("clean_course")["title"])
    cleaned_df["subject"] = cleaned_df["course_code"].map(raw_data
                                                         .drop_duplicates(subset="clean_course", keep="first")
                                                         .set_index("clean_course")["subject"])
    cleaned_df["school"] = cleaned_df["course_code"].map(raw_data
                                                         .drop_duplicates(subset="clean_course", keep="first")
                                                         .set_index("clean_course")["school"])
    cleaned_df["description"] = cleaned_df["course_code"].map(raw_data
                                                         .drop_duplicates(subset="clean_course", keep="first")
                                                         .set_index("clean_course")["description"])
    
    cleaned_df["credits"] = cleaned_df["course_code"].map(raw_data
                                                         .drop_duplicates(subset="clean_course", keep="first")
                                                         .set_index("clean_course")["credits"])
    # cleaned_df["terms_offered"] = cleaned_df["terms_offered"].astype(object)
    cleaned_df["terms_offered"] = cleaned_df["course_code"].map(raw_data.groupby("clean_course")["term"].apply(lambda x: list(set(x))))
    cleaned_df["terms_offered"] = cleaned_df["terms_offered"].apply(json.dumps)
    
    cleaned_df["prerequisites"] = cleaned_df["course_code"].map(raw_data
                                                         .drop_duplicates(subset="clean_course", keep="first")
                                                         .set_index("clean_course")["description"]
                                                         .str.findall(r"([A-Z][A-Za-z]{3}[ ]?[A-Z]?[A-Z]?[0-9]{4})")
                                                         .apply(lambda lst: [c[:4] + c[-4:] for c in lst]))
    cleaned_df["prerequisites"] = cleaned_df["prerequisites"].apply(json.dumps)

    cleaned_df["corequisites"] = cleaned_df["course_code"].map(raw_data
                                                         .drop_duplicates(subset="clean_course", keep="first")
                                                         .set_index("clean_course")["description"]
                                                         .str.findall(r"([A-Z][A-Za-z]{3}[ ]?[A-Z]?[A-Z]?[0-9]{4})")
                                                         .apply(lambda lst: [c[:4] + c[-4:] for c in lst]))
    cleaned_df["corequisites"] = cleaned_df["corequisites"].apply(json.dumps)

    cleaned_df["instructors"] = cleaned_df["course_code"].map(raw_data
                                                              .groupby("clean_course")["instructor"]
                                                              .apply(lambda x: [
                                                                  re.sub(r" -(e-mail)?(,)?(homepage)?", "", i).strip()
                                                                  for i in set(x)
                                                                  if re.sub(r" -(e-mail)?(,)?(homepage)?", "", i).strip()
                                                                  ]))
    cleaned_df["instructors"] = cleaned_df["instructors"].apply(json.dumps)

    cleaned_df["course_culpa"] = cleaned_df["course_culpa"].apply(lambda _: "")
    cleaned_df["course_culpa"] = cleaned_df["course_culpa"].apply(json.dumps)
    cleaned_df["instructor_culpas"] = cleaned_df["instructor_culpas"].apply(lambda _: [])
    cleaned_df["instructor_culpas"] = cleaned_df["instructor_culpas"].apply(json.dumps)

    clean = Path(raw_file).name
    clean = clean.removesuffix(".json")

    destpath = f"../backend/cleaned.sqlite3"
    if os.path.exists(destpath):
        os.remove(destpath)
        print(f"Deleted old database: {destpath}")

    adderdatabase = sqlite3.connect(destpath)
    cleaned_df.to_sql(name='api_calendarcourse', con=adderdatabase,if_exists="append", index=False)
    print(f"{raw_file} cleaned into ../backend/cleaned.sqlite3")
    return f"../backend/cleaned.sqlite3"