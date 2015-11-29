import re
import json
from bs4 import BeautifulSoup

class Parser:
    def __init__(self, URL="", source=""):
        self.URL = URL
        self.source = source

    def find_phone(self):
        pattern = '(\d{3}[-\.\s]??\d{3}[-\.\s]??\d{4}|\(\d{3}\)\s*\d{3}[-\.\s]??\d{4}|\d{3}[-\.\s]??\d{4})'
        # print(re.findall(pattern, self.source))
        return re.findall(pattern, self.source)

    def find_name(self):

        char, i = "", 0
        pattern = '(<title>\s*|<TITLE>\s*)(.*)(\s*<\/title>|\s*<\/TITLE>)'
        res = re.findall(pattern, self.source)
        title = str(res[0][1])  # between title tags

        # Remove texts after the name
        for char in title:
            if (char in {'|', '\'', ',', ':', '-'}):
                break
            i += 1
        if (i == len(title)):
            name = title
        else:
            name = title[:title.index(char)]

        return name.strip()

    def find_uniname(self):

        pattern = "((http|https)://(www|[a-z\-]*)\.)([a-z\.]*(?=\/))"
        reg = re.findall(pattern, self.URL)
        uni_url = reg[0][3]

        with open("uni.json") as f:
            unis = json.load(f)
            for k in unis:
                if uni_url.endswith(k):
                    return unis[k].strip()

    def find_email(self):
        pattern1 = r'(?:[a-z0-9!#$%&\'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&\'*+/=?^_`{|}~-]+)*|"(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])*")@(?:(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?|\[(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?|[a-z0-9-]*[a-z0-9]:(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21-\x5a\x53-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])+)\])'
        pattern2 = r'(^([mailto:(\s)?a-zA-Z0-9_.+-])+(@|(\s?(\{|\(|\[)\s?(at|AT)\s?(\}|\)|\])\s?)|(\s(at|AT|@)\s))[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)'


        res1 = re.findall(pattern1, self.source)
        if(len(res1) == 0):
            return re.findall(pattern2, self.source)
        else:
            return res1

        # mailto ile başlayabilir

    """
    def find_publications(self):
        publications = []
        source = ''
        soup_out = BeautifulSoup(self.source, "lxml")

        for t_out in soup_out.findAll(['strong', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'], text=['publications', 'publication', 'Publications:', 'Publications', 'Publication']):
            source += str(t_out.parent)

        soup_in = BeautifulSoup(source, "lxml")

        for t_in in soup_in.findAll('p'):
            t_in = re.sub('<[^>]*>|\[.*\]|\s{2,}', '', str(t_in))
            publications.append(t_in)

        return publications
    """


    def find_publication(self):
        soup = BeautifulSoup(self.source, "lxml")
        text = ""
        for li in soup.select("li"):
            print(li.get_text())
