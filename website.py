from flask import Flask
from flask import render_template, request
from sqlalchemy import *
from sqlalchemy.engine.url import URL
import setting
import main
app = Flask(__name__)

db = None
KEYWORD = ""

@app.route('/')
@app.route('/index')
@app.route('/index.html')
def homepage():
    return render_template('/index.html')


@app.route('/profile/<id>')
def profile(id):
    data = list()
    c = db.connect()

    # bio
    query1 = "select fname, lname, title from bio where pid=\'"+str(id)+"\';"
    res = c.execute(query1)
    f = res.fetchall()
    bio = [i for i in f if f][0]
    data.append(bio)

    # work
    query2 = "select university, dept from work where pid=\'"+str(id)+"\';"
    res = c.execute(query2)
    f = res.fetchall()
    work = [i for i in f if f][0]
    data.append(work)


    # publication
    query3 = "select pubid from published where pid=\'"+str(id)+"\';"
    res = c.execute(query3)
    f = res.fetchall()
    pubid = [i[0] for i in f if f]
    publist = list()
    for j in pubid:
        query4 = "select pubname, url from publication where pubid=\'"+str(j)+"\';"
        res = c.execute(query4)
        f = res.fetchall()
        publist.append([(i[0],i[1]) for i in f if f])

    print(publist)
    data.append(publist)

    # interest
    query5 = "select interest from interested_in where pid=\'"+str(id)+"\';"
    res = c.execute(query5)
    f = res.fetchall()
    interest = [i[0] for i in f if f]
    data.append(interest)

    return render_template('/profile.html', pid=id, data= data)


@app.route('/add_person', methods=['POST'])
def add_person():

    result=""
    try:
        keyword = request.form['x']
    except Exception as e:
        print(e)
        pass

    try:
        result = main.mainStart(keyword)
        print("line76: "+str(result))
    except Exception as e:
        print(e)

    return profile(result)

@app.route('/listall')
@app.route('/listall.html')

def list_all():

    data = list()
    c = db.connect()

    query = "select bio.pid, fname, lname, title, university from bio, work " \
                    "where bio.pid = work.pid"

    res = c.execute(query)

    if(res):
        for i in res:
             data.append(i)

    print(data)
    return render_template("listall.html", data=data)


@app.route('/result', methods=['POST'])
def result():
    global KEYWORD
    keyword = ""
    filter=""

    try:
        keyword = request.form['x'].lower()
    except Exception as e:
        print(e)
        pass

    if(keyword):
        KEYWORD = keyword
    else:
        keyword = KEYWORD


    try:
        filter = request.form.getlist('filter')
    except Exception as e:
        print(e)
        pass

    l = list()

    if(filter):
        if("kisiler" in filter):
            res = searchInBio(keyword)
            for i in res:
                l.append(i[0])

        if("universite" in filter):
            res = searchInUni(keyword)
            for i in res:
                l.append(i[0])

        if("bolum" in filter):
            res = searchInDept(keyword)
            for i in res:
                l.append(i[0])

        if("ilgialani" in filter):
            res = searchInInterest(keyword)
            for i in res:
                l.append(i[0])

        if("yayinlar" in filter):
            res = searchInPub(keyword)
            for i in res:
                l.append(i[0])

    else:
        res = searchInBio(keyword)
        for i in res:
            if(not i[0] in l):
                l.append(i[0])

        res = searchInUni(keyword)
        for i in res:
            if(not i[0] in l):
                l.append(i[0])

        res = searchInDept(keyword)
        for i in res:
            if(not i[0] in l):
                l.append(i[0])

        res = searchInInterest(keyword)
        for i in res:
            if(not i[0] in l):
                l.append(i[0])

        res = searchInPub(keyword)
        for i in res:
            if(not i[0] in l):
                l.append(i[0])

    namelist = list()
    for i in l:
        namelist.append(searchByID(i))


    return render_template('/result.html', key=keyword, data=namelist)

def searchByID(id):
    c = db.connect()
    liste = list()

    query = "select bio.pid, fname, lname, title, university from bio, work " \
                    "where bio.pid = work.pid and bio.pid=\'"+str(id)+"\'"
    res = c.execute(query)

    if(res):
        for i in res:
             return i

    return ("None", "None", "None", "None")


def db_connect():
    return create_engine(URL(**setting.DATABASE))


def searchInBio(keyword):
    columns = ["fname", "lname", "title", "bplace", "education"]
    c = db.connect()
    liste = list()

    for col in columns:
        query = "select pid from bio where "+col+" ilike \'"+keyword+"\'"
        res = c.execute(query)
        f = res.fetchall()
        if(f):
            for i in f:
                liste.append(i)

    return liste

def searchInUni(keyword):
    c = db.connect()
    query = "select pid from work where university"+" ilike \'"+keyword+"\'"
    res = c.execute(query)
    f = res.fetchall()

    return [i for i in f if f]


def searchInDept(keyword):
    c = db.connect()
    query = "select pid from work where dept"+" ilike \'"+keyword+"\'"
    res = c.execute(query)
    f = res.fetchall()

    return [i for i in f if f]


def searchInInterest(keyword):
    c = db.connect()
    query = "select pid from interested_in where interest"+" ilike \'"+keyword+"\'"
    res = c.execute(query)
    f = res.fetchall()

    return [i for i in f if f]

def searchInPub(keyword):
    c = db.connect()
    query = "select pubid from publication where pubname"+" ilike \'"+keyword+"\'"
    res = c.execute(query)
    f = res.fetchall()

    pubid_list = [i[0] for i in f if f]
    id_list = list()

    for i in pubid_list:
        query = "select pid from published where pubid=\'"+str(i)+"\';"
        res = c.execute(query)
        f = res.fetchall()
        for i in f:
            id_list.append(i)

    return id_list


if __name__ == '__main__':
    db = db_connect()
    app.debug=True
    app.run()



