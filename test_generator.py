import pathlib
import os

current_dir = str(pathlib.Path(__file__).parent.resolve())


class CaseWriter:
    file = "test_cases.txt"

    def __init__(self):
        self.cases = []
        pass

    def add_case(self, t, r):
        self.cases.append((t,r))

    def finish(self, w):
        with open(current_dir + os.sep + CaseWriter.file, 'a') as f:
            f.writelines(os.linesep.join(["#".join([w,t,r]) for t,r in self.cases]))
            f.write("\n")


if __name__ == '__main__':
    print(current_dir)
