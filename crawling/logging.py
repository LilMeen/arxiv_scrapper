import logging

def setup_logger(log_file):
    logger = logging.getLogger(log_file)  
    logger.setLevel(logging.ERROR)

    # Xóa handler cũ nếu có
    if logger.hasHandlers():
        logger.handlers.clear()

    handler = logging.FileHandler(log_file, mode='a', encoding='utf-8')
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger