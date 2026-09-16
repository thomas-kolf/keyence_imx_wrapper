# Keyence IMX Adapter – Processing Concept

## Purpose

The Keyence IMX adapter processes product-specific measurement CSV files and transforms them into Power BI-ready CSV files.

The adapter follows the same general architecture as the existing metrology pipeline:

- machine-specific preprocessing inside the IMX adapter
- general file indexing handled separately by `file_indexer.py`
- product-specific preprocessing enabled through configuration
- no unnecessary product-specific logic hardcoded in the Python modules

---

## Source Structure

The staging/source directory contains a recipe file (`.slfx`) and a result folder with the same name without the extension.

Example:

```text
V:\
│
├─ All_On_AMB_Infotech-Tray.slfx
│
├─ All_On_AMB_Infotech-Tray\
│    ├─ 20260806NUD6642N.csv
│    ├─ 20260807NUD6642N.csv
│    └─ ...
│
└─ Powerbi_Details_All_On_AMB_Infotech-Tray\
```

The adapter:

1. finds configured `.slfx` recipe files
2. derives the corresponding result folder from the recipe name
3. selects the relevant daily measurement CSV
4. extracts the individual measurement runs
5. creates one Power BI-ready CSV per measurement run

Example source file:

```text
20260807NUD6642N.csv
```

`NUD6642N` represents the computer name.

---

## Output Granularity

One Power BI CSV is generated per measurement run.

A measurement run is separated based on `Messzeit`.

The output filename follows:

```text
{DMC}_{YYYYMMDD}_{HHMMSS}_{computer_name}_PowerBI.csv
```

Example:

```text
AMB123456_20260807_154538_NUD6642N_PowerBI.csv
```

The timestamp is included so repeated measurements of the same DMC on the same day do not overwrite each other.

The output files are stored in the recipe-specific Power BI directory:

```text
Powerbi_Details_All_On_AMB_Infotech-Tray\
```

Other configured recipes/products receive their own corresponding folder:

```text
Powerbi_Details_<ProductOrRecipeName>\
```

---

## Configuration

Configuration remains TOML-based.

Example:

```toml
[general]
device = "Keyence IMX"
computer_name = "NUD6642N"

[default_schema]
metadata_end = 8
feature_start = 8

target_label = "Sollwert"
upper_tolerance_label = "Obergrenze"
lower_tolerance_label = "Untergrenze"

missing_dmc = "MISSING_DMC"

[tray]
rows = 6
columns = 19
measurement_order = "row_wise"

[recipes."All_On_AMB_Infotech-Tray"]
enabled = true
output_folder = "Powerbi_Details_All_On_AMB_Infotech-Tray"
```

### Default Schema

For the currently known IMX CSV format:

```python
metadata = row[:8]
features = row[8:]
```

This structure is used as the default.

If another product has a different CSV structure, the recipe can override the default without changing the extraction code.

Example:

```toml
[recipes."Another_Product".schema]
metadata_end = 10
feature_start = 10
```

If no recipe-specific schema is defined, `default_schema` is used.

---

## Dynamic Feature Extraction

Measurement features are not hardcoded.

All columns beginning at `feature_start` are treated as measurement features.

The three parameter rows provide the corresponding values for every feature:

- `Sollwert` → Target
- `Obergrenze` → Upper Tolerance
- `Untergrenze` → Lower Tolerance

Therefore, the number of generated rows automatically depends on the number of features in the respective product.

Example:

```text
5 features  → 5 rows per part
12 features → 12 rows per part
20 features → 20 rows per part
```

No measurement feature should be discarded.

---

## Power BI Output Format

The output uses long format.

Each physical part generates one row per measurement feature.

Planned columns:

```text
Cell_DMC
Physical_Position
Physical_Row
Physical_Column
Timestamp
Lot
Recipe
Feature
Value
Target
Upper_Tolerance
Lower_Tolerance
Overall_Result
Responsible
Number
Device
Source_File
```

The complete DMC is preserved unchanged, including suffixes such as `.5`.

If no DMC is available:

```text
Cell_DMC = MISSING_DMC
```

Empty or failed measurements are retained so that physical positions and failed measurements are not lost.

---

## Tray Position Mapping

The current tray contains:

```text
6 rows × 19 columns = 114 positions
```

The CSV field `laufenden Zähler` represents the physical position.

Measurement order is defined as row-wise:

```text
Position 1–19   → Row 1
Position 20–38  → Row 2
Position 39–57  → Row 3
Position 58–76  → Row 4
Position 77–95  → Row 5
Position 96–114 → Row 6
```

Position mapping:

```python
physical_row = ((position - 1) // 19) + 1
physical_column = ((position - 1) % 19) + 1
```

The position remains valid even if measurement values or the DMC are missing.

---

## Planned Adapter Structure

```text
keyence-imx-adapter/
│
├── main.py
├── config.toml
├── file_discovery.py
├── extract.py
└── powerbi_csv.py
```

Responsibilities:

- `main.py` – orchestration of the processing flow
- `file_discovery.py` – discovery of recipe files, result folders and daily CSV files
- `extract.py` – extraction of metadata, runs, features, values and tolerances
- `powerbi_csv.py` – creation of one Power BI-ready CSV per measurement run
- `config.toml` – general settings, default schema, tray configuration and recipe-specific settings

JSON output is currently not required and can be added later if needed.

---

## Processing Flow

```text
Find .slfx recipe
        ↓
Check whether recipe is enabled in config.toml
        ↓
Find corresponding result folder
        ↓
Find relevant daily measurement CSV
        ↓
Read header and tolerance rows
        ↓
Determine features dynamically
        ↓
Read measurement rows
        ↓
Calculate physical Row / Column
        ↓
Group data into measurement runs
        ↓
Transform each part into long format
        ↓
Create one Power BI CSV per measurement run
        ↓
Store in Powerbi_Details_<Recipe>\
```