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

            if board_label.name.upper() == label_name.upper():

                return board_label

        return None

    def create_label(self,label_name):

        label_color = random.choice(self.label_colors)

        return self.target_board.add_label(label_name,label_color)

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

        target_cards = [
            card
            for card
            in self.cards
            if card.name == card_name
        ]

        if target_cards:

            return target_cards[0]

        else:

            return None

    def card_with_name_exists(self,card_name):

        logging.info(f'Checking if card named "{card_name}" already exists.')

        if self.get_card_by_name(card_name) is None:

            target_cards = [
                card
                for card
                in self.target_board.closed_cards()
                if card.name == card_name
            ]

            if target_cards:

                return True

            else:

                return False

        return True


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

    def get_trello_labels_for_issue(self,issue):

        labels = [
            self.get_board_label_by_name(issue_label.name)
            for issue_label
            in issue.labels
        ]

        return labels

    def create_card_for_issue_in_list(self,issue,list_name):

        logging.info(f'Creating new card for issue "{issue.title}"')

        self.create_labels_not_existing(issue)

        card_labels = self.get_trello_labels_for_issue(issue)

        target_list = self.get_list_by_name(list_name)

        new_card = target_list.add_card(name=issue.title, labels=card_labels)

        self.copy_comments(issue,new_card)

    def get_list_by_name(self,list_name):

        logging.info(f'Gathering list named {list_name}')

        target_lists = [
            trello_list
            for trello_list
            in self.target_board.all_lists()
            if trello_list.name == list_name
        ]

        if target_lists:

            return target_lists[0]

        else:

            logging.error(f'Unable to find list named {list_name}!')

            exit(1)