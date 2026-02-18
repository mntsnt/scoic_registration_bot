import os

BOT_TOKEN = os.environ["BOT_TOKEN"]
ADMIN_ID = int(os.environ["ADMIN_ID"])
WORKSHOP_PRICE = float(os.environ["WORKSHOP_PRICE"])
DB_FILE = os.environ.get("DB_FILE", "database.db")