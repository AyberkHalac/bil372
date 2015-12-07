import re
import json
from bs4 import BeautifulSoup


class Parser:
    def __init__(self, url="", source=""):
        self.URL = url
        self.source = source
        self.__publist = dict()
        self.publist2 = list()

    def find_phone(self):
        pattern = '(\d{3}[-\.\s]??\d{3}[-\.\s]??\d{4}|\(\d{3}\)\s*\d{3}[-\.\s]??\d{4}|\d{3}[-\.\s]??\d{4})'
        return re.findall(pattern, self.source)

    def find_name(self):
        try:
            char, i = "", 0
            pattern = '(<title>\s*|<TITLE>\s*)(.*)(\s*<\/title>|\s*<\/TITLE>)'
            res = re.findall(pattern, self.source)
            title = str(res[0][1])
            for char in title:
                if (char in {'|', '\'', ',', ':', '-'}):
                    break
                i += 1
            if (i == len(title)):
                name = title
            else:
                name = title[:title.index(char)]
        except:
            return ""
        name = name.replace('Home', '')
        name = name.replace('Page', '')
        name = name.replace('Web', '')
        name = name.replace('Main', '')
        name = name.strip()
        try:
            return (name[0:name.rindex(' ')].lower(), name[name.rindex(' ') + 1:].lower())
        except:
            return ""

    def find_rank(self):
        rank_dic = {}
        ranks = ['adjunct professor', 'assistant professor', 'associate Professor', 'professor', 'lecturer',
                 'senior lecturer', 'associate professor', 'research assistant', 'research associate',
                 'research professor', 'research fellow', 'research instructor', 'instructor',
                 'research assistant professor', 'research associate professor', 'postdoctoral researcher',
                 'agregation', 'docent', 'habilitation', 'privatdozent', 'teaching assistant',
                 'teaching associate', 'visiting professor', 'teaching professor', 'visiting research professor',
                 'doç. dr.']

        for i in ranks:
            if i in self.source.lower():
                rank_dic[i] = self.source.lower().index(i)

        return min(rank_dic, key=rank_dic.get)

    def find_interest(self):
        interest = []
        with open('C:\\academic_dicipline.txt', 'r') as file:
            for line in file:
                if line.startswith('* [[') or line.startswith('** [['):
                    content = line.replace('[[', '').replace(']]', '').replace('* ', '').replace('*', '')[:-1]
                    if content.find('|') > 0:
                        content = content[:content.find('|')]
                    if content.find('(') > 0:
                        content = content[:content.find('(')]
                    interest.append(content.lower())
        interest_found = []
        for i in interest:
            if self.source.lower().find(i) > 0:
                interest_found.append(i)
        return interest_found


    def find_dept(self):
        with open('C:\\dept.txt', 'r') as file:
            for line in file:
                if line.lower()[:-1] in self.source.lower():
                    return line[:-1].lower()


    def find_uniname(self):

        from urllib.parse import urlparse
        uni_url = urlparse(self.URL).netloc

        f = open("C:\\uni.json")
        unis = json.load(f)
        f.close()
        for k in unis:
            if uni_url.endswith(k):
                return unis[k].strip().lower()

    def find_email(self):
        pattern1 = r'(?:[a-z0-9!#$%&\'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&\'*+/=?^_`{|}~-]+)*|"(?:[\x01-\x08\x0b\x0c' \
                   r'\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])*")@(?:(?:[a-z0-9](?:[a-z0-9-]' \
                   r'*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?|\[(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.)' \
                   r'{3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?|[a-z0-9-]*[a-z0-9]:(?:[\x01-\x08\x0b\x0c\x0e-\x1f' \
                   r'\x21-\x5a\x53-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])+)\])'
        pattern2 = r'^((<[^>]*>)*[mailto:(\sa-zA-Z0-9_.+-])+(@|(\s?(\{|\(|\[)\s?(at|AT)\s?(\}|\)|\])\s?)' \
                   r'|(\s(at|AT|@)\s))[a-zA-Z0-9-]+(\.|dot|\s)[a-zA-Z0-9-.]+'

        res1 = re.findall(pattern1, self.source, re.IGNORECASE)
        if (len(res1) == 0):
            result = re.findall(pattern2, self.source, re.IGNORECASE)
            return result
        else:
            return res1


    def find_publication(self):
        PUB_LIMIT = 3
        soup = BeautifulSoup(self.source)
        re_year = r'(19[0-9]{2})|(20(0|1)[0-9])'

        # Remove before "publication"

        source = self.__remove_before_pub(soup)

        soup2 = BeautifulSoup(source)
        if(len(soup2.select("li p")) > PUB_LIMIT):
            for lip in soup2.select("li p"):
                text = lip.get_text()
                self.__helper_pub(re_year, text, lip)

        elif(len(soup2.select("div p")) > PUB_LIMIT):
            for divp in soup2.select("div p"):
                text = divp.get_text()
                self.__helper_pub(re_year, text, divp)

        elif(len(soup2.select("li span")) > PUB_LIMIT):
            for lispan in soup2.select("li span"):
                text = lispan.get_text()
                self.__helper_pub(re_year, text, lispan)

        if(len(soup2.select("div span")) > PUB_LIMIT):
            for divspan in soup2.select("div span"):
                text = divspan.get_text()
                self.__helper_pub(re_year, text, divspan)

        if(len(soup2.select("p")) > PUB_LIMIT):
            for p in soup2.select("p"):
                text = p.get_text()
                self.__helper_pub(re_year, text, p)

        if(len(soup2.select("li")) > PUB_LIMIT):
            for li in soup2.select("li"):
                text = li.get_text()
                self.__helper_pub(re_year, text, li)

        if(self.__publist):
            for key in self.__publist:
                info = self.parse_publication(key)
                self.publist2.append([info['desc'],
                                      info['page'],
                                      info['date'],
                                      self.__publist[key]])
        return self.publist2

    def __remove_before_pub(self, soup):
        keys = ['publications', 'publication', 'Publications:', 'Publications', 'Publication',
                'paper', 'Paper', 'article', 'Article']
        tags = soup.findAll(['strong', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'])

        for t_out in tags:
            for i in keys:
                if i in t_out.text:
                    txt = t_out.text
                    index = self.source.index(i)
                    source = self.source[index + len(t_out.text):]
                    source = source[source.index(">")+1:].strip()
                    if("</" in source[:5]):
                        return source[source.index(">"):].strip()

                    return source

    def __helper_pub(self, re_year, text, src):
        PUB_DESC_LIMIT = 30
        if (re.findall(re_year, text) and len(text) > PUB_DESC_LIMIT):
            self.__publist[text.strip()] = self.__check_link_in_pub(src)


    def __check_link_in_pub(self, src):
        hrefs = list()

        for i in src.find_all("a"):
            if("href" in i.attrs):
                if(i["href"] == "#"):
                    continue

                if("http" not in i["href"]):
                    from urllib.parse import urljoin
                    hrefs.append(urljoin(self.URL, i["href"]))
                else:
                    hrefs.append(i["href"])
        if(hrefs):
            return hrefs[0]
        else:
            return None

    def parse_publication(self, text):
        txt = text
        information = dict()
        page_pattern = r'((\(?(pp|Pp).)(\s)?(\d+(\s?-\s?)\d+\)?)|(\d+(pp|Pp).))'
        date_pattern = r'\(?(((19[0-9]{2})|(20(0|1)[0-9])),?\s?)((January|February|March|April|May|June|July|August|' \
                       r'September|October|November|December)|(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\.?)' \
                       r'?\s?([1-9]|[12]\d|3[01])?\)?|\(?((0[1-9]|[12]\d|3[01])?\s?((January|February|March|April|May' \
                       r'|June|July|August|September|October|November|December)|(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|' \
                       r'Oct|Nov|Dec)\.?)\,?\s?((19[0-9]{2})|(20(0|1)[0-9]))\)?) '

        information['page'] = re.findall(page_pattern, text)
        information['date'] = re.findall(date_pattern, text)

        if(information['page']):
            page = information['page'][0][0]
        else:
            page = ''

        if(information['date']):
            date = information['date'][0][0]
        else:
            date = ''

        desc = txt.replace(page, '')
        desc = desc.replace(date,'')

        information['page'] = page
        information['date'] = date
        information['desc'] = desc

        return information

    def find_address(self):
        pattern = r'(Address|address)(\s|\:)+[a-zA-Z0-9-.\s:\,]*'
        res = re.findall(pattern, self.source)
        return res

    def find_courses(self):
        COURSE_LIMIT = 3
        DESC_LIMIT_MIN = 20
        DESC_LIMIT_MAX = 50

        text = list()
        soup = BeautifulSoup(self.source)

        # Remove before "course" or "teach"

        try:
            source = self.__remove_before_course(soup)
            soup2 = BeautifulSoup(source)
        except Exception as e:
            soup2 = BeautifulSoup(self.source)

        if(len(soup2.select("li p")) > COURSE_LIMIT):
            for lip in soup2.select("li p"):
                if(len(lip.get_text()) in range(DESC_LIMIT_MIN, DESC_LIMIT_MAX) and
                        not "\n" in lip.get_text()):
                    text.append(lip.get_text())
            return text

        elif(len(soup2.select("div p")) > COURSE_LIMIT):
            for divp in soup2.select("div p"):
                if(len(divp.get_text()) in range(DESC_LIMIT_MIN, DESC_LIMIT_MAX) and
                       not "\n" in divp.get_text()):
                    text.append(divp.get_text())
            return text


        elif(len(soup2.select("li span")) > COURSE_LIMIT):
            for lispan in soup2.select("li span"):
                if(len(lispan.get_text()) in range(DESC_LIMIT_MIN, DESC_LIMIT_MAX) and
                       not "\n" in lispan.get_text()):
                    text.append(lispan.get_text())
            return text

        if(len(soup2.select("div span")) > COURSE_LIMIT):
            for divspan in soup2.select("div span"):
                if(len(divspan.get_text()) in range(DESC_LIMIT_MIN, DESC_LIMIT_MAX) and
                       not "\n" in divspan.get_text()):
                    text.append(divspan.get_text())
            return text

        if(len(soup2.select("p")) > COURSE_LIMIT):
            for p in soup2.select("p"):
                if(len(p.get_text()) in range(DESC_LIMIT_MIN, DESC_LIMIT_MAX) and
                       not "\n" in p.get_text()):
                    text.append(p.get_text())
            return text

        if(len(soup2.select("li")) > COURSE_LIMIT):
            for li in soup2.select("li"):
                if(len(li.get_text()) in range(DESC_LIMIT_MIN, DESC_LIMIT_MAX) and
                       not "\n" in li.get_text()):
                    text.append(li.get_text())
            return text

    def __remove_before_course(self, soup):
        teach_keys = ['Teaching', 'teaching', 'Course', 'course', "class", "Class"]
        tags = soup.findAll(['strong', 'title', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
        source = ""

        for t_out in tags:
            for i in teach_keys:
                if i in t_out.text:
                    source = self.source[self.source.index(str(t_out)):]

        pub_keys = ['publications', 'publication', 'Publications:', 'Publications', 'Publication']

        for t_out in tags:
            for i in pub_keys:
                if i in t_out.text:
                    source = source[:source.index(str(t_out))]
                    return source


        return source

