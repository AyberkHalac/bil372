import random
import re
import psycopg2
from crawler import Crawler


def test(n=5, sample=True):
    with open('URL.txt') as file:
        content = [line.rstrip('\n') for line in file]
    file.close()
    if sample:
        return random.sample(content, n)
    else:
        return content


def add_database(url, fname, lname, uniname, dept, rank, email, phone, fax, office_no, address, conn, c):
    c.execute("SELECT * FROM person where website = \'" + url + "\'")
    result = c.fetchall()
    if len(result) == 0:
        c.execute("INSERT INTO person (website) VALUES (\'" + url + "\') RETURNING pid;")
        repid = c.fetchone()[0]
        query = "INSERT INTO bio (pid,fname,lname,title,bdate,bplace,education) VALUES (%s, %s, %s ,%s,'UNKNOWN', 'UNKNOWN' ,'UNKNOWN');"
        data = (repid, fname, lname, rank)
        c.execute(query, data)
        conn.commit()
        query = "INSERT INTO work (pid,university, dept) VALUES (%s, %s, %s);"
        data = (repid, uniname, dept)
        c.execute(query, data)
        conn.commit()
        query = "INSERT INTO contact (pid,email,phone,fax,office_no,address) VALUES (%s, %s, %s, %s, %s,%s);"
        data = (repid, email, phone, fax, office_no, address)
        c.execute(query, data)
        conn.commit()
    else:
        print("line36: " + str(result[0]))
        return True, result[0]

    return False, repid


def db_publication(pubname, url, ptype, conn, c):
    query = "INSERT INTO publication (pubname,url,ptype) VALUES ( %s, %s, %s) RETURNING pubid;"
    data = (pubname, url, ptype)
    c.execute(query, data)
    pubid = c.fetchone()[0]
    conn.commit()
    return pubid


def db_published(pid, pubid, pdate, conn, c):
    query = "INSERT INTO published (pid,pubid,pdate) VALUES (%s, %s, %s);"
    data = (pid, pubid, pdate)
    c.execute(query, data)
    conn.commit()


def db_interest(pid, interest, conn, c):
    query = "INSERT INTO interested_in (pid, interest) VALUES (%s, %s);"
    data = (pid, interest)
    c.execute(query, data)
    conn.commit()


def db_contribute(pubid, contribute, conn, c):
    query = "INSERT INTO contribute (pubid, contributes) VALUES (%s, %s);"
    data = (pubid, contribute)
    c.execute(query, data)
    conn.commit()


def parse(url, dictionary, conn, c):
    if len(dictionary['name']) > 0:
        fname = dictionary['name'][0]
        lname = dictionary['name'][1]
    else:
        fname = 'UNKNOWN'
        lname = 'UNKNOWN'

    if len(dictionary['tel']) > 0:
        tel = dictionary['tel'][0]
    else:
        tel = 'UNKNOWN'

    if dictionary['email'] == '':
        email = 'UNKNOWN'
    else:
        email = dictionary['email']

    if dictionary['rank'] == '':
        rank = 'UNKNOWN'
    else:
        rank = dictionary['rank']

    if dictionary['uni'] == '':
        uni = 'UNKNOWN'
    else:
        uni = dictionary['uni']

    if dictionary['dept'] == '':
        dept = 'UNKNOWN'
    else:
        dept = dictionary['dept']

    person_found = add_database(url, fname, lname, uni, dept, rank, email, tel, tel, 'UNKNOWN', 'address', conn, c)

    if person_found[0] == True:
        return person_found[1][0]

    repid = person_found[1]
    if len(dictionary['publication']) > 0:
        for pub in dictionary['publication']:
            publication = pub
            pub_desc = publication[0]
            pub_page = publication[1]
            pub_date = publication[2]
            pub_link = publication[3]
            pubid = db_publication(pub_desc, pub_link, 'paper', conn, c)
            db_published(repid, pubid, pub_date, conn, c)
            pattern = '(([A-Za-z\s\.]){2,16},)+(\sand[\sA-Za-z\.]{2,16})'
            contribute = re.findall(pattern, pub_desc)
            if len(contribute) > 0:
                db_contribute(pubid, contribute[0], conn, c)
    if len(dictionary['interest']) > 0:
        for interest in dictionary['interest']:
            db_interest(repid, interest, conn, c)
    conn.close()

    return repid


def mainStart(url):
    print("************")
    print(url)
    crawler = Crawler(url)
    dictionary = crawler.run()
    print(dictionary)
    conn_string = "host='localhost' dbname='bil372' user='postgres' password='12345'"
    conn = psycopg2.connect(conn_string)
    c = conn.cursor()
    # c.execute("TRUNCATE TABLE person, bio, contact, interested_in, project, published,contribute, publication, research, work RESTART IDENTITY;")
    id = parse(url, dictionary, conn, c)
    print("PID:"+str(id))
    return id


