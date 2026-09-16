from pathlib import Path
import tomllib


CONFIG_FILE = Path(__file__).with_name("config.toml")


def load_config():
    with open(CONFIG_FILE, "rb") as file:
        return tomllib.load(file)


def get_recipe_config(config, recipe_name):
    recipes = config.get("recipes", {})

    recipe_config = recipes.get(recipe_name)

    if recipe_config is None:
        return None

    if not recipe_config.get("enabled", False):
        return None

    schema = {
        **config["default_schema"],
        **recipe_config.get("schema", {})
    }

    tray = {
        **config["tray"],
        **recipe_config.get("tray", {})
    }

    return {
        "recipe_name": recipe_name,
        "general": config["general"],
        "schema": schema,
        "tray": tray,
        "output_folder": recipe_config["output_folder"]
    }