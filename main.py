# Start month: 07/2022
# Start id: 6755

# End month: 07/2022
# End id: 11754

# For each assigned paper, crawling:
# => Initial submission and subsequent revisions (Ex: 2207.12345v1, 2207.12345v2, etc.)
# => For paper submitted once, add suffix with v1 (Ex: 2207.12345v1)

# The scraping process should retrieve:
# => full-text source files(TeX)
# => metadata
# => BibTex references
# => Crawling reference information for each version


from datetime import datetime
import threading
import time
import math
import os
import pandas as pd
import configparser

from crawling.arxiv_scrapper import arxiv_scrapper
from crawling.semantic_scholar_scrapper import semantic_scholar_scrapper

MAX_ID = 30000

def summary_log(num_threads):
    # concat all log files into summary.log
    with open('logs/summary.log', 'w', encoding='utf-8') as summary_file:
        for i in range(num_threads):
            thread_log_file = f'logs/thread_{i+1}.log'
            if os.path.exists(thread_log_file):
                with open(thread_log_file, 'r', encoding='utf-8') as f:
                    summary_file.write(f.read())
                    summary_file.write('\n')

def exec_multithread(arxiv_scrapper, semantic_scholar_scrapper, max_retries, time_interval, id_list, arxiv_num_threads=4, scholar_num_threads=4):
    threads = []
    """ 
    arxiv_pagination = math.ceil(len(id_list) / arxiv_num_threads)
    arxiv_chunk = []
    # Write metalog files
    with open('logs/arxiv_metalog.log', 'w', encoding='utf-8') as f:
        for i in range(arxiv_num_threads):
            start_index = i * arxiv_pagination
            end_index = (i + 1) * arxiv_pagination - 1 if (i + 1) * arxiv_pagination - 1 < len(id_list) else len(id_list) - 1
            start_id = id_list[start_index]
            end_id = id_list[end_index]

            id_list_chunk = id_list[start_index:end_index + 1]
            arxiv_chunk.append(id_list_chunk)

            f.write(f"Thread {i+1}: IDs {start_id} to {end_id}, total {len(id_list_chunk)}\n")

    for i in range(arxiv_num_threads):
        id_list_chunk = arxiv_chunk[i]

        print(f"Starting thread {i+1} for IDs {id_list_chunk[0]} to {id_list_chunk[-1]}")
        thread = threading.Thread(
            target=arxiv_scrapper,
            args=(id_list_chunk, f'logs/arxiv_thread_{i+1}.log')
        )

        threads.append(thread)
        thread.start() """


    semantic_scholar_pagination = math.ceil(len(id_list) / scholar_num_threads)
    semantic_scholar_chunk = []
    # Write metalog files
    with open('logs/scholar_metalog.log', 'w', encoding='utf-8') as f:
        for i in range(scholar_num_threads):
            start_index = i * semantic_scholar_pagination
            end_index = (i + 1) * semantic_scholar_pagination - 1 if (i + 1) * semantic_scholar_pagination - 1 < len(id_list) else len(id_list) - 1
            start_id = id_list[start_index]
            end_id = id_list[end_index]

            id_list_chunk = id_list[start_index:end_index + 1]
            semantic_scholar_chunk.append(id_list_chunk)

            f.write(f"Thread {i+1}: IDs {start_id} to {end_id}, total {len(id_list_chunk)}\n")
    
    for i in range(scholar_num_threads):
        id_list_chunk = semantic_scholar_chunk[i]

        print(f"Starting thread {i+1} for IDs {id_list_chunk[0]} to {id_list_chunk[-1]}")
        thread = threading.Thread(
            target=semantic_scholar_scrapper,
            args=(id_list_chunk, max_retries, time_interval, f'logs/scholar_thread_{i+1}.log')
        )

        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

def exec_singlethread(crawl, id_list):
    crawl(id_list, log_file='logs/singlethread.log')


def generate_id_list(start_month, end_month, start_id, end_id):
    monthly_submission_df = pd.read_csv('get_monthly_submissions.csv')
    monthly_submission_df['month'] = monthly_submission_df['month'].apply(lambda x: str(x)[2:4] + str(x)[5:7])

    # convert string to datetime
    month_start_date_format = datetime.strptime(start_month, '%y%m')
    month_end_date_format = datetime.strptime(end_month, '%y%m')

    id_list = []
    for single_month in pd.date_range(start=month_start_date_format, end=month_end_date_format, freq='MS'):
        month_str = single_month.strftime('%y%m')
        start = start_id if month_str == start_month else 1
        end = end_id if month_str == end_month else monthly_submission_df[(monthly_submission_df['month'] == month_str)]['submissions'].iloc[0]
        
        for i in range(start, end + 1):
            id_list.append(f'{month_str}.{str(i).zfill(5)}')
    return id_list

if __name__ == "__main__":
    #shutil.rmtree('data', ignore_errors=True)
    #shutil.rmtree('logs', ignore_errors=True)
    os.makedirs('data', exist_ok=True)
    os.makedirs('logs', exist_ok=True)
    os.makedirs('runtime_logs', exist_ok=True)

    run_time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    config = configparser.ConfigParser()
    config.read('config.ini')

    start_month = str(config['configuration']['start_month'])
    end_month = str(config['configuration']['end_month'])
    start_id = int(config['configuration']['start_id'])
    end_id = int(config['configuration']['end_id'])
    arxiv_num_threads = int(config['configuration']['arxiv_num_threads'])
    scholar_num_threads = int(config['configuration']['scholar_num_threads'])

    max_retries = int(config['configuration']['max_retries'])
    time_interval = int(config['configuration']['time_interval'])

    run_type = ['multithread', 'singlethread'][0]

    id_list = generate_id_list(start_month=start_month, end_month=end_month, start_id=start_id, end_id=end_id)

    if run_type == 'multithread':
        start_time = time.time()
        exec_multithread(
            arxiv_scrapper, 
            semantic_scholar_scrapper, 
            max_retries=max_retries, 
            time_interval=time_interval, 
            id_list=id_list, 
            arxiv_num_threads=arxiv_num_threads, 
            scholar_num_threads=scholar_num_threads
        )
        end_time = time.time()
        print(f"Total time taken: {end_time - start_time} seconds")
        print()

        with open('runtime_logs/summary.log', 'a', encoding='utf-8') as f:
            f.write(f"\n=== Run at {run_time_str} ===\n")
            f.write(f"start_month = {config['configuration']['start_month']}\n")
            f.write(f"end_month = {config['configuration']['end_month']}\n")
            f.write(f"start_id = {config['configuration']['start_id']}\n")
            f.write(f"end_id = {config['configuration']['end_id']}\n")
            f.write(f"arxiv_num_threads = {config['configuration']['arxiv_num_threads']}\n")
            f.write(f"scholar_num_threads = {config['configuration']['scholar_num_threads']}\n")
            f.write(f"max_retries = {config['configuration']['max_retries']}\n")
            f.write(f"time_interval = {config['configuration']['time_interval']}\n")
            f.write(f"total run time = {end_time - start_time} seconds\n\n")


    
