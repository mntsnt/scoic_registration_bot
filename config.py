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

# Full admins (can approve/disapprove and manage all features)
FULL_ADMIN_IDS_ENV = os.environ.get("FULL_ADMIN_IDS")  # comma-separated ids
if FULL_ADMIN_IDS_ENV:
    full_admins = []
    for x in FULL_ADMIN_IDS_ENV.split(","):
        x = x.strip()
        if not x:
            continue
        try:
            full_admins.append(int(x))
        except ValueError:
            logging.warning("Skipping invalid FULL_ADMIN_IDS value: %r", x)
    FULL_ADMIN_IDS = full_admins
else:
    # If no FULL_ADMIN_IDS specified, use all ADMIN_IDS as full admins
    FULL_ADMIN_IDS = ADMIN_IDS.copy()

# Limited admins (can only view registered members, no approval rights)
LIMITED_ADMIN_IDS_ENV = os.environ.get("LIMITED_ADMIN_IDS")  # comma-separated ids
if LIMITED_ADMIN_IDS_ENV:
    limited_admins = []
    for x in LIMITED_ADMIN_IDS_ENV.split(","):
        x = x.strip()
        if not x:
            continue
        try:
            limited_admins.append(int(x))
        except ValueError:
            logging.warning("Skipping invalid LIMITED_ADMIN_IDS value: %r", x)
    LIMITED_ADMIN_IDS = limited_admins
else:
    LIMITED_ADMIN_IDS = []

# All admin IDs (for backward compatibility and notifications)
ALL_ADMIN_IDS = list(set(FULL_ADMIN_IDS + LIMITED_ADMIN_IDS + ADMIN_IDS))

WORKSHOP_GROUP_LINK = os.environ.get("WORKSHOP_GROUP_LINK") or os.environ.get("GROUP_LINK") or ""