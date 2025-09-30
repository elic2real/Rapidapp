import logging
import sys
LOGGING_CONFIG = {
    "version": 1,
    "formatters": {
        "json": {
            "format": '{"time":"%(asctime)s","level":"%(levelname)s","msg":"%(message)s","job_id":"%(job_id)s","route":"%(route)s","duration_ms":"%(duration_ms)s"}'
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "json",
            "stream": sys.stdout,
        }
    },
    "root": {"level": "INFO", "handlers": ["console"]},
}