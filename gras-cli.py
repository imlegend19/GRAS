from pyfiglet import Figlet
import os
import re
import click
import colorama
colorama.init()
import json
from conf import *
from PyInquirer import (Token, ValidationError, Validator, print_json, prompt,
                        style_from_dict, Separator)
from termcolor import colored
from pyfiglet import figlet_format
import requests

#--------Adds color----------------
style = style_from_dict({
    Token.QuestionMark: '#fac731 bold',
    Token.Answer: '#4688f1 bold',
    Token.Instruction: '',  # default
    Token.Separator: '#cc5454',
    Token.Selected: '#0abf5b',  # default
    Token.Pointer: '#673ab7 bold',
    Token.Question: '',
})

#-------OUTPUT COLORED TEXT-------


def log(string, color, font="slant", figlet=False):
    if colored:
        if not figlet:
            print(colored(string, color))
        else:
            print(colored(figlet_format(string, font=font), color))
    else:
        print(string)


#TODO: MAYBE ADD ALL VALIDATOR CLASSES IN A SEPARATE UTILS FILE, INSTEAD OF CALLING THE API FROM conf.py
#----CHECKS IF INPUT IS EMPTY----------


class EmptyValidator(Validator):
    def validate(self, value):
        if len(value.text):
            return True
        else:
            raise ValidationError(message="You can't leave this blank",
                                  cursor_position=len(value.text))


#-----TODO: AUTHKEY VALIDATION---------args,kwargs
class AuthKeyValidator(Validator):
    def validate(self, value):
        if len(value.text):
            if auth_key_validator(value.text) != True:
                raise ValidationError(message="invalid auth key",
                                      cursor_position=len(value.text))
            else:
                set_item("AUTH", "AUTH_KEY", value.text)
        else:
            raise ValidationError(message="You can't leave this blank",
                                  cursor_position=len(value.text))


#-------TODO: USER/PASS VALIDATION---------
class UserValidator(Validator):
    def validate(self, value):
        if len(value.text):
            ok = user_validator(value.text)
            if ok != True:
                raise ValidationError(
                    message=f"The user {value.text} does not exist",
                    cursor_position=len(value.text))
            else:
                set_item("AUTH", "user_name", value.text)
        else:
            raise ValidationError(message="You can't leave this blank",
                                  cursor_position=len(value.text))


#---PASSWORDVALIDATOR-------------
class PassValidator(Validator):
    set_item("AUTH", "pass_attempts", '1')

    def validate(self, value):
        pass_attempts = int(get_item("AUTH", "pass_attempts"))
        if len(value.text):
            user = get_item("AUTH", "user_name")
            if pass_validator(user, value.text) != True and pass_attempts <= 3:
                set_item("AUTH", "pass_attempts", str(pass_attempts + 1))
                raise ValidationError(
                    message=f"Wrong Password attempt#{pass_attempts}",
                    cursor_position=len(value.text))
            elif pass_attempts > 3:
                raise click.UsageError("ENTERED INVALID PASSWORD 3 TIMES")
            else:
                set_item("AUTH", "password", value.text)
        else:
            raise ValidationError(message="You can't leave this blank",
                                  cursor_position=len(value.text))


#-------CHECKS IF REPO EXISTS--
class RepoValidator(Validator):
    def validate(self, value):
        if len(value.text):
            if '/' not in value.text:
                raise ValidationError(
                    message="input has to be in the format <owner>/<repo>",
                    cursor_position=len(value.text))
            else:
                ok = repo_validator(value.text)
                if ok == True:
                    set_item("repo", "owner", value.text.split('/')[0])
                    set_item("repo", "name", value.text.split('/')[0])
                else:
                    raise ValidationError(
                        message=f"The repo {value.text} does not exist",
                        cursor_position=len(value.text))

        else:
            raise ValidationError(message="You can't leave this blank",
                                  cursor_position=len(value.text))


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
        {
            'type':
            'password',
            'name':
            'password',
            'message':
            'Enter your github password: ',
            'when':
            lambda answers: answers['auth_option'] == auth_choices[1] and
            answers['user_name'],
            'validate':
            PassValidator
        },
    ]
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


@click.command()
def start():
    """
    CLI for mining repository data
    """
    #reset()

    log("GRAS", color="blue", figlet=True)
    log("Welcome to GRAS CLI", "green")
    log("Enter your authentication details", "blue")
    ask_AUTH()

    log("Enter your repo details", "blue")
    ask_repo()
    repo_name = get_item("repo", "name")
    repo_owner = get_item("repo", "owner")
    log(f"name: {repo_name}, owner: {repo_owner}", "green")


if __name__ == '__main__':
    start()
