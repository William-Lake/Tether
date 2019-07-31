import logging


class MigrationUtil(object):

    def __init__(self,trello_util,github_util):

        self.trello_util = trello_util

        self.github_util = github_util

    def address_new_cards_old_issues(self):

        self.gather_new_cards_stale_issues()
        
        self.migrate_cards_delete_issues()

    def gather_new_cards_stale_issues(self):

        logging.info('Determining cards to migrate and issues to delete')

        card_names = [
            card.name
            for card
            in self.trello_util.cards
        ]

        issue_titles = [
            issue.title
            for issue
            in self.github_util.issues
        ]

        self.new_card_names = list(set(card_names) - set(issue_titles))

        self.stale_issue_titles = list(set(issue_titles) - set(card_names))

    def migrate_cards_delete_issues(self):

        if self.new_card_names or self.stale_issue_titles:

            logging.info(f'{len(self.new_card_names)} cards to migrate and {len(self.stale_issue_titles)} issues to close')

            cards_to_migrate = [
                card
                for card
                in self.trello_util.cards
                if card.name in self.new_card_names
            ]

            issues_to_delete = [
                issue
                for issue
                in self.github_util.issues
                if issue.title in self.stale_issue_titles
            ]

            if cards_to_migrate:

                logging.info('Migrating new cards to github')

                for card in cards_to_migrate:

                    logging.info(f'Migrated card: {card.name}')

                    self.github_util.add_new_issue(card)


            if issues_to_delete:

                logging.info('Deleting stale issues from github')

                for issue in issues_to_delete:

                    logging.info(f'Closed issue: {issue.title}')

                    issue.edit(state='closed')

        else:

            logging.info('No new cards to migrate or issues to close.')

    def compare_cards_issues(self):

        for card in self.trello_util.cards:

            for issue in self.github_util.issues:

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

            issue.edit(labels=new_issue_labels)

