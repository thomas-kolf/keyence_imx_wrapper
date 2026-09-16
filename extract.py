import csv
from collections import defaultdict
from pathlib import Path


def parse_number(value):
    value = value.strip()

    if value == "":
        return None

    return float(value.replace(",", "."))


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
    feature_columns = header[feature_start:]

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

        dmc = metadata.get("AMB_DMC", "").strip()

        if not dmc:
            dmc = schema["missing_dmc"]

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
            "cell_dmc": dmc,
            "physical_position": position,
            "physical_row": physical_row,
            "physical_column": physical_column,
            "measurements": measurements,
        }

        runs[timestamp].append(part)

    return dict(runs)