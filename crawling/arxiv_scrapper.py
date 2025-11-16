import arxiv
from datetime import datetime
import json
import os
import tarfile
import time

from utils.logging import setup_logger, close_logger

MAX_ID = 200



def arxiv_scrapper(id_list, log_file):
    error_logger = setup_logger(f'{log_file}_error.log')
    info_logger = setup_logger(f'{log_file}_paper_size.log')

    client = arxiv.Client()

    papers = get_papers(client, id_list)
    
    previous_paper_id = None
    for paper in papers[::-1]:
        paper_id, version = paper.entry_id.split("arxiv.org/abs/")[-1].split('v')

        if previous_paper_id != paper_id:
            get_metadata(paper, papers)


        get_full_text_source(paper, error_logger, info_logger)
        previous_paper_id = paper_id

    close_logger(error_logger)
    close_logger(info_logger)
    with open('logs/total_papers.log', 'a', encoding='utf-8') as f:
        f.write(f"{len(papers)}\n")
        f.close()
    return


def get_papers(client, id_list):
    additional_id = [] 
    papers = []

    chunks = [id_list[i:i + MAX_ID] for i in range(0, len(id_list), MAX_ID)]
    for chunk in chunks:
        search = arxiv.Search(
            id_list=chunk,
            sort_by=arxiv.SortCriterion.Relevance
        )
        result_papers = list(client.results(search))

        for paper in result_papers:
            papers.append(paper)
            version = int(paper.get_short_id().split('v')[1])
            if version > 1:
                for i in range(1, version):
                    p_id = paper.entry_id.split('arxiv.org/abs/')[-1].split('v')[0]
                    additional_id.append(f"{p_id}v{i}")
    
    chunks = [additional_id[i:i + MAX_ID] for i in range(0, len(additional_id), MAX_ID)]
    for chunk in chunks:
        search = arxiv.Search(
            id_list=chunk,
            sort_by=arxiv.SortCriterion.Relevance
        )
        result_papers = list(client.results(search))
        papers.extend(result_papers)
    
    papers.sort(key=lambda x: x.entry_id)
    return papers




def get_metadata(paper, all_papers):
    paper_id = paper.entry_id.split("arxiv.org/abs/")[-1].split('v')[0]

    metadata_dict= {
        'title': paper.title,
        'authors': [str(author) for author in paper.authors],
        'publication_venue': paper.journal_ref,
        'submission_date': datetime.strftime(paper.published, '%Y-%m-%d'),
        'revised_dates': []
    }
    version = int(paper.get_short_id().split('v')[1])
    
    for i in range(1, version + 1):
        version_paper = next(p for p in all_papers if p.entry_id.split("arxiv.org/abs/")[-1] == f"{paper_id}v{i}")
        date_obj = version_paper.updated
        iso_date = datetime.strftime(date_obj, '%Y-%m-%d')
        metadata_dict['revised_dates'].append(iso_date)

    folder_path = 'data/' + paper_id.replace('.', '-')
    os.makedirs(folder_path, exist_ok=True)

    metadata_json = json.dumps(metadata_dict, indent=4)
    with open(f'{folder_path}/metadata.json', 'w', encoding='utf-8') as f:
        f.write(metadata_json)
        f.close()


def get_full_text_source(paper, error_logger, info_logger):
    paper_id = paper.entry_id.split("arxiv.org/abs/")[-1].split('v')[0]
    #save_path = 'data/' + paper_id.replace('.', '-') + '/tex'
    save_path = os.path.join('data', paper_id.replace('.', '-'), 'tex')
    os.makedirs(save_path, exist_ok=True)

    paper_version_folder_path = paper.entry_id.split("arxiv.org/abs/")[-1].replace('.', '-')


    tar_path = None
    try: 
        tar_path = paper.download_source(dirpath=save_path)
        destination_path = os.path.join(save_path, paper_version_folder_path)
        os.makedirs(destination_path, exist_ok=True)

        with tarfile.open(tar_path, "r:gz") as tar:
            tar.extractall(path=destination_path)

            # Get paper size in MB
            paper_size_mb = get_folder_size_mb(destination_path)
            # Delete non tex files and non bib files
            for root, _, files in os.walk(destination_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    if file.endswith('.tar.gz'):
                        nested_tar_path = file_path
                        with tarfile.open(nested_tar_path) as nested_tar:
                            nested_tar.extractall(path=root)
                        os.remove(nested_tar_path)
                    else: 
                        if not file.endswith('.tex') and not file.endswith('.bib'):
                            os.remove(file_path)
            paper_size_mb_after_remove = get_folder_size_mb(destination_path)
            info_logger.info(f"Paper {paper.entry_id.split('arxiv.org/abs/')[-1]} (before/after remove pdf): {paper_size_mb:.2f} MB / {paper_size_mb_after_remove:.2f} MB")
        os.remove(tar_path)
    except Exception as e:
        error_logger.error(f"{paper.entry_id.split('arxiv.org/abs/')[-1]}: {e}")

        if tar_path and os.path.exists(tar_path):
            os.remove(tar_path)


def get_folder_size_mb(folder):
    if not os.path.exists(folder):
        return 0
    total = 0
    for root, dirs, files in os.walk(folder):
        for f in files:
            fp = os.path.join(root, f)
            total += os.path.getsize(fp)
    return total / (1024 * 1024)