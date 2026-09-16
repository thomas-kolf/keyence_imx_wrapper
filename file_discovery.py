from datetime import date
from pathlib import Path


def find_recipe_files(source_root):
    source_root = Path(source_root)

    if not source_root.exists():
        raise FileNotFoundError(
            f"Source root does not exist: {source_root}"
        )

    return sorted(source_root.glob("*.slfx"))


def find_result_folder(recipe_path):
    result_folder = recipe_path.with_suffix("")

    if not result_folder.is_dir():
        return None

    return result_folder


def find_daily_measurement_csv(
    result_folder,
    computer_name,
    processing_date=None
):
    if processing_date is None:
        processing_date = date.today()

    date_string = processing_date.strftime("%Y%m%d")

    expected_filename = (
        f"{date_string}{computer_name}.csv"
    )

    measurement_file = result_folder / expected_filename

    if not measurement_file.is_file():
        return None

    return measurement_file