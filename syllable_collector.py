import json
from contextlib import closing
from time import sleep

from requests import RequestException, get
from bs4 import BeautifulSoup

class UrlGetter:

    def simple_get(self, url):
        """
        Attempts to get the content at `url` by making an HTTP GET request.
        If the content-type of response is some kind of HTML/XML, return the
        text content, otherwise return None.

        """

        try:
            with closing(get(url, stream=True)) as resp:
                if resp.status_code == 200:
                    return resp.content
                else:
                    raise ValueError("Url not available")

        except RequestException as e:
            raise ValueError("Url not available")



class DictUpdater:

    def __init__(self, fname) -> object:
        self.dobj = {}
        self.fname = fname
        self.start()

    def start(self):
        with open(self.fname, encoding='utf-8') as f:
            self.dobj = json.load(f)
        pass

    def save(self, k, v):
        self.dobj[k] = v
        with open(self.fname, 'w', encoding='utf-8') as f:
            json.dump(self.dobj, f)
        pass


du = DictUpdater( "words5char_utf-8-syllables.json")


if __name__ == '__main__':

    w5cs= []

    with open("words5char_utf-8.json", encoding="utf-8") as f:
        w5c = json.load(f)

    count = 0
    size_w = len(w5c)
    for w in w5c:
        count+=1
        if w in du.dobj:
            print("{} already in the wordset = {}".format(w, du.dobj[w]))
            w5cs.append(du.dobj[w])
            continue
        print("Collecting for word {}".format(w))
        content = UrlGetter().simple_get("https://www.separaremsilabas.com/index.php?p={}".format(w))
        bs = BeautifulSoup(content, 'html.parser')
        try:
            ws = bs.find("font", color="#0018BF").text.strip()
            print("{} of {} -  '{}'".format(count,size_w,ws))
            w5cs.append(ws)
            du.save(w,ws)
        except Exception as e:
            print(e)
            print("Could not retrieve the syllable separation for word {}".format(w))

        sleep(1)
