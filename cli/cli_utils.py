# standard library
import sys
import os
sys.path.append('/home/viper/dev/GRAS')
import requests
import csv
#third party
import colorama
colorama.init()
import click
from PyInquirer import (Token, ValidationError, Validator, print_json, prompt,
                        style_from_dict, Separator)
from termcolor import colored
from pyfiglet import figlet_format

#modules
from components.query_engine.structs import *
from config import set_item, get_item, check



#----------------------------------------------------------------
# UTILITY FUNCTIONS
#---------------------------------------------------------------

style = style_from_dict({
    Token.QuestionMark: '#fac731 bold',
    Token.Answer: '#4688f1 bold',
    Token.Instruction: '',  # default
    Token.Separator: '#cc5454',
    Token.Selected: '#0abf5b',  # default
    Token.Pointer: '#673ab7 bold',
    Token.Question: '',
})


def log(string, color, font="slant", figlet=False):
    if colored:
        if not figlet:
            print(colored(string, color))
        else:
            print(colored(figlet_format(string, font=font), color))
    else:
        print(string)


#----------------------------------------------------------------
# VALIDATOR CLASSES
#----------------------------------------------------------------


class EmptyValidator(Validator):
    def validate(self, value):
        if len(value.text):
            return True
        else:
            raise ValidationError(message="You can't leave this blank",
                                  cursor_position=len(value.text))


#----TODO MAKE SURE THE USER CHOSES ATLEAST ONE STRUCT--------------------
class EmptyChoiceValidator(Validator):
    def validate(self, value):
        if len(value):
            return True
        else:
            raise ValidationError(message="You must choose at least one item")


#-----TODO: AUTHKEY VALIDATION---------args,kwargs
def auth_key_validator(auth_key):
    return True


class AuthKeyValidator(Validator):
    def validate(self, value):
        if len(value.text):
            if auth_key_validator(value.text) != True:
                raise ValidationError(message="invalid auth key",
                                      cursor_position=len(value.text))
        else:
            raise ValidationError(message="You can't leave this blank",
                                  cursor_position=len(value.text))


#-------TODO: USER/PASS VALIDATION---------
class UserValidator(Validator):
    def validate(self, value):
        if len(value.text):
            ok = requests.get("https://api.github.com/users/{}".format(
                value.text)).ok
            if ok != True:
                raise ValidationError(
                    message=f"The user {value.text} does not exist",
                    cursor_position=len(value.text))
            else:
                set_item("AUTH", "user_name", value.text)
        else:
            raise ValidationError(message="You can't leave this blank",
                                  cursor_position=len(value.text))


#---PASSWORDVALIDATOR----------------
#TODO
def pass_validator(user, password):
    return True


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
                ok = requests.get("https://api.github.com/repos/{}".format(
                    value.text)).ok
                if ok != True:
                    raise ValidationError(
                        message=f"The repo {value.text} does not exist",
                        cursor_position=len(value.text))

        else:
            raise ValidationError(message="You can't leave this blank",
                                  cursor_position=len(value.text))


#---------STRUCT GENERATOR-------------------
def gen_struct():
    path = './components/query_engine/structs'
    struct_files = []
    for (root,dirs,files) in os.walk('./components/query_engine/structs'):
        struct_files.append(files)
    struct_files = struct_files[0]
    


# #--------CSV GENERATOR-------------------
# def gen_csv_from_struct(struct):
#     repo = get_item("repo","name")
#     with open('{}_{}.csv'.format(repo,struct), w) as csv_file:
#         fieldnames = list()

gen_struct()