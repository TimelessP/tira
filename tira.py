import os.path
import pickle
from typing import Dict

from model import Issue

ISSUE_NOT_FOUND = "Issue not found"

TIRADATA_PICKLE = "tiradata.pickle"


class Controller:
    def __init__(self):
        self.issues: Dict[str, Issue] = {}
        self.is_running = True
        self.next_id = 1
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
            }
            print("")
            action, *args = input("> ").split()
            if action not in actions:
                print("Unknown action")
                continue
            actions[action](*args)

    def add(self):
        key = f"TI-{self.next_id}"
        self.next_id += 1
        description = input("Description: ")
        self.issues[key] = Issue(key, description)
        self.save()
        print("Added issue")

    def list(self):
        for issue in self.issues.values():
            formatted_date = issue.created.strftime("%Y-%m-%d %H:%M")
            print(f"{issue.key}\t{formatted_date}\t{repr(issue.description)}")

    def show(self, key):
        issue = self.issues.get(key, None)
        if issue is None:
            print(ISSUE_NOT_FOUND)
            return
        print(issue.key)
        print(issue.description)
        print(issue.created)

    def delete(self, key):
        issue = self.issues.get(key, None)
        if issue is None:
            print(ISSUE_NOT_FOUND)
            return
        del self.issues[key]
        self.save()
        print("Deleted issue")

    def edit(self, key):
        issue = self.issues.get(key, None)
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
        print("add")
        print("list")
        print("show <key>")
        print("delete <key>")
        print("edit <key>")
        print("exit")
        print("help")


if __name__ == "__main__":
    Controller().run()
