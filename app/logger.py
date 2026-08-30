import logging
import os

class Logger:

    def __init__(self, name=__name__, level=logging.INFO):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)

        if not self.logger.handlers:
            log_format = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )

            console_handler = logging.StreamHandler()
            console_handler.setFormatter(log_format)
            self.logger.addHandler(console_handler)

            log_file = os.getenv("APP_LOG_FILE", "app.log")
            file_handler = logging.FileHandler(log_file)
            file_handler.setFormatter(log_format)
            self.logger.addHandler(file_handler)

    def get_logger(self):
        return self.logger