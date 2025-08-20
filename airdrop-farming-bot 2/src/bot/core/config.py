import os, yaml
from dotenv import load_dotenv
def load_env_config():
    load_dotenv(override=False)
    return {
        "RPC_URL": os.getenv("RPC_URL"),
        "CHAIN_ID": int(os.getenv("CHAIN_ID", "11155111")),
        "PRIVATE_KEY": os.getenv("PRIVATE_KEY"),
        "LOG_LEVEL": os.getenv("LOG_LEVEL", "INFO"),
    }
def load_yaml(path: str):
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)
