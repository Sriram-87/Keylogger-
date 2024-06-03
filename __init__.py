# src/keylogger/__init__.py

# Define which symbols should be exported when the package is imported
from .email_sender import EmailSender
from .event_handler import MyFileSystemEventHandler
from .keylogger import Keylogger

# Optionally, you can specify the symbols to export using __all__
__all__ = ['EmailSender', 'MyFileSystemEventHandler', 'Keylogger']
