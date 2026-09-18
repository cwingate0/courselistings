import pandas as pd
import json
from pathlib import Path

async def concat(archive_file: str, combine_with: str, destination: str):
    with open(f"../database/{archive_file}", "r") as f:
        archive = json.load(f)
    with open(f"../database/{combine_with}", "r") as f:
        new = json.load(f)

    archive_df = pd.DataFrame(archive)
    new_df = pd.DataFrame(new)

    combined_json = pd.concat([archive_df, new_df], ignore_index=True)

    output_name = f"../database/{destination}"
    with open(output_name, "w") as json_file:
        json.dump(combined_json.to_dict(orient="records"), json_file, indent=4)
    print(f"{archive_file} and {combine_with} combined into {destination}")
    return Path(destination).name