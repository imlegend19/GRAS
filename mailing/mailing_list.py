from bs4 import BeautifulSoup
import requests
import urllib
import gzip
import os
from joblib import Parallel, delayed

compressed_types = ['gz']
uncompressed = ['mbox', 'txt']

def downloader(url ,link):
    final_url = url+link
    if not os.path.exists("data"):
        os.makedirs("data")

    if link.split('.')[-1] == "txt":
        print("Text File")
        urllib.request.urlretrieve(final_url, "./data/{}".format(link))
    else:
        filename, _, _ = link.partition('.gz')

        try:
            with urllib.request.urlopen(final_url) as resp:
                with gzip.GzipFile(fileobj=resp) as uncompressed:
                    content = uncompressed.read()
            
            with open('./data/{fi}'.format(fi=filename),'wb') as f:
                f.write(content)
        except:
            print("Error")
        


if __name__ == "__main__":
    url = "https://mta.openssl.org/pipermail/openssl-commits/"
    resp = requests.get(url)
    
    soup = BeautifulSoup(resp.text, 'html.parser')

    links = list()

    for l in soup.findAll("a"):
        check = l["href"].split('.')
        # if(check[-1] == "gz" or check[-1] == "txt"):
        if(check[-1] in uncompressed or check[-1] in compressed_types):
            links.append(l["href"])

    Parallel(n_jobs = 5)(delayed(downloader)(url, l) for l in links)
    
    