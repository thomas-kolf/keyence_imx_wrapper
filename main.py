from config import load_config, get_recipe_config
from file_discovery import (
    find_recipe_files,
    find_result_folder,
    find_daily_measurement_csv
)
from extract import extract_measurement_runs
from powerbi_csv import create_powerbi_csvs


def main():
    config = load_config()

    source_root = config["general"]["source_root"]
    computer_name = config["general"]["computer_name"]

    recipe_files = find_recipe_files(source_root)

    if not recipe_files:
        print(f"No .slfx recipe files found in: {source_root}")
        return

    for recipe_path in recipe_files:
        recipe_name = recipe_path.stem

        recipe_config = get_recipe_config(
            config,
            recipe_name
        )

        if recipe_config is None:
            print(
                f"Skipping recipe without preprocessing: "
                f"{recipe_name}"
            )
            continue

        result_folder = find_result_folder(recipe_path)

        if result_folder is None:
            print(
                f"Result folder missing for recipe: "
                f"{recipe_name}"
            )
            continue

        measurement_file = find_daily_measurement_csv(
            result_folder,
            computer_name
        )

        if measurement_file is None:
            print(
                f"No measurement CSV found for today: "
                f"{recipe_name}"
            )
            continue

        print(f"\nProcessing recipe: {recipe_name}")
        print(f"Measurement file: {measurement_file}")

        runs = extract_measurement_runs(
            measurement_file,
            recipe_config
        )

        print(f"Measurement runs found: {len(runs)}")

        for timestamp, parts in runs.items():
            print(
                f"  {timestamp}: "
                f"{len(parts)} positions"
            )

        created_files = create_powerbi_csvs(
            runs,
            recipe_config,
            measurement_file
        )

        print(f"Power BI files created: {len(created_files)}")

        for created_file in created_files:
            print(f"  {created_file}")


if __name__ == "__main__":
    main()