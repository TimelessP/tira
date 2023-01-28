import os.path
import pickle
import re
from typing import Dict

from model import Issue

KEY_IS_REQUIRED = "Key is required"
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
            "find": self.find,
        }
        while self.is_running:
            print("")
            action, *args = input(f"tira: {self.tira_space}> ").split() or " "

            for action_name, handler in actions.items():
                if action_name.startswith(action):
                    break
            else:
                print("Invalid action")
                continue

            handler(*args)

    def find(self, *args):
        text = " ".join(args)
        if not text:
            print("Text to find is required")
            return

        for issue in self.issues.values():
            formatted_date = issue.created.strftime("%Y-%m-%d %H:%M")
            line = f"{issue.key}\t{formatted_date}\t{repr(issue.description)}"
            if text.lower() in line.lower():
                print("")
                self.show(issue.key)
                is_more = input("More? (Enter|n) ")
                if is_more.lower() == "n":
                    break

    def space(self, *args):
        space = " ".join(args)
        if not space or not re.search(r"^[A-Z]{2,3}$", space):
            print("Space must be two or three capital letters")
            return

        self.tira_space = space

    def spaces(self, *args):
        filter_text = " ".join(args)
        if filter_text:
            spaces = set(key.split("-")[0] for key in self.issues if filter_text.lower() in key.lower())
        else:
            spaces = set(key.split("-")[0] for key in self.issues)

        if not spaces:
            print("No spaces found")
            return

        print(" ".join(sorted(spaces)))

    def add(self, *args):
        key = f"{self.tira_space}-{self.next_id}"
        self.next_id += 1
        description = " ".join(args) if args else input("Description: ")
        self.issues[key] = Issue(key, description)
        self.save()
        print(f"Added issue {key}")

    def list(self, *args):
        filter_text = " ".join(args)
        for issue in [iss for iss in self.issues.values() if iss.key.startswith(self.tira_space)]:
            formatted_date = issue.created.strftime("%Y-%m-%d %H:%M")
            line = f"{issue.key}\t{formatted_date}\t{repr(issue.description)}"
            if not filter or filter_text.lower() in line.lower():
                print(line)

    def show(self, *args):
        key = " ".join(args)
        if not key:
            print(KEY_IS_REQUIRED)
            return

        issue = self.issues.get(key, None) or self.issues.get(f"{self.tira_space}-{key}", None)
        if issue is None:
            print(ISSUE_NOT_FOUND)
            return

        print(issue.key)
        print(issue.description)
        print(issue.created)

    def delete(self, *args):
        key = " ".join(args)
        if not key:
            print(KEY_IS_REQUIRED)
            return

        issue = self.issues.get(key, None) or self.issues.get(f"{self.tira_space}-{key}", None)
        if issue is None:
            print(ISSUE_NOT_FOUND)
            return

        print(f"Deleted issue {issue.key}")
        del self.issues[issue.key]
        self.save()

    def edit(self, *args):
        key = " ".join(args)
        if not key:
            print(KEY_IS_REQUIRED)
            return

        issue = self.issues.get(key, None) or self.issues.get(f"{self.tira_space}-{key}", None)
        if issue is None:
            print(ISSUE_NOT_FOUND)
            return

        print("Editing issue", issue.key)
        print(f"Description: {issue.description}")
        issue.description = input("New description (Enter=no change): ") or issue.description
        self.save()
        print(f"Edited issue {issue.key}")

    def quit(self, *_):
        self.save()
        self.is_running = False

    def help(self, *_):
        print("Valid actions:")
        print("\tadd [<text>]     Add a new issue.")
        print("\tlist [<text>]    List issues in the current space.")
        print("\tshow <key>       Show an issue.")
        print("\tdelete <key>     Delete an issue.")
        print("\tedit <key>       Edit an issue.")
        print("\texit             Exit the program.")
        print("\thelp             Show this help.")
        print("\tspace <space>    Set the space for new issues.")
        print("\tspaces [<text>]  List spaces.")
        print("\tfind <text>      Find issues in all spaces that contain the text.")

        print("Current space:", self.tira_space)


if __name__ == "__main__":
    Controller().run()
