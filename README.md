# DBT2021 - Pipette robot automation
## Git/Github setup:
Based on instructions from https://towardsdatascience.com/simple-github-integration-with-vscode-3d7a3db33047 with some additions and modifications. 
### Install all requirements
1. Create an account on GitHub.
2. Install Git from https://git-scm.com/
3. Install GitHub extension for VSCode https://marketplace.visualstudio.com/items?itemName=GitHub.vscode-pull-request-github

### Create local repo
1. Open new window in VSCode (no file or folder selected).
2. Select Clone Git Repository and enter url https://github.com/M-Jonsson/dbt2021.git 
3. Select a folder to locally store the files.

### Update user credentials
1. In VSCode, open a terminal (terminal -> new terminal in the toolbar on top).
2. In the terminal window, select Terminal
3. Open a Git Bash terminal by pressing the small arrow to the right of the plus button (Launch profile...) and select Git Bash.
4. In the Git Bash terminal enter:
'''
git config user.name <your GitHub username>
git config user.email <the email address of you GitHub account>
'''

## Using GitHub with VSCode
For larger changes, create a fork/branch from the main repo. (Comprabale to making a copy of all files and making edits to those [create a branch], then deleting the old files after everything works [merging to main with a pull request]).
For smaller changes, the changes can be direclty commited.
### Large changes - creating a fork/branch
1. Press the branch button in the lower left corner (should be on the main branch by default). 
2. Select "create a new branch..." and enter a name.
3. Edit files.
4. Commit changes to the new branch (see next section).
5. When done, create a pull request to merge the current branch into the main branch 
### Commiting changes
A modified file will have a "M" symbol to show that the edits are only done on the local files. They must be commited to edit the file on the GitHub. The same applies to deleted or new files, but with different symbols. 
1. Select source control on the left panel.
2. The relevant file can be opened to compare changes.
3. If happy with the changes, select "stage changes" (plus symbol beside the file name). Staging is mid-step in updating the GitHub files in case several files have been edited locally but only some should be uploaded.
4. When all files that should be uploaded have been staged, enter a messege to describe the changes and press the Commit button (check mark) at the top of the source control pane.
5. Finally, sync changes to update the GitHub files with the commit. 
