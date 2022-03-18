import re, json


class DictUpdater:

    def __init__(self, fname):
        self.dobj = {}
        self.fname = fname
        self.start()

    def start(self):
        with open(self.fname) as f:
            self.dobj = json.load(f)
        pass

    def save(self, k, v):
        self.dobj[k] = v
        with open(self.fname, 'w') as f:
            json.dump(self.dobj, f)
        pass


du = DictUpdater( "words5char-syllables.json")

print("len(wordSet) ", len(du.dobj))

if __name__ == '__main__':
    with open("print.log") as f:
        for l in f:
            match = re.match("^Collec.*? (\w+)$",l)
            if match:
                w = match.group(1)
                print(w)
            else:
                match = re.match("^\d.*? '([^']+)'$",l)
                if match:
                    sw = match.group(1)
                    print(sw)
                    if w in du.dobj:
                        print("{} already in the wordset = {}".format(w, du.dobj[w] ))
                        continue
                    else:
                        du.save(w,sw)
                else:
                    print("faiô")

print(du.dobj)

