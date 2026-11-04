"""Read allowlisted local settings without executing file contents or logging secrets."""
import os
from pathlib import Path
SETTINGS_FILE = Path(__file__).resolve().parent / '.env'
def settings(path=None):
    values = {}
    file = Path(path) if path is not None else SETTINGS_FILE
    if file.exists():
        for line in file.read_text().splitlines():
            name, sep, value = line.strip().partition('=')
            if sep and name in ('META_API_KEY', 'MODEL_API_KEY', 'META_MODEL'):
                values[name] = value.strip().strip('\"\'')
    for name in ('META_API_KEY', 'MODEL_API_KEY', 'META_MODEL'):
        if os.getenv(name): values[name] = os.environ[name]
    return values
def meta_key():
    values = settings()
    return values.get('META_API_KEY') or values.get('MODEL_API_KEY')
