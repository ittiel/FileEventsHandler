"""
Custom logger class based on python logging library.
"""
import logging


class Logger:

    def __init__(self, logger_name):
        """
        Class Constructor.
        Initializes the Following:
        1. log file name, path and mode.
        2. log level.
        3. log date and time format.
        :param logger_name: For the logger name to be shown in the log file.
        """
        # Create logger
        self.logger = logging.getLogger(logger_name)
        self.log_file = 'file_event_handler_logs.txt'
        self.log_file_mode = 'w'
        # Set level and format
        self.log_level = logging.INFO
        self.logger.setLevel(self.log_level)
        self.log_format = '[%(asctime)s] - [%(name)-12s] - [%(levelname)s] --- %(message)s'
        self.date_format = '%d/%m/%y %H:%M:%S'
        logging.basicConfig(filename=self.log_file, filemode=self.log_file_mode, level=self.log_level,
                            format=self.log_format, datefmt=self.date_format)

