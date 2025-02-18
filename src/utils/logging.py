import datetime
import json
import logging
import sys
from logging.config import dictConfig
from types import FrameType
from typing import cast

import loguru
import stackprinter

from app.config.config import settings
from app.schemas.json_logs import BaseJsonLogSchema

# Set stackprinter as the default exception printer
stackprinter.set_excepthook(style="darkbg2")

LEVEL_TO_NAME = {
    logging.CRITICAL: "CRITICAL",
    logging.ERROR: "ERROR",
    logging.WARNING: "WARNING",
    logging.INFO: "INFO",
    logging.DEBUG: "Debug",
    logging.NOTSET: "Trace",
}
FILE_PATH = "fastapi.json"


class ConsoleLogger(logging.Handler):
    def emit(self, record: logging.LogRecord) -> None:  # pragma: no cover
        # Get corresponding Loguru level if it exists
        try:
            level = loguru.logger.level(record.levelname).name
        except ValueError:
            level = str(record.levelno)
        # Find caller from where originated the logged message
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:  # noqa: WPS609
            frame = cast(FrameType, frame.f_back)
            depth += 1
        loguru.logger.opt(depth=depth, exception=record.exc_info).log(
            level,
            record.getMessage(),
        )


class JSONLogFormatter(logging.Formatter):
    """
    Custom class-formatter for writing logs to json
    """

    def format(self, record: logging.LogRecord, *args, **kwargs) -> str:
        """
        Formating LogRecord to json

        :param record: logging.LogRecord
        :return: json string
        """
        log_object: dict = self._format_log_object(record)
        return json.dumps(log_object, ensure_ascii=False)

    @staticmethod
    def _format_log_object(record: logging.LogRecord) -> dict:
        now: str = (
            datetime.datetime.fromtimestamp(record.created)
            .astimezone()
            .replace(microsecond=0)
            .isoformat()
        )
        message = record.getMessage()
        duration = record.duration if hasattr(record, "duration") else record.msecs

        json_log_fields = BaseJsonLogSchema(
            thread=record.process,
            timestamp=now,
            level=LEVEL_TO_NAME[record.levelno],
            msg=message,
            func=record.funcName + ":" + str(record.lineno),
            source_log=record.name,
            duration=duration,
            app_name=settings.PROJECT_NAME,
            app_version=settings.VERSION,
        )

        if hasattr(record, "props"):
            json_log_fields.props = record.props

        if record.exc_info:
            json_log_fields.exceptions = (
                # default library traceback
                # traceback.format_exception(*record.exc_info)
                # stackprinter gets all debug information
                # https://github.com/cknd/stackprinter/blob/master/stackprinter/__init__.py#L28-L137
                stackprinter.format(
                    record.exc_info,
                    suppressed_paths=[
                        r"lib/python.*/site-packages/starlette.*",
                    ],
                    add_summary=False,
                ).split("\n")
            )

        elif record.exc_text:
            json_log_fields.exceptions = record.exc_text

        # Pydantic to dict
        json_log_object = json_log_fields.model_dump(
            exclude_unset=True,
            by_alias=True,
        )
        # getting additional fields
        if hasattr(record, "request_json_fields"):
            json_log_object.update(record.request_json_fields)

        return json_log_object


def handlers(env, to_file=settings.SAVE_LOGS_TO_FILE):
    handler = ["json"] if env == 1 else ["intercept"]

    if to_file:
        handler.append("file_handler")

    return handler


LOG_HANDLER = handlers(settings.JSON_LOG_FORMAT)
LOGGING_LEVEL = logging.DEBUG if settings.DEBUG else logging.INFO

LOG_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "json": {
            "()": JSONLogFormatter,
        },
    },
    "handlers": {
        "json": {
            "formatter": "json",
            "class": "logging.StreamHandler",
            "stream": sys.stdout,
        },
        "intercept": {
            "()": ConsoleLogger,
        },
        # 'file_handler': {
        #     'level': 'INFO',
        #     'filename': FILE_PATH,
        #     'class': 'logging.FileHandler',
        #     'formatter': 'json'
        # }
    },
    "loggers": {
        "main": {
            "handlers": LOG_HANDLER,
            "level": LOGGING_LEVEL,
            "propagate": False,
        },
        "uvicorn": {
            "handlers": LOG_HANDLER,
            "level": "INFO",
            "propagate": False,
        },
        "uvicorn.access": {
            "handlers": LOG_HANDLER,
            "level": "ERROR",
            "propagate": False,
        },
    },
}


dictConfig(LOG_CONFIG)
logger = logging.getLogger("main")
