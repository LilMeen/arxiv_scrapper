# arXiv & Semantic Scholar Scraper

## 1. How to Run

### 1.1. Problem Before Running

Recently, an error occurs when using the **arXiv** library (v2.3.0).\
The error happens in the function `download_source()` due to incorrect
handling of the PDF link.

The bug is caused by this line:

    self.pdf_url.replace("/pdf/", "/src/")

Because `pdf_url` is sometimes **NoneType**, calling `.replace()` raises
an exception.

To fix this, users must manually modify the installed arXiv library.\
In function `Result._get_pdf_url`, update the assignment of `_pdf_url`
to:

``` python
pdf_urls = [link.href for link in links if "/pdf/" in link.href]
```

This ensures PDF URLs are correctly retrieved.

### 1.2. Configuration

The configuration file is `config.ini`. Users can adjust parameters
depending on scraping needs:

-   **start_month** --- Starting month (YYMM format)\
-   **end_month** --- Ending month (YYMM format)\
-   **start_id** --- First paper ID to scrape\
-   **end_id** --- Last paper ID to scrape\
-   **arxiv_num_threads** --- Number of threads for arXiv scraping\
-   **scholar_num_threads** --- Number of threads for Semantic Scholar
    scraping\
-   **max_retries** --- Maximum retry attempts\
-   **time_interval** --- Waiting time between retries (seconds)

### 1.3. Step-by-Step Guide

1.  Install dependencies:

        pip install -r requirements.txt

2.  Update the `_get_pdf_url` function inside the arXiv library as
    described above.

3.  Run:

        python main.py

### 1.4. Running on Google Colab

To run on Google Colab, clone the repository and execute the program:

``` bash
!git clone https://github.com/LilMeen/arxiv_scrapper
%cd arxiv_scrapper
!pip install -r requirements.txt
!python main.py
```

**Note:**\
Unexpectedly, when running on Google Colab, the `arXiv` library does
*not* require fixing --- `download_source()` works normally.\
However, when running locally, the code modification is necessary to
prevent errors.

------------------------------------------------------------------------

