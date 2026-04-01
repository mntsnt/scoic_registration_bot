import logging
import os

BOT_TOKEN = os.environ.get("BOT_TOKEN")

ADMIN_ID = os.environ.get("ADMIN_ID")
if ADMIN_ID is not None:
    try:
        ADMIN_ID = int(ADMIN_ID)
    except ValueError:
        ADMIN_ID = None

ADMIN_IDS_ENV = os.environ.get("ADMIN_IDS")  # comma-separated ids
if ADMIN_IDS_ENV:
    admins = []
    for x in ADMIN_IDS_ENV.split(","):
        x = x.strip()
        if not x:
            continue
        try:
            admins.append(int(x))
        except ValueError:
            logging.warning("Skipping invalid ADMIN_IDS value: %r", x)
    ADMIN_IDS = admins
else:
    ADMIN_IDS = [ADMIN_ID] if ADMIN_ID else []

WORKSHOP_GROUP_LINK = os.environ.get("WORKSHOP_GROUP_LINK") or os.environ.get("GROUP_LINK") or ""