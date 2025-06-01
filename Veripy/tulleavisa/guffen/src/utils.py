import os

def get_json_files(json_dir="json"):
    """Returnerer liste over alle .json-filer i valgt mappe."""
    path = os.path.join(os.path.dirname(os.path.dirname(__file__)), json_dir)
    return [f for f in os.listdir(path) if f.endswith(".json")]
