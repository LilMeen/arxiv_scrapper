import arxiv
from datetime import datetime
import json
import os
import tarfile


from crawling.logging import setup_logger

MAX_ID = 200



def arxiv_scrapper(id_list, log_file):
    logger = setup_logger(log_file)

    client = arxiv.Client()

    papers = get_papers(client, id_list)
    
    previous_paper_id = None
    for paper in papers[::-1]:
        paper_id, version = paper.entry_id.split("arxiv.org/abs/")[-1].split('v')

        if previous_paper_id != paper_id:
            get_metadata(paper, papers)


        get_full_text_source(paper, logger)
        previous_paper_id = paper_id
    return


def get_papers(client, id_list):
    additional_id = [] 
    papers = []

    chunks = [id_list[i:i + MAX_ID] for i in range(0, len(id_list), MAX_ID)]
    for chunk in chunks:
        print(f"Processing chunk with {len(chunk)} IDs, from {chunk[0]} to {chunk[-1]}")
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
    
    print()
    chunks = [additional_id[i:i + MAX_ID] for i in range(0, len(additional_id), MAX_ID)]
    for chunk in chunks:
        print(f"Processing additional chunk with {len(chunk)} IDs, from {chunk[0]} to {chunk[-1]}")
        search = arxiv.Search(
            id_list=chunk,
            sort_by=arxiv.SortCriterion.Relevance
        )
        result_papers = list(client.results(search))
        papers.extend(result_papers)
    
    papers.sort(key=lambda x: x.entry_id)
    for paper in papers:
        print(paper.entry_id)
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


def get_full_text_source(paper, logger):
    paper_id = paper.entry_id.split("arxiv.org/abs/")[-1].split('v')[0]
    save_path = 'data/' + paper_id.replace('.', '-') + '/tex'
    os.makedirs(save_path, exist_ok=True)

    paper_version_folder_path = paper.entry_id.split("arxiv.org/abs/")[-1].replace('.', '-')

    tar_path = paper.download_source(dirpath=save_path)

    destination_path = os.path.join(save_path, paper_version_folder_path)
    os.makedirs(destination_path, exist_ok=True)

    try: 
        with tarfile.open(tar_path, "r:gz") as tar:
            tar.extractall(path=destination_path)

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
        os.remove(tar_path)
    except Exception as e:
        logger.error(f"{paper.entry_id.split('arxiv.org/abs/')[-1]}: {e}")
        os.remove(tar_path)
