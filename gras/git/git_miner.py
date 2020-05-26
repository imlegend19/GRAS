import logging
import multiprocessing as mp
from timeit import default_timer

from pygit2 import GIT_SORT_TIME, GIT_SORT_TOPOLOGICAL, Repository

from gras.base_miner import BaseMiner

logger = logging.getLogger("main")


class GitMiner(BaseMiner):
    def __init__(self, args):
        if args is not None:
            super().__init__(args)
        
        self.repo = Repository("/home/mahen/flutter/.git")
        self._fetch_references()
        self.queue = mp.JoinableQueue()
        self.process()
    
    def _load_from_file(self, file):
        pass
    
    def dump_to_file(self, path):
        pass
    
    def _fetch_references(self):
        self.tags, self.branches = [], {}
        for reference in self.repo.listall_references():
            if 'refs/tags' in reference:
                self.tags.append(reference)
            else:
                self.branches[reference] = self.repo.lookup_reference(reference).peel().oid
    
    def _parse_commit(self, oid):
        pass
    
    def _fetch_commit_ids(self):
        commits = set()
        for branch, target in self.branches.items():
            logger.info(f"Ongoing Branch {branch}...")
            
            for commit in self.repo.walk(target, GIT_SORT_TOPOLOGICAL | GIT_SORT_TIME):
                if commit.oid not in commits:
                    commits.add(commit.oid)
                    self.queue.put(commit.oid)
                else:
                    break
                
                # print(datetime.utcfromtimestamp(commit.commit_time).strftime('%Y-%m-%d %H:%M:%S'))
        
        return commits
    
    def process(self):
        commits = self._fetch_commit_ids()
        GitParser(queue=self.queue)
        
        processes = [
            mp.Process(target=self._parse_commit, args=(oid,)) for oid in commits
        ]
        
        del commits
        
        start_time = default_timer()
        print('starting processes...')
        for process in processes:
            process.start()
        
        print(default_timer() - start_time)


class GitParser(mp.Process):
    def __init__(self, queue):
        super(GitParser, self).__init__()
        
        self.queue = queue
    
    def run(self):
        print('run')
    
    def fetch_commits(self):
        pass


if __name__ == '__main__':
    GitMiner(None)
