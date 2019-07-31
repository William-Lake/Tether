from github import Github
import getpass
import logging
import random

class GithubUtil(object):
    '''
    '''
    def __init__(self,github_repo):

        logging.info('Signing into Github')

        username = self.gather_username()

        self.github = Github(username, getpass.getpass())

        self.user = self.github.get_user(login=username)

        try:

            self.target_repo = self.user.get_repo(name=github_repo.strip())

        except:

            logging.critical(f'Unable to find repo named {github_repo} for {username}!')

            exit(1)

        self.issues = self.target_repo.get_issues(state='all')

    def gather_username(self):

        while True:

            user_name = input('Username: ').strip()

            if not user_name: print('Please provide a Username.')

            else: return user_name

    def add_new_issue(self,card):

        logging.info(f'Creating new issue for card "{card.name}"')

        issue_labels = self.determine_new_issue_labels_for_card(card)

        new_issue = self.target_repo.create_issue(card.name,body=card.description,labels=issue_labels)

        self.copy_comments(card,new_issue)
        '''
        title
        labels
        '''

    def determine_new_issue_labels_for_card(self,card):

        logging.info(f'Determing new issue labels for card "{card.name}"')

        issue_labels = []

        for card_label in card.labels:

            repo_label = self.get_repo_label_by_name(card_label.name)

            if repo_label is None:

                repo_label = self.create_label(card_label.name)

            issue_labels.append(repo_label)

        return issue_labels

    def get_repo_label_by_name(self,label_name):

        logging.info(f'Gathering repo label named {label_name}')

        for repo_label in self.target_repo.get_labels():

            if repo_label.name == label_name:

                return repo_label

        return None

    def create_label(self,card_label):

        logging.info(f'Creating label with name {card_label}')

        random_color_num_func = lambda: random.randint(0,255)

        label_color = f'#{random_color_num_func():02x}{random_color_num_func():02x}{random_color_num_func():02x}'

        logging.info(f'New label color is {label_color}')

        return self.target_repo.create_label(card_label.name, label_color)

    def copy_comments(self,card,new_issue):

        logging.info(f'Copying comments from card to new issue for {card.name}')

        for comment in card.get_comments():

            new_issue.create_comment(comment)

    def create_labels_not_existing(self,card):

        if card.labels:

            for card_label in card.labels:

                repo_label = self.get_repo_label_by_name(card_label.name)

                if repo_label is None:

                    self.create_label(card_label.name)

        else:

            logging.info('Card has no labels')

    @staticmethod
    def is_issue_in_progress(issue):

        issue_label_names = [
            issue_label.name
            for issue_label
            in issue.labels
        ]

        return 'In Progress' in issue_label_names
