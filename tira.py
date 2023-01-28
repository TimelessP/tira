import argparse
import os.path
import pickle
import re
import sys
from typing import Dict
from datetime import datetime

from model import Issue

TIRA_DATA_PICKLE = "tira_data.pickle"
KEY_IS_REQUIRED = "Key is required"
ISSUE_NOT_FOUND = "Issue not found"

tira_data_file_path = TIRA_DATA_PICKLE


class Controller:
    def __init__(self, data_file_path):
        self.data_file_path = data_file_path
        self.last_modified = None
        self.issues: Dict[str, Issue] = {}
        self.is_running = True
        self.next_id = 1
        self.tira_space = "TI"
        self.load()

    def save(self):
        os.makedirs(os.path.dirname(self.data_file_path), exist_ok=True)
        with open(self.data_file_path, "wb") as f:
            pickle.dump(self.issues, f)

        self.last_modified = os.path.getmtime(self.data_file_path)

    def load(self):
        if os.path.exists(self.data_file_path):
            with open(self.data_file_path, "rb") as f:
                self.issues = pickle.load(f)
                if not self.issues:
                    self.next_id = 1
                else:
                    self.next_id = max(int(key.split("-")[1]) for key in self.issues) + 1

            self.last_modified = os.path.getmtime(self.data_file_path)

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
            try:
                action, *args = input(f"tira: {self.tira_space}> ").split() or " "
            except EOFError:
                action = "exit"
                args = []

            if os.path.exists(self.data_file_path) and \
                    (self.last_modified is None or
                     os.path.getmtime(self.data_file_path) != self.last_modified):

                self._force_reload_data()
                continue

            for action_name, handler in actions.items():
                if action_name.startswith(action):
                    break
            else:
                print("Invalid action")
                continue

            # noinspection PyArgumentList
            handler(*args)

    def _force_reload_data(self):
        formatted_expected = datetime.fromtimestamp(self.last_modified).strftime(
            "%Y-%m-%d %H:%M:%S") if self.last_modified else "None"
        formatted_actual = datetime.fromtimestamp(os.path.getmtime(self.data_file_path)).strftime(
            "%Y-%m-%d %H:%M:%S")
        print("The data file has been modified by another process.")
        print(f"Expected timestamp:\t{formatted_expected}")
        print(f"Actual timestamp:\t{formatted_actual}")
        self.load()
        print("Data has now been reloaded.")

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
        print("")
        print("Current space:", self.tira_space)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--data_file", help="Path to the data file")
    process_args = parser.parse_args()

    if process_args.data_file:
        tira_data_file_path = process_args.data_file
    else:
        if sys.platform == "win32":
            tira_data_file_path = os.path.join(os.getenv("APPDATA"), "tira", TIRA_DATA_PICKLE)
        elif sys.platform == "darwin":
            tira_data_file_path = os.path.join(os.getenv("HOME"), "Library", "Application Support", "tira",
                                               TIRA_DATA_PICKLE)
        else:
            tira_data_file_path = os.path.join(os.getenv("HOME"), ".config", "tira", TIRA_DATA_PICKLE)

    Controller(tira_data_file_path).run()
