# Tether

*T*r*E*llo gi*TH*ub updat*ER*

Relies on [py-trello](https://github.com/sarumont/py-trello) and [PyGithub](https://github.com/PyGithub/PyGithub)

## Overall Process

1. Find any new Trello Cards that don't have a Github Issue with the same title.
2. Find any Github Issues that don't have a Trello Card with the same name.
3. For each new Trello Card, create a new Github Issue.
  * If the Trello Card contains Labels not in the Github Repo, they are created during this step. 
4. Close each Github issue that doesn't have an equivalent Trello Card.
5. Match up Trello Cards and Github Issues with the same Name/Title.
6. For each pair,
  * Address the Labels
    * If the Trello Card contains Labels not in the Github Repo, create them in the Github Repo.
    * Remove Labels from the Github Issue that aren't on the Trello Card.
  * Address the Comments
    * Find all the comments on the Trello Card not on the Github Issue. Add the comments to the Github Issue.
    * Find all the comments on the Github Issue not on the Trello Card. Add the comments to the Trello Card.
    
## Usage

1. Clone repo
2. Install requirements

```bash
pip install -r requirements.txt
```

3. Execute main.py, passing in the required arguments.

```bash
python main.py GithubRepoName "TrelloBoard With Spaces In Name" trello.json INFO
```

### Help

```bash
python main.py -h
usage: Trello Github Updater [-h]
                             github_repo trello_board trello_json_file
                             [{NOTSET,DEBUG,INFO,WARNING,ERROR,CRITICAL}]

positional arguments:
  github_repo           The name of the Github repo you want to migrate to.
  trello_board          The name of the Trello board you want to migrate from.
  trello_json_file      A json file containing the info required for logging
                        into your Trello account.
  {NOTSET,DEBUG,INFO,WARNING,ERROR,CRITICAL}
                        The level of logging/output this process should
                        provide.

optional arguments:
  -h, --help            show this help message and exit
```

## Trello.json

See the provided example trello.json. You'll need to collect the required info from https://trello.com/app-key

