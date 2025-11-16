import os

def calc_error_count(error_log_file):
    error_data = None
    # count error by counting lines in log_file
    if os.path.exists(error_log_file):
        with open(error_log_file, 'r', encoding='utf-8') as f:
            error_data = f.readlines()
        num_errors = len(error_data)
    return num_errors

def calc_success_rate(total_id):
    error_data = None
    # count error by counting lines in arxiv.log
    if os.path.exists('logs/arxiv_error.log'):
        with open('logs/arxiv_error.log', 'r', encoding='utf-8') as f:
            error_data = f.readlines()
        num_errors = len(error_data)

    return (len(total_id) - num_errors) / len(total_id) * 100


def calc_avg_paper_size(size_log_file):
    size_data = None
    total_before_size = 0.0
    total_after_size = 0.0
    num_papers = 0
    # calculate average paper size from size_log_file
    if os.path.exists(size_log_file):
        with open(size_log_file, 'r', encoding='utf-8') as f:
            size_data = f.readlines()
        for line in size_data:
            num_papers += 1
            size_info = line.strip().split(':')[-1].strip()
            before_size, after_size = size_info.split('/')
            before_size_mb = float(before_size.strip().split(' ')[0])
            total_before_size += before_size_mb
            after_size_mb = float(after_size.strip().split(' ')[0])
            total_after_size += after_size_mb
    if num_papers == 0:
        return 0.0
    return total_before_size / num_papers, total_after_size / num_papers


def calc_total_papers(total_log_file):
    total_data = None
    num_papers = 0
    # count total papers by counting lines in total_log_file
    if os.path.exists(total_log_file):
        with open(total_log_file, 'r', encoding='utf-8') as f:
            total_data = f.readlines()
        for line in total_data:
            num_papers += int(line.strip())
    os.remove(total_log_file)
    return num_papers

def calc_avg_references(references_log_file):
    references_data = None
    total_references = 0
    num_papers = 0
    # calculate average references from references_log_file
    if os.path.exists(references_log_file):
        with open(references_log_file, 'r', encoding='utf-8') as f:
            references_data = f.readlines()
        for line in references_data:
            num_papers += 1
            references_info = line.strip().split(':')[-1].strip()
            num_references = int(references_info.split(' ')[0])
            total_references += num_references
    if num_papers == 0:
        return 0.0
    return total_references / num_papers


def calc_memory(memory_log_file):
    memory_data = None
    peak_memory = 0.0
    # get peak memory from memory_log_file
    if os.path.exists(memory_log_file):
        with open(memory_log_file, 'r', encoding='utf-8') as f:
            memory_data = f.readlines()
        for line in memory_data:
            if 'Peak memory usage' in line:
                peak_memory = float(line.strip().split(':')[-1].strip().split(' ')[0])
            if 'Average memory used' in line:
                avg_memory = float(line.strip().split(':')[-1].strip().split(' ')[0])
    return peak_memory, avg_memory
