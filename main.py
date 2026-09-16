from config import load_config, get_recipe_config


def main():
    config = load_config()

    recipe_name = "All_On_AMB_Infotech-Tray"

    recipe_config = get_recipe_config(config, recipe_name)

    if recipe_config is None:
        print(f"No preprocessing configured for recipe: {recipe_name}")
        return

    print(f"Recipe: {recipe_config['recipe_name']}")
    print(f"Device: {recipe_config['general']['device']}")
    print(f"Source root: {recipe_config['general']['source_root']}")
    print(f"Output folder: {recipe_config['output_folder']}")
    print(f"Metadata end: {recipe_config['schema']['metadata_end']}")
    print(f"Feature start: {recipe_config['schema']['feature_start']}")
    print(
        f"Tray: {recipe_config['tray']['rows']} x "
        f"{recipe_config['tray']['columns']}"
    )


if __name__ == "__main__":
    main()