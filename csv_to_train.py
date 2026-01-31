import pandas as pd
import json
import os

# ==================================================
# CONFIG
# ==================================================

INPUT_FILE = "clean_data.csv"   # works even if originally called data.csv
OUTPUT_JSONL = "train.jsonl"

# Required logical fields (what we WANT)
REQUIRED_FIELDS = {
    "crop": ["crop", "crop_name", "name_of_crop"],
    "region": ["region", "agro_region"],
    "state": ["state"],
    "district": ["district"],
    "cropping_season": ["cropping_season", "season"],
    "area_acres": ["area_acres", "area", "land_area"],
    "avg_rainfall_mm": ["avg_rainfall_mm", "avg_rainfall_in_mm", "rainfall"],
    "yield_quintal": ["yield_quintal", "yeild_in_quintal", "yield"],
    "soil_type": ["soil_type", "soil"],
}

# ==================================================
# STEP 1: LOAD FILE (CSV OR EXCEL SAFELY)
# ==================================================

def load_file(path):
    if path.lower().endswith(".xlsx"):
        return pd.read_excel(path)
    else:
        return pd.read_csv(
            path,
            encoding="latin1",
            engine="python",
            on_bad_lines="skip"
        )

df = load_file(INPUT_FILE)

# ==================================================
# STEP 2: NORMALIZE COLUMN NAMES
# ==================================================

df.columns = (
    df.columns
    .astype(str)
    .str.strip()
    .str.lower()
    .str.replace(" ", "_")
    .str.replace("(", "")
    .str.replace(")", "")
)

print("\n✅ Found columns:")
for c in df.columns:
    print(" -", c)

# ==================================================
# STEP 3: AUTO-MAP COLUMNS (KEY FIX)
# ==================================================

column_map = {}

for target, aliases in REQUIRED_FIELDS.items():
    for col in df.columns:
        if col in aliases:
            column_map[target] = col
            break

missing = [k for k in REQUIRED_FIELDS if k not in column_map]
if missing:
    raise ValueError(f"\n❌ Missing required columns: {missing}\nCheck your Excel file.")

# Rename columns to standard names
df = df.rename(columns={v: k for k, v in column_map.items()})

print("\n✅ Mapped columns:")
for k, v in column_map.items():
    print(f" {k}  <-  {v}")

# ==================================================
# STEP 4: HANDLE MISSING VALUES
# ==================================================

df = df.fillna({
    "region": "Unknown",
    "state": "Unknown",
    "district": "Unknown",
    "soil_type": "Unknown",
    "avg_rainfall_mm": df["avg_rainfall_mm"].mean(),
    "yield_quintal": df["yield_quintal"].mean(),
})

# ==================================================
# STEP 5: CLEAN TEXT
# ==================================================

for col in df.select_dtypes(include=["object"]).columns:
    df[col] = df[col].astype(str).str.strip().str.title()

# ==================================================
# STEP 6: GENERATE TRAINING OUTPUT
# ==================================================

def generate_output(row):
    if row["yield_quintal"] < 15:
        return (
            f"The yield is low for {row['crop']}. Improve soil fertility, "
            f"optimize irrigation scheduling, and adopt better crop management practices."
        )
    else:
        return (
            f"{row['crop']} is performing well in {row['soil_type']} soil during "
            f"the {row['cropping_season']} season. Continue current practices "
            f"and monitor weather conditions."
        )

# ==================================================
# STEP 7: WRITE JSONL
# ==================================================

with open(OUTPUT_JSONL, "w", encoding="utf-8") as f:
    for _, row in df.iterrows():
        record = {
            "instruction": "Generate farming advice based on crop and environmental data",
            "input": (
                f"Crop: {row['crop']}\n"
                f"Region: {row['region']}\n"
                f"State: {row['state']}\n"
                f"District: {row['district']}\n"
                f"Season: {row['cropping_season']}\n"
                f"Area: {row['area_acres']} acres\n"
                f"Avg rainfall: {row['avg_rainfall_mm']} mm\n"
                f"Soil type: {row['soil_type']}"
            ),
            "output": generate_output(row)
        }
        f.write(json.dumps(record) + "\n")

print("\n🎉 SUCCESS!")
print(f"Generated {len(df)} training samples → {OUTPUT_JSONL}")
