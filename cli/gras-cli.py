from cli_utils import *
import click
from PyInquirer import (Token, ValidationError, Validator, prompt)
auth_choices = ['Use your gh auth key', 'use your username and password']


#----AUTH QUESTION---------------------
def ask_AUTH():
    questions = [
        {
            'type': 'list',
            'name': 'auth_option',
            'message': 'How would you like to authenticate?',
            'choices': auth_choices
        },
        {
            'type': 'input',
            'name': 'auth_key',
            'message': 'Enter your auth_key:',
            'when': lambda answers: answers['auth_option'] == auth_choices[0],
            'validate': AuthKeyValidator
        },
        {
            'type': 'input',
            'name': 'user_name',
            'message': 'Enter your github user name: ',
            'when': lambda answers: answers['auth_option'] == auth_choices[1],
            'validate': UserValidator
        },
    ]
    answers = prompt(questions, style=style)
    return answers


def ask_password():
    questions = [{
        'type': 'password',
        'name': 'password',
        'message': 'Enter your github password: ',
        'validate': PassValidator
    }]
    answers = prompt(questions, style=style)
    return answers


#---------REPO OWNER QUESTION-----------------
def ask_repo():
    questions = [{
        'type': 'input',
        'name': 'repo',
        'message': 'Enter name of the repo in the format <owner>/<repo>',
        'validate': RepoValidator
    }]
    answers = prompt(questions, style=style)
    return answers


structs = [{
    'name': 'repository details',
    'checked': True
}, {
    'name': 'branches'
}, {
    'name': 'languages'
}, {
    'name': 'issues'
}, {
    'name': 'issue comments'
}, {
    'name': 'milestones'
}, {
    'name': 'labels'
}, {
    'name': 'user pull requests'
}, {
    'name': 'releases'
}, {
    'name': 'stargazers'
}, {
    'name': 'watchers'
}]


def ask_struct():
    questions = [{
        'type': 'checkbox',
        'name': 'structs',
        'message': 'select what items you would like to parse',
        'choices': structs
        #'validate':
    }]
    answers = prompt(questions, style=style)
    return answers


@click.group()
def cli1():
    pass


@cli1.command()
def start():
    """
    Authenticate
    """
    #reset()
    log("GRAS", color="blue", figlet=True)
    log("Welcome to GRAS CLI", "green")
    log("Enter your authentication details", "blue")
    auth = ask_AUTH()
    if (auth["auth_option"] == auth_choices[0]):
        set_item("AUTH", "AUTH_KEY", auth["auth_key"])
    else:
        passwrd = ask_password()


@click.group()
def cli2():
    pass


@cli2.command()
def gen():
    """
    Generate Data
    """
    if check("AUTH", "AUTH_KEY") or check("AUTH", "user_name"):
        log("Enter your repo details", "blue")
        repo = ask_repo()
        set_item("repo", "owner", repo["repo"].split('/')[0])
        set_item("repo", "name", repo["repo"].split('/')[0])
        repo_name = get_item("repo", "name")
        repo_owner = get_item("repo", "owner")
        log(f"name: {repo_name}, owner: {repo_owner}", "green")
    else:
        log(
            "please enter authentication details first using the <start> command",
            "red")
        exit()
    struct = ask_struct()['structs']
    for item in struct:


cli = click.CommandCollection(sources=[cli1, cli2])

if __name__ == '__main__':
    cli()