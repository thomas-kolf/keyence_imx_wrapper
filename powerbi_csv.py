import csv
from datetime import datetime
from pathlib import Path


OUTPUT_COLUMNS = [
    "Leadframe_DMC",
    "Cell_DMC",
    "DMC_Position",
    "DMC_Row",
    "DMC_Column",
    "Physical_Position",
    "Physical_Row",
    "Physical_Column",
    "Timestamp",
    "Lot",
    "Recipe",
    "Feature",
    "Value",
    "Target",
    "Upper_Tolerance",
    "Lower_Tolerance",
    "Overall_Result",
    "Responsible",
    "Number",
    "Device",
    "Source_File",
]


def create_output_filename(
    timestamp,
    computer_name
):
    timestamp_object = datetime.strptime(
        timestamp,
        "%d.%m.%Y %H:%M:%S"
    )

    date_string = timestamp_object.strftime("%Y%m%d")
    time_string = timestamp_object.strftime("%H%M%S")

    return (
        f"{date_string}_"
        f"{time_string}_"
        f"{computer_name}_PowerBI.csv"
    )


def create_powerbi_rows(
    parts,
    recipe_config,
    source_file
):
    output_rows = []

    device = recipe_config["general"]["device"]
    recipe_name = recipe_config["recipe_name"]

    for part in parts:
        metadata = part["metadata"]

        for measurement in part["measurements"]:
            output_rows.append(
                {
                    "Leadframe_DMC": part["leadframe_dmc"],
                    "Cell_DMC": part["cell_dmc"],
                    "DMC_Position": part["dmc_position"],
                    "DMC_Row": part["dmc_row"],
                    "DMC_Column": part["dmc_column"],

                    "Physical_Position": part["physical_position"],
                    "Physical_Row": part["physical_row"],
                    "Physical_Column": part["physical_column"],

                    "Timestamp": metadata.get("Messzeit", ""),
                    "Lot": metadata.get("Losnummer", ""),
                    "Recipe": recipe_name,

                    "Feature": measurement["feature"],
                    "Value": measurement["value"],
                    "Target": measurement["target"],
                    "Upper_Tolerance": measurement["upper_tolerance"],
                    "Lower_Tolerance": measurement["lower_tolerance"],

                    "Overall_Result": metadata.get("OK/N.i.O.", ""),
                    "Responsible": metadata.get("Verantwortliche/r", ""),
                    "Number": metadata.get("Nummer", ""),

                    "Device": device,
                    "Source_File": Path(source_file).name,
                }
            )

    return output_rows


def write_powerbi_csv(
    output_file,
    rows
):
    with open(
        output_file,
        "w",
        encoding="utf-8-sig",
        newline=""
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=OUTPUT_COLUMNS,
            delimiter=";"
        )

        writer.writeheader()
        writer.writerows(rows)


def create_powerbi_csvs(
    runs,
    recipe_config,
    source_file
):
    source_root = Path(
        recipe_config["general"]["source_root"]
    )

    output_folder = (
        source_root /
        recipe_config["output_folder"]
    )

    output_folder.mkdir(
        parents=True,
        exist_ok=True
    )

    computer_name = recipe_config["general"]["computer_name"]

    created_files = []

    for timestamp, parts in runs.items():

        output_filename = create_output_filename(
            timestamp,
            computer_name
        )

        output_file = (
            output_folder /
            output_filename
        )

        rows = create_powerbi_rows(
            parts,
            recipe_config,
            source_file
        )

        write_powerbi_csv(
            output_file,
            rows
        )

        created_files.append(output_file)

    return created_files