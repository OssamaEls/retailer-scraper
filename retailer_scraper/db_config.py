from pathlib import Path

import yaml


file_path = Path(__file__).parent.parent / 'config.yaml'

with open(file_path) as f:
    config = yaml.safe_load(f)

