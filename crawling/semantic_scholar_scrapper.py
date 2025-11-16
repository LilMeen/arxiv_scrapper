import json
import os
import requests
import time

from utils.logging import setup_logger, close_logger

def semantic_scholar_scrapper(id_list, max_retries, time_interval, log_file):
    error_logger = setup_logger(f'{log_file}_error.log')
    info_logger = setup_logger(f'{log_file}_references.log')
    req = requests.Session()


    for paper_id in id_list:
        url =  f'https://api.semanticscholar.org/graph/v1/paper/arXiv:{paper_id}'
        params = {
            "fields": "references,references.externalIds,references.title,references.authors,references.publicationDate"
        }


        for attempt in range(max_retries):
            response = req.get(url, params=params)
            data = response.json()
            if response.status_code == 200:
                time.sleep(time_interval)
                break
            
            if attempt + 1 == max_retries: 
                error_logger.error(f"{paper_id}")
            time.sleep(time_interval)

        reference_data = data.get('references', [])

        reference = {}
        
        for ref in reference_data:
            external_ids = ref.get('externalIds', {})
            if not external_ids:
                continue
                
            paper_arxiv_id = external_ids.get('ArXiv')
            if not paper_arxiv_id:
                continue

            paper_arxiv_id = paper_arxiv_id.replace('.', '-')
            title = ref.get('title', 'N/A')
            authors = [author.get('name', 'N/A') for author in ref.get('authors', [])]
            venue = ref.get('venue', 'N/A')
            scholar_id = ref.get('paperId', 'N/A')
            publication_date = ref.get('publicationDate', 'N/A')

            
            reference[paper_arxiv_id] = {
                'semanticScholarID': scholar_id,
                'title': title,
                'authors': authors,
                'venue': venue,
                'submission_date': publication_date
            }
        json_object = json.dumps(reference, indent=4)

        folder_path = 'data/' + paper_id.replace('.', '-')
        os.makedirs(folder_path, exist_ok=True)
        with open(f'{folder_path}/references.json', 'w', encoding='utf-8') as f:
            f.write(json_object)
            f.close()

        info_logger.info(f"{paper_id}: {len(reference)} references")

    close_logger(error_logger)
    close_logger(info_logger)