from pyfiglet import Figlet
import os
import re
import click
import colorama
colorama.init()
import json
from conf import get_item , set_item, reset
from PyInquirer import (Token, ValidationError, Validator, print_json, prompt,
                        style_from_dict,Separator)
from termcolor import colored
from pyfiglet import figlet_format
import requests
# value = 'sympy'
# ok = requests.get("https://api.github.com/repos/sympy/{}".format(value)).ok
# print(ok)


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

def log(string, color, font = "slant",figlet=False):
    if colored:
        if not figlet:
            print(colored(string,color))
        else:
            print(colored(figlet_format(string,font=font),color))
    else:
        print(string)

#----CHECKS IF INPUT IS EMPTY----------

class EmptyValidator(Validator):
    def validate(self, value):
        if len(value.text):
            return True
        else:
            raise ValidationError(
                message="You can't leave this blank",
                cursor_position=len(value.text))

#-----TODO: AUTHKEY VALIDATION---------
class AuthKeyValidator(Validator):
    def validate(self,value):
        if len(value.text):
            return True
        else:
            raise ValidationError(
            message="You can't leave this blank",
            cursor_position=len(value.text))

#-------TODO: USER/PASS VALIDATION---------
class PassValidator(Validator):
    def validate(self,value):
        if len(value.text):
            return True
        else:
            raise ValidationError(
            message="You can't leave this blank",
            cursor_position=len(value.text))

#-------CHECKS IF REPO EXISTS---TODO: currently if the user gets the owner wrong, he has to restart the\
#         whole thing, need to find fix or the alternative is that we ask them in the format <owner>/<name>
class RepoValidator(Validator):
    def validate(self, value):
        if len(value.text):
            owner = get_item("repo","owner")
            ok = requests.get("https://api.github.com/repos/{}/{}".format(owner,value.text)).ok
            if ok != True:
                raise ValidationError(
                    message=f"The repo {value.text} does not exist",
                    cursor_position=len(value.text))
        else:
            raise ValidationError(
                message="You can't leave this blank",
                cursor_position=len(value.text))


auth_choices = ['Use your gh auth key',
                'use your username and password']

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
            'type' : 'input',
            'name' : 'auth_key',
            'message': 'Enter your auth_key:',
            'when' : lambda answers: answers['auth_option'] == auth_choices[0],
            'validate': AuthKeyValidator
        },
        {
            'type' : 'input',
            'name' : 'user_name',
            'message': 'Enter your github user name: ',
            'when' : lambda answers: answers['auth_option'] == auth_choices[1],
            'validate': EmptyValidator
        },
        {
            'type' : 'password',
            'name' : 'password',
            'message': 'Enter your github password: ',
            'when' : lambda answers: answers['auth_option'] == auth_choices[1] and answers['user_name'],
            'validate': PassValidator
        },
    ]
    answers = prompt(questions, style=style)
    return answers

#---------REPO OWNER QUESTION-----------------
def ask_repo_owner():
    questions = [
        {
            'type': 'input',
            'name': 'owner',
            'message': 'Enter name of the owner',
            'validate': EmptyValidator
        }
    ]
    answers = prompt(questions, style=style)
    return answers

#------------------REPO NAME QUESTION----------------
def ask_repo_name():
    questions = [
        {
            'type': 'input',
            'name': 'name',
            'message': 'Enter name of the name',
            'validate': RepoValidator
        }
    ]
    answers = prompt(questions, style=style)
    return answers



@click.command()
def main():
    """
    CLI for mining repository data
    """
    log("GRAS", color="blue", figlet=True)
    log("Welcome to GRAS CLI", "green")

    log("Enter your authentication details", "blue")
    auth = ask_AUTH()
    if(auth["auth_option"] == auth_choices[0]):
        set_item("AUTH", "AUTH_KEY",auth["auth_key"])
    else:   
        set_item("AUTH", "user_name",auth["user_name"])
        set_item("AUTH", "password",auth["password"])
    log(f"{auth}", "green")

    log("Enter your repo details", "blue")
    owner = ask_repo_owner()
    set_item("repo","owner",owner["owner"])
    name = ask_repo_name()
    set_item("repo","name",name["name"])
    repo_name = get_item("repo","owner")
    log(f"{repo_name}", "green")
    reset()

if __name__ == '__main__':
    main()
