import concurrent.futures
import gzip
import logging
import urllib.request

import requests
from bs4 import BeautifulSoup

from gras.errors import DownloaderError

COMPRESSED_TYPES = ['gz']
UNCOMPRESSED_TYPES = ['mbox', 'txt']
THREADS = 10

logger = logging.getLogger("main")


class Downloader:
    def __init__(self, url, path):
        self.url = url
        self.path: str = path
        
        if self.path[-1] == '/':
            self.path = self.path[:-1]
    
    def process(self):
        resp = requests.get(self.url)
        
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        links = list()
        
        for s in soup.findAll("a"):
            check = s["href"].split('.')
            if check[-1] in UNCOMPRESSED_TYPES or check[-1] in COMPRESSED_TYPES:
                links.append(s["href"])
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=THREADS) as executor:
            process = {executor.submit(self._download, link): link for link in links}
            for future in concurrent.futures.as_completed(process):
                link = process[future]
                logger.debug(f"Downloaded {link}")
    
    def _download(self, link):
        final_url = self.url + link
        
        if link.split('.')[-1] == "txt":
            urllib.request.urlretrieve(final_url, f"{self.path}/{link}")
        else:
            filename, _, _ = link.partition('.gz')
            
            try:
                with urllib.request.urlopen(final_url) as resp:
                    with gzip.GzipFile(fileobj=resp) as uncompressed:
                        content = uncompressed.read()
                
                with open(f'{self.path}/{filename}', 'wb') as f:
                    f.write(content)
            except Exception as e:
                DownloaderError(msg=e)
