import os.path
import pickle
import re
from typing import Dict

from model import Issue

ISSUE_NOT_FOUND = "Issue not found"
TIRADATA_PICKLE = "tiradata.pickle"


class Controller:
    def __init__(self):
        self.issues: Dict[str, Issue] = {}
        self.is_running = True
        self.next_id = 1
        self.tira_space = "TI"
        self.load()

    def save(self):
        with open(TIRADATA_PICKLE, "wb") as f:
            pickle.dump(self.issues, f)

    def load(self):
        if os.path.exists(TIRADATA_PICKLE):
            with open(TIRADATA_PICKLE, "rb") as f:
                self.issues = pickle.load(f)
                self.next_id = max(int(key.split("-")[1]) for key in self.issues) + 1

    def run(self):
        while self.is_running:
            actions = {
                "add": self.add,
                "list": self.list,
                "show": self.show,
                "delete": self.delete,
                "edit": self.edit,
                "exit": self.quit,
                "help": self.help,
                "space": self.space,
                "spaces": self.spaces,
            }
            print("")
            action, *args = input(f"tira: {self.tira_space}> ").split()
            if action not in actions:
                print("Unknown action")
                continue
            actions[action](*args)

    def space(self, space=None):
        if not space or not re.search(r"^[A-Z]{2,3}$", space):
            print("Space must be two or three capital letters")
            return
        self.tira_space = space

    def spaces(self):
        spaces = set(key.split("-")[0] for key in self.issues)
        print(" ".join(sorted(spaces)))

    def add(self):
        key = f"{self.tira_space}-{self.next_id}"
        self.next_id += 1
        description = input("Description: ")
        self.issues[key] = Issue(key, description)
        self.save()
        print("Added issue")

    def list(self):
        for issue in [iss for iss in self.issues.values() if iss.key.startswith(self.tira_space)]:
            formatted_date = issue.created.strftime("%Y-%m-%d %H:%M")
            print(f"{issue.key}\t{formatted_date}\t{repr(issue.description)}")

    def show(self, key):
        issue = self.issues.get(key, None) or self.issues.get(f"{self.tira_space}-{key}", None)
        if issue is None:
            print(ISSUE_NOT_FOUND)
            return
        print(issue.key)
        print(issue.description)
        print(issue.created)

    def delete(self, key):
        issue = self.issues.get(key, None) or self.issues.get(f"{self.tira_space}-{key}", None)
        if issue is None:
            print(ISSUE_NOT_FOUND)
            return
        del self.issues[key]
        self.save()
        print("Deleted issue")

    def edit(self, key):
        issue = self.issues.get(key, None) or self.issues.get(f"{self.tira_space}-{key}", None)
        if issue is None:
            print(ISSUE_NOT_FOUND)
            return
        print("Editing issue", issue.key)
        print(f"Description: {issue.description}")
        issue.description = input("New description (Enter=no change): ") or issue.description
        self.save()
        print("Edited issue")

    def quit(self):
        self.save()
        self.is_running = False

    def help(self):
        print("Valid actions:")
        print("\tadd            Add a new issue.")
        print("\tlist           List all issues.")
        print("\tshow <key>     Show an issue.")
        print("\tdelete <key>   Delete an issue.")
        print("\tedit <key>     Edit an issue.")
        print("\texit           Exit the program.")
        print("\thelp           Show this help.")
        print("\tspace <space>  Set the space for new issues.")
        print("\tspaces         List all spaces.")

        print ("Current space:", self.tira_space)


if __name__ == "__main__":
    Controller().run()
