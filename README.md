[![Python 3.6](https://img.shields.io/badge/python-3.6-blue.svg)](https://www.python.org/downloads/release/python-360/) [![License](https://img.shields.io/badge/License-BSD%203--Clause-orange.svg)](https://opensource.org/licenses/BSD-3-Clause)

# GRAS (Git Repositories Archiving Service)

Git Repository Mining Service (GRAS) is a tool designed to thoroughly mine software repositories. Software repository data has become the foundation of many empirical software engineering research projects such as sentiment mining, developer social networks, etc. However, the mining and collection of this data proves to be very challenging due to the density and connectedness of each component. GRAS was built due to the need for cleaner and coherent organization of mined data and optimization of the mining process. It is capable of mining a repository from various version control systems and storing it into more than 3 types of databases in a harmonized way. GRAS also has a built-in file dependency analyzer (currently, Java & Python are only supported) that parses the entire project and creates a heterogenous graph representing the file relationships and their dependencies on each other. The file dependency graph is stored in a Neo4j database. We are currently working on the Identity Merging Component. 

## Installation

1. Clone this repository: `$ git clone https://github.com/imlegend19/GRAS.git`
2. `$ cd GRAS`
3. Create a virtual environment: 
   ```
   $ python3 -m venv venv
   $ source venv/bin/activate
   ``` 
4. Install the requirements: `$ pip install requirements.txt`
   - *Note:* If you get error while installing mysqlclient, try running the following:
      ```
      sudo apt-get install python3-dev libmysqlclient-dev
      ```
   - *Note:* If you get `error building wheel` error while installing `pycparser` or `neo4j`, try running this:
      ```
      pip install wheel
      ```
5. Bingo! The setup is now complete.

## Usage

```
usage: python3 main.py [-g [GENERATE]] [-m [MINE]] [-s [STATS]] [-B [BASIC]]
               [-BE [BASIC_EXTRA]] [-IT [ISSUE_TRACKER]] [-CD [COMMIT]]
               [-PT [PULL_TRACKER]] [-CS CHUNK_SIZE] [-f [FULL]] [--path PATH]
               [--aio [AIO]] [-t TOKENS [TOKENS ...]] [-yk YANDEX_KEY]
               [-i {github,git,identity-merging,java-cda,java-miner}]
               [-RO REPO_OWNER] [-RN REPO_NAME] [-SD START_DATE]
               [-ED END_DATE] [-c CONFIG]
               [-dbms {sqlite,mysql,postgresql,neo4j}] [-DB DB_NAME]
               [-U DB_USERNAME] [-P [DB_PASSWORD]] [-H DB_HOST] [-p DB_PORT]
               [-dbo DB_OUTPUT] [-dbl [DB_LOG]] [-h]
               [-a {arrow,eclipse,dots_1,dots_2,birds,dash,cycle,rod,bar,balloon}]
               [-OP {1,2,3}] [-CL [CLEAR_LOGS]] [-o OUTPUT]

GRAS - GIT REPOSITORIES ARCHIVING SERVICE

GRAS-COMMANDS:
  -g [GENERATE], --generate [GENERATE]
                        Generate a config file template
  -m [MINE], --mine [MINE]
                        Mine the repository
  -s [STATS], --stats [STATS]
                        View the stats of the repository
  -B [BASIC], --basic [BASIC]
                        Mining Stage 1-A: Basic
  -BE [BASIC_EXTRA], --basic-extra [BASIC_EXTRA]
                        Mining Stage 1-B: Basic Extra
  -IT [ISSUE_TRACKER], --issue-tracker [ISSUE_TRACKER]
                        Mining Stage 2: Issue Tracker
  -CD [COMMIT], --commit [COMMIT]
                        Mining Stage 3: Commit Data
  -PT [PULL_TRACKER], --pull-tracker [PULL_TRACKER]
                        Mining Stage 4: Pull Request Tracker
  -CS CHUNK_SIZE, --chunk-size CHUNK_SIZE
                        Time Period Chunk Size (in Days)
  -f [FULL], --full [FULL]
                        Mine the complete repository
  --path PATH           Path to the directory to mine
  --aio [AIO]           If added, git-miner would use asyncio architecture

GRAS-SETTINGS:
  -t TOKENS [TOKENS ...], --tokens TOKENS [TOKENS ...]
                        List of Personal API Access Tokens for parsing
  -yk YANDEX_KEY, --yandex-key YANDEX_KEY
                        Yandex Translator API Key
                        (https://translate.yandex.com/developers/keys)
  -i {github,git,identity-merging,java-cda,java-miner}, --interface {github,git,identity-merging,java-cda,java-miner}
                        Interface of choice
  -RO REPO_OWNER, --repo-owner REPO_OWNER
                        Owner of the repository
  -RN REPO_NAME, --repo-name REPO_NAME
                        Name of the repository
  -SD START_DATE, --start-date START_DATE
                        Start Date for mining the data (in any ISO 8601
                        format, e.g., 'YYYY-MM-DD HH:mm:SS +|-HH:MM')
  -ED END_DATE, --end-date END_DATE
                        End Date for mining the data (in any ISO 8601 format,
                        e.g., 'YYYY-MM-DD HH:mm:SS +|-HH:MM')
  -c CONFIG, --config CONFIG
                        Path to the config file

DATABASE-SETTINGS:
  -dbms {sqlite,mysql,postgresql,neo4j}
                        DBMS to dump the data into
  -DB DB_NAME, --db-name DB_NAME
                        Name of the database
  -U DB_USERNAME, --db-username DB_USERNAME
                        The user name that is used to connect and operate the
                        selected database
  -P [DB_PASSWORD], --db-password [DB_PASSWORD]
                        The password for the user name entered
  -H DB_HOST, --db-host DB_HOST
                        The database server IP address or DNS name
  -p DB_PORT, --db-port DB_PORT
                        The database server db_port that allows communication
                        to your database
  -dbo DB_OUTPUT, --db-output DB_OUTPUT
                        The path to the .db file in case of sqlite dbms
  -dbl [DB_LOG], --db-log [DB_LOG]
                        DB-log flag to log the generated SQL produced

OTHER:
  -h, --help            show this help message and exit
  -a {arrow,eclipse,dots_1,dots_2,birds,dash,cycle,rod,bar,balloon}, --animator {arrow,eclipse,dots_1,dots_2,birds,dash,cycle,rod,bar,balloon}
                        Loading animator
  -OP {1,2,3}, --operation {1,2,3}
                        Choose the operation to perform for retrieving the
                        stats.: 1. CREATE, 2. UPDATE, 3. APPEND
  -CL [CLEAR_LOGS], --clear-logs [CLEAR_LOGS]
                        Clear the logs directory
  -o OUTPUT, --output OUTPUT
                        The output path where the config file is to be
                        generated
```
