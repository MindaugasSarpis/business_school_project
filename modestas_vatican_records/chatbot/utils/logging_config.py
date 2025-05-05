import logging

def configure_logging() -> logging.Logger:
    """Configure logging for the entire application."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(filename)s:%(lineno)d - %(levelname)s - %(message)s",
        force=True,
    )
    return logging.getLogger()