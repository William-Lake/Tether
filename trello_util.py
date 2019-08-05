import logging
from trello import TrelloClient
import random

from github_util import GithubUtil

class TrelloUtil(object):

    def __init__(self,trello_json,trello_board):

        logging.info('Signing into Trello')

        self.client = TrelloClient(
            api_key=trello_json['api_key'].strip(),
            api_secret=trello_json['api_secret'].strip(),
            token=trello_json['token'].strip(),
            token_secret=trello_json['token_secret'].strip()
        )

        self.target_board = None

        for board in self.client.list_boards():

            if board.name.upper().strip() == trello_board.upper().strip():

                self.target_board = board

                break

        if self.target_board is None:

            logging.critical(f'Unable to find trello board named {trello_board}!')

            exit(1)

        # self.organize_lists()

        self.cards = self.target_board.open_cards()

        self.label_colors = ['green','yellow','orange','red','purple','blue','sky','lime','pink','black']

        self.done_list = None

    def get_board_label_by_name(self,label_name):

        logging.info('Gathering board label by name')

        for board_label in self.target_board.get_labels():

            if board_label.name == label_name:

                return board_label

        return None

    def create_label(self,label_name):

        label_color = random.choice(self.label_colors)

        return self.target_board.add_label(issue_label.name,label_color)

    def copy_comments(self,issue,new_card):

        for comment in issue.get_comments():

            try:

                new_card.comment(comment.body)

            except:

                logging.error('Error while trying to add comment!')

    def create_labels_not_existing(self,issue):

        new_labels = []

        for issue_label in issue.labels:

            board_label = self.get_board_label_by_name(issue_label.name)

            if board_label is None:

                new_labels.append(self.create_label(issue_label.name))

        return new_labels

    def get_card_by_name(self,card_name):

        return [
            card
            for card
            in self.cards
            if card.name == card_name
        ][0]

    def move_card_to_done(self,card):

        if self.done_list is None:

            self.done_list = [
                board_list
                for board_list
                in self.target_board.all_lists()
                if board_list.name == 'Done'
            ][0]

        moved_card = self.done_list.add_card(card.name,source=card.id)

        card.delete()

    # Not used at the moment, but used when going from Github to Trello.
    # def organize_lists(self):

    #     logging.info('Organizing Lists')

    #     for this_list in self.target_board.all_lists():

    #         if this_list.name == 'To Do':

    #             self.todo_list = this_list

    #         elif this_list.name == 'Doing':

    #             self.doing_list = this_list

    #         elif this_list.name == 'Done':

    #             self.done_list = this_list

    # Not used at the moment, but used when going from Github to Trello.
    # def add_new_card(self,issue):

    #     logging.info('Adding new card')

    #     target_list = self.determine_list_for_issue(issue)

    #     new_card_labels = self.determine_new_card_labels_for_issue(issue)

    #     new_card = target_list.add_card(name=issue.title, labels=new_card_labels)

    #     self.copy_comments(issue,new_card)

    # Not used at the moment, but used when going from Github to Trello.
    # def determine_list_for_issue(self,issue):

    #     logging.info('Determining list for issue')

    #     target_list = None

    #     if issue.state == 'closed':

    #         target_list = self.done_list

    #     elif GithubUtil.is_issue_in_progress(issue):

    #         target_list = self.doing_list

    #     else:

    #         target_list = self.todo_list

    #     return target_list

    # Not used at the moment, but used when going from Github to Trello.
    # def determine_new_card_labels_for_issue(self,issue):

    #     logging.info('Determining card labels for issue')

    #     card_labels = []

    #     for issue_label in issue.labels:

    #         board_label = self.get_board_label_by_name(issue_label.name)

    #         if board_label is None:

    #             self.create_label(issue_label.name)

    #         card_labels.append(board_label)

    #     return card_labels