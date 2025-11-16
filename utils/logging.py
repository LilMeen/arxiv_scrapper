import logging
import os

def setup_logger(log_file):
    logger = logging.getLogger(log_file)  
    logger.setLevel(logging.INFO)

    # Xóa handler cũ nếu có
    if logger.hasHandlers():
        logger.handlers.clear()

    handler = logging.FileHandler(log_file, mode='a', encoding='utf-8')
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger

def close_logger(logger):
    for handler in logger.handlers[:]:
        handler.close()
        logger.removeHandler(handler)


def summary_threading_log(scrapper_name, num_threads, log_type):
    # concat all log files into summary.log
    with open(f'logs/{scrapper_name}_{log_type}.log', 'w', encoding='utf-8') as summary_file:
        for i in range(num_threads):
            thread_log_file = f'logs/{scrapper_name}_thread_{i+1}_{log_type}.log'
            if os.path.exists(thread_log_file):
                with open(thread_log_file, 'r', encoding='utf-8') as f:
                    summary_file.write(f.read())
                    f.close()
                os.remove(thread_log_file)  