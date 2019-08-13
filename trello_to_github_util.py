import logging


class TrelloToGithubUtil(object):

    def __init__(self,trello_util,github_util):

        self.trello_util = trello_util

        self.github_util = github_util

    def migrate(self):

        self.identify_changes()
        
        self.apply_changes()

    def identify_changes(self):

        logging.info('Determining cards to migrate and issues to delete')

        '''
        If a card is in Trello and not in Github
            If there's an equivalent github issue that's been closed
                Make the comparisons re: labels/comments
                Move the card to the "Done" list
            Else
                Make the github issue
        '''

        card_names = [
            card.name
            for card
            in self.trello_util.cards
        ]

        open_issue_titles = [
            issue.title
            for issue
            in self.github_util.open_issues
        ]

        closed_issue_titles = [
            issue.title
            for issue
            in self.github_util.closed_issues
        ]

        # Cards in trello not in github's open issues
        self.names_of_cards_to_create = list(set(card_names) - set(open_issue_titles))

        # Issues closed in github in and in Trello
        self.names_of_cards_to_move_to_done = [
            card_name
            for card_name
            in list(set(closed_issue_titles) & set(card_names))
        ]

        # TODO May be able to improve this.
        self.names_of_cards_to_create = [
            card_name
            for card_name
            in self.names_of_cards_to_create
            if card_name not in self.names_of_cards_to_move_to_done
        ]

        # Open Issues in github, not in Trello
        self.titles_of_issues_to_close = list(set(open_issue_titles) - set(card_names))

    def apply_changes(self):

        if self.names_of_cards_to_create:

            logging.info(f'{len(self.names_of_cards_to_create)} issues to create in Github')

            for card_name in self.names_of_cards_to_create:

                card = self.trello_util.get_card_by_name(card_name)

                logging.info(f'Migrated card: {card.name}')

                self.github_util.add_new_issue(card)

        if self.names_of_cards_to_move_to_done:

            logging.info(f'{len(self.names_of_cards_to_move_to_done)} cards to move to "Done"')

            for card_name in self.names_of_cards_to_move_to_done:

                card = self.trello_util.get_card_by_name(card_name)

                if card.get_list().name != 'Done':

                    logging.info(f'Moved card: {card.name}')

                    self.trello_util.move_card_to_done(card)

        if self.titles_of_issues_to_close:

            logging.info(f'{len(self.titles_of_issues_to_close)} issues in Github to close')

            for issue_title in self.titles_of_issues_to_close:

                issue = self.github_util.get_issue_by_title(issue_title)

                logging.info(f'Closed issue: {issue.title}')

                issue.edit(state='closed')

    def compare_cards_issues(self):

        logging.info('Comparing cards and issues')

        for card in self.trello_util.cards:

            for issue in self.github_util.open_issues:

                if card.name.upper().strip() == issue.title.upper().strip():

                    self.address_labels(card,issue)

                    self.address_comments(card,issue)
                    
                    break

    def address_comments(self,card,issue):

        logging.info('Addressing comments')

        issue_comments = [
            issue_comment.body
            for issue_comment
            in issue.get_comments()
        ]

        card_comments = [
            comment['data']['text']
            for comment
            in card.get_comments()
        ]

        new_issue_comments = list(set(card_comments) - set(issue_comments))

        new_card_comments = list(set(issue_comments) - set(card_comments))

        if new_issue_comments:

            logging.info(f'Adding {len(new_issue_comments)} new card comments to issue')

            for issue_comment in new_issue_comments:

                try:

                    issue.create_comment(issue_comment)

                except:

                    logging.error(f'Unable to add a comment to the issue! "{issue_comment}"')

        if new_card_comments:

            logging.info(f'Adding {len(new_card_comments)} new issue comments to card')

            for card_comment in new_card_comments:

                try: 
                    
                    card.comment(card_comment)

                except:

                    logging.error(f'Unable to add a comment to the card! "{card_comment}"')

                    continue

    def address_labels(self,card,issue):

        logging.info('Creating labels new to github')

        self.github_util.create_labels_not_existing(card)

        logging.info('Removing labels from github issue not on trello card')

        # Identify labels that need to be added/removed

        issue_label_dict = {}

        card_label_dict = {}

        for issue_label in issue.labels:

            issue_label_dict[issue_label.name] = issue_label

        if card.labels:

            for card_label in card.labels:

                card_label_dict[card_label.name] = card_label

        else:

            logging.info('Card has no labels')

        labels_to_remove = [
            issue_label_name
            for issue_label_name
            in issue_label_dict.keys()
            if issue_label_name not in card_label_dict.keys()
        ]

        labels_to_add = [
            card_label_name
            for card_label_name
            in card_label_dict.keys()
            if card_label_name not in issue_label_dict.keys()
        ]

        logging.info(f'There are {len(labels_to_remove)} labels to remove and {len(labels_to_add)} labels to add')

        # Apply changes to intermediary label list

        new_issue_labels = issue.labels

        for label_name in labels_to_remove:

            new_issue_labels.remove(issue_label_dict[label_name])

        for label_name in labels_to_add:

            new_issue_labels.append(self.github_util.target_repo.get_label(label_name))

        # Make changes
        if labels_to_remove or labels_to_add:

            logging.info('Making changes to issue labels')

            new_issue_labels = [
                label.name
                for label
                in new_issue_labels
            ]

            issue.edit(labels=new_issue_labels)

