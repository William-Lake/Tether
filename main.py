
from argparse import ArgumentParser
import json
import logging
import random

from github_util import GithubUtil
from migration_util import MigrationUtil
from trello_util import TrelloUtil

def log_and_exit(message):

    logging.critical(message)

    exit(1)

def load_json(trello_json_file):

    try:

        trello_json = json.loads(open('trello_json_file','r').read())

    except:

        log_and_exit(f'Unable to load json file at {trello_json_file}!')

    for required_key in ['api_key','api_secret','token']:

        if required_key not in trello_json.keys():

            log_and_exit(f'{required_key} not in the json file!')

        if not trello_json[required_key].strip():

            log_and_exit(f'No json value for {required_key}!')

    return trello_json

def gather_args():

    arg_parser = ArgumentParser('Trello Github Updater')

    arg_parser.add_argument('github_repo',help='The name of the Github repo you want to migrate to.')

    arg_parser.add_argument('trello_board',help='The name of the Trello board you want to migrate from.')

    arg_parser.add_argument('trello_json_file',help='A json file containing the info required for logging into your Trello account.')

    arg_parser.add_argument('log_level',nargs='?',choices=['NOTSET','DEBUG','INFO','WARNING','ERROR','CRITICAL'],default='INFO',help='The level of logging/output this process should provide.')

    args = arg_parser.parse_args()

    return args.github_repo, args.trello_board, args.trello_json_file, args.log_level

if __name__ == "__main__":

    # https://docs.python.org/3/library/logging.html#logging-levels
    logging_level_value_dict = {
        'NOTSET':0,
        'DEBUG':10,
        'INFO':20,
        'WARNING':30,
        'ERROR':40,
        'CRITICAL':50
    }

    github_repo, trello_board, trello_json_file, log_level = gather_args()

    logging.basicConfig(level=logging_level_value_dict[log_level])

    trello_json = load_json(trello_json_file)    

    github_util = GithubUtil(github_repo)

    trello_util = TrelloUtil(trello_json, trello_board)

    migration_util = MigrationUtil(trello_util,github_util)

    migration_util.address_new_cards_old_issues()

    migration_util.compare_cards_issues(trello_util,github_util)



        
