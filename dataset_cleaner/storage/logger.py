import os
import logging

def setup_logger(output_dir: str):
    """Sets up loggers for application.log, processing.log, errors.log, and rejected.log."""
    logs_dir = os.path.join(output_dir, "logs")
    os.makedirs(logs_dir, exist_ok=True)

    formatter = logging.Formatter('[%(asctime)s] %(levelname)s - %(message)s')

    def build_logger(name, filename, level=logging.INFO):
        handler = logging.FileHandler(os.path.join(logs_dir, filename), encoding="utf-8")
        handler.setFormatter(formatter)
        logger = logging.getLogger(name)
        logger.setLevel(level)
        logger.addHandler(handler)
        return logger

    app_log = build_logger("app_logger", "application.log")
    proc_log = build_logger("proc_logger", "processing.log")
    err_log = build_logger("err_logger", "errors.log", level=logging.ERROR)
    rej_log = build_logger("rej_logger", "rejected.log")

    return app_log, proc_log, err_log, rej_log
