**************************
Quickstart for using GRAS
**************************

A quick example showing you how to use GRAS to mine a repository

.. contents:: Table of Contents

Install
=======

Install using pip:

.. code:: console

    $ pip install gras

.. note::
    note about versions/folder/environement

Install via source code:

.. code:: console

    $git clone 'githublink'

Create necessary files/directories(?)
======================================
There are certain files and directories required

.. code:: console

    $ mkdir db

Adding a directory to hold your database

.. code:: console

   $ cd db
   $ touch file.db

make a database file to store data..

Checking the stats of a repo
===============================

.. code:: console

    $ gras -RO sympy -RN sympy -t <GITHUB AUTH TOKEN> -s


will return:

.. code-block:: console

    {
        "branches": {
            "1.6": {
                "total_commit_comments": 130,
                "total_commits": 42859
            },
            "master": {
                "total_commit_comments": 130,
                "total_commits": 42958
            },
            "revert-14280-zero_vector": {
                "total_commit_comments": 130,
                "total_commits": 31321
            },
            "revert-19179-pypi": {
                "total_commit_comments": 130,
                "total_commits": 42891
            }
        },
        "total_anon_contributors": 512,
        "total_assignees": 45,
        "total_contributors": 440,
        "total_forks": 2950,
        "total_issues": 0,
        "total_labels": 120,
        "total_languages": 7,
        "total_milestones": 53,
        "total_pull_requests": 0,
        "total_releases": 25,
        "total_stargazers": 6944,
        "total_tags": 68,
        "total_watchers": 306
    }








