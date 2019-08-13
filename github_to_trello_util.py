import logging


class GithubToTrelloUtil(object):

    def __init__(self,trello_util,github_util):

        self.trello_util = trello_util

        self.github_util = github_util

    def migrate(self):

        '''
        Tether is meant to go only from Trello to Github,
        so this functionality is limited.
        It's meant to be used in the circumstances when
        you already have a Github project with issues-
        but you just created a Trello board for it.
        This way you can copy over all your github issues
        to Trello before using Tether normally.
        Otherwise all of your Github issues will be closed.
        '''

        for issue in self.github_util.open_issues:

            if not self.trello_util.card_with_name_exists(issue.title):

                self.trello_util.create_card_for_issue_in_list(issue,'To Do')

        for issue in self.github_util.closed_issues:

            if not self.trello_util.card_with_name_exists(issue.title):

                self.trello_util.create_card_for_issue_in_list(issue,'Done')