import os
from pathlib import Path

from dotenv import load_dotenv


def load_env(environment):
    env_path = Path(".") / f".env-{environment}"
    if os.path.isfile(env_path):
        load_dotenv(dotenv_path=env_path, verbose=True)
        return

    print(
        f"env not found: {env_path}. This file is required and must contain your ENC_KEY"
    )
    exit(1)
