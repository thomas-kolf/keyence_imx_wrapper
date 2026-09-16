import csv
import re
from collections import defaultdict
from pathlib import Path


def parse_number(value):
    value = value.strip()

    if value == "":
        return None

    return float(value.replace(",", "."))


def split_cell_dmc(cell_dmc, missing_dmc):
    if cell_dmc == missing_dmc:
        return None, None, None, None

    match = re.fullmatch(r"(.+)(\d)\.(\d)", cell_dmc)

    if match is None:
        return None, None, None, None

    leadframe_dmc = match.group(1)
    dmc_row = int(match.group(2))
    dmc_column = int(match.group(3))
    dmc_position = f"{dmc_row}.{dmc_column}"

    return (
        leadframe_dmc,
        dmc_position,
        dmc_row,
        dmc_column,
    )


def calculate_position(position, tray_config):
    rows = tray_config["rows"]
    columns = tray_config["columns"]
    measurement_order = tray_config["measurement_order"]

    if measurement_order == "row_wise":
        physical_row = ((position - 1) // columns) + 1
        physical_column = ((position - 1) % columns) + 1

    elif measurement_order == "column_wise":
        physical_row = ((position - 1) % rows) + 1
        physical_column = ((position - 1) // rows) + 1

    else:
        raise ValueError(
            f"Unknown measurement order: {measurement_order}"
        )

    return physical_row, physical_column


def read_csv_rows(file_path):
    file_path = Path(file_path)

    try:
        with open(file_path, "r", encoding="utf-8-sig", newline="") as file:
            return list(csv.reader(file, delimiter=";"))

    except UnicodeDecodeError:
        with open(file_path, "r", encoding="cp1252", newline="") as file:
            return list(csv.reader(file, delimiter=";"))


def extract_measurement_runs(file_path, recipe_config):
    rows = read_csv_rows(file_path)

    if len(rows) < 4:
        raise ValueError(
            f"Measurement CSV does not contain enough rows: {file_path}"
        )

    schema = recipe_config["schema"]
    tray_config = recipe_config["tray"]

    metadata_end = schema["metadata_end"]
    feature_start = schema["feature_start"]

    header = rows[0]

    metadata_columns = header[:metadata_end]

    target_row = rows[1]
    upper_row = rows[2]
    lower_row = rows[3]

    if target_row[0] != schema["target_label"]:
        raise ValueError(
            f"Expected '{schema['target_label']}' row"
        )

    if upper_row[0] != schema["upper_tolerance_label"]:
        raise ValueError(
            f"Expected '{schema['upper_tolerance_label']}' row"
        )

    if lower_row[0] != schema["lower_tolerance_label"]:
        raise ValueError(
            f"Expected '{schema['lower_tolerance_label']}' row"
        )

    feature_definitions = []

    for index in range(feature_start, len(header)):
        feature_definitions.append(
            {
                "name": header[index],
                "target": parse_number(target_row[index]),
                "upper_tolerance": parse_number(upper_row[index]),
                "lower_tolerance": parse_number(lower_row[index]),
            }
        )

    runs = defaultdict(list)

    for row in rows[4:]:
        if not row:
            continue

        metadata = {}

        for index, column_name in enumerate(metadata_columns):
            metadata[column_name] = row[index].strip()

        timestamp = metadata.get("Messzeit", "")

        if not timestamp:
            continue

        position_text = metadata.get("laufenden Zähler", "")

        if not position_text:
            continue

        position = int(position_text)

        physical_row, physical_column = calculate_position(
            position,
            tray_config
        )

        cell_dmc = metadata.get("AMB_DMC", "").strip()

        if not cell_dmc:
            cell_dmc = schema["missing_dmc"]

        (
            leadframe_dmc,
            dmc_position,
            dmc_row,
            dmc_column,
        ) = split_cell_dmc(
            cell_dmc,
            schema["missing_dmc"]
        )

        measurements = []

        for index, feature in enumerate(
            feature_definitions,
            start=feature_start
        ):
            value = None

            if index < len(row):
                value = parse_number(row[index])

            measurements.append(
                {
                    "feature": feature["name"],
                    "value": value,
                    "target": feature["target"],
                    "upper_tolerance": feature["upper_tolerance"],
                    "lower_tolerance": feature["lower_tolerance"],
                }
            )

        part = {
            "metadata": metadata,

            "leadframe_dmc": leadframe_dmc,
            "cell_dmc": cell_dmc,

            "dmc_position": dmc_position,
            "dmc_row": dmc_row,
            "dmc_column": dmc_column,

            "physical_position": position,
            "physical_row": physical_row,
            "physical_column": physical_column,

            "measurements": measurements,
        }

        runs[timestamp].append(part)

    return dict(runs)