from __future__ import annotations

import logging
import time

import psycopg

from app.core.config import settings

logger = logging.getLogger(__name__)

MAX_RETRIES = 60
SLEEP_SECONDS = 1


def main() -> None:
    url = settings.database_url.replace("postgresql+psycopg", "postgresql")

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            with psycopg.connect(url, connect_timeout=2) as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT 1;")
            logger.info("DB is ready")
            return
        except psycopg.Error as exc:
            logger.info(
                "Waiting for DB... attempt %s/%s (%s)",
                attempt,
                MAX_RETRIES,
                str(exc)[:120],
            )
            time.sleep(SLEEP_SECONDS)

    raise RuntimeError("DB not ready after 60 seconds")


if __name__ == "__main__":
    main()
