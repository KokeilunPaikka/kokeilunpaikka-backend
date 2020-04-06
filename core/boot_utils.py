import os

from dotenv import find_dotenv, load_dotenv


def load_django_settings_module():
    # Load environment variables from .env file
    load_dotenv(dotenv_path=find_dotenv())

    settings_module = os.environ.get('DJANGO_SETTINGS_MODULE', 'core.settings.local')
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", settings_module)
