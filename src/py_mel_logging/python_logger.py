"""Implementation of PythonLogger."""
import logging
import os
import sys
from string import Template
from typing import Callable
from typing import TypeVar

import clr  # type: ignore

from .i18n import i18n

sys.path.append(os.path.join(os.path.dirname(__file__), "dlls/netstandard2.0"))
clr.AddReference(r"Microsoft.Extensions.Logging.Abstractions")

from Microsoft.Extensions.Logging import EventId  # type: ignore
from Microsoft.Extensions.Logging import LogLevel  # type: ignore
from System import IDisposable  # type: ignore

TState = TypeVar("TState")


class PythonLogger:
    """A connector between the Microsoft.Extensions.Logging framework \
    and a python logger."""

    def __init__(self, log_level: int, handler: logging.Handler):
        """
        Initialize.

        Parameters
        ----------
        log_level: int
                   Max level to log messages at.
        handler: logging.Handler
                 Handler for dispatching messages to the correct location.
        """
        self._logger = logging.getLogger(__name__)
        self._logger.setLevel(log_level)
        self._logger.addHandler(handler)

    def begin_scope(self, state: TState) -> IDisposable:
        """
        Begins a logical operation scope.

        Logging scopes are not currently supported in python.

        Parameters
        ----------
        state: TState
               The identifier for the scope.

        Returns
        -------
        None.
        """
        return None

    def is_enabled(self, log_level: LogLevel) -> bool:
        """
        Check if the given logLevel is enabled.

        Parameters
        ----------
        log_level: LogLevel
                   level to be checked.

        Returns
        -------
        true if enabled; false otherwise.
        """
        python_level: int = PythonLogger._get_python_level(log_level)
        result: bool = self._logger.isEnabledFor(python_level)
        return result

    def log(
        self,
        log_level: LogLevel,
        event_id: EventId,
        state: TState,
        exception: Exception,
        formatter: Callable[[TState, Exception], str],
    ) -> None:
        """
        Write a log entry.

        Parameters
        ----------
        log_level: LogLevel
                   Entry will be written on this level.
        event_id: EventId
                  Id of the event.
        state: TState
               The entry to be written. Can be also an object.
        exception: Exception
                   The exception related to this entry.
        formatter: Callable[[TState, Exception], str]
                   Function to create a String message of the state and
                   exception.
        """

        if not self.is_enabled(log_level):
            return

        message: str = ""
        if formatter is not None:
            message = formatter(state, exception)
        else:
            if state is not None:
                message = str(state)
            if exception is not None:
                if message != "":
                    message += "\n"
                message += i18n("Literals", "EXCEPTION_STR") + ": " + exception.Message

        if id is not None:
            msg_args = {"id": event_id.Id, "message": message}
            message = Template("[${id}] : ${message}").safe_substitute(msg_args)

        python_level: int = self._get_python_level(log_level)
        self._logger.log(python_level, message)

    @staticmethod
    def _get_python_level(log_level: LogLevel) -> int:
        """
        Get the equivalent python logging level for a .NET LogLevel.

        Parameters
        ----------
        log_level: LogLevel
                   The .NET LogLevel.

        Returns
        -------
        The equivalent python logging level.
        """
        python_level: int = logging.CRITICAL
        if log_level == getattr(LogLevel, "None"):
            python_level = logging.NOTSET
        elif log_level == LogLevel.Trace:
            # Python has no trace level, so we return the level right below debug as trace.
            python_level = logging.DEBUG - 1
        elif log_level == LogLevel.Debug:
            python_level = logging.DEBUG
        elif log_level == LogLevel.Information:
            python_level = logging.INFO
        elif log_level == LogLevel.Warning:
            python_level = logging.WARN
        elif log_level == LogLevel.Error:
            python_level = logging.ERROR
        return python_level
