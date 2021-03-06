from flask import Flask,render_template,request,redirect,make_response,session
import pymysql


app = Flask(__name__)
app.secret_key="123456"

#错误
@app.errorhandler(404)
def error(error):
    return render_template('404.html')

@app.errorhandler(400)
def error(error):
    return render_template('')

#启动闪屏
@app.route('/start')
def start():
    session["start"] = "started"
    return render_template('start.html')

#首页推荐
@app.route('/')
def index():
    if(session.get("start")!="started"):
        return redirect('/start')
    if(session.get("login")=="yes"):
        userid = session.get("userid")
        db = pymysql.connect('localhost', 'root', '123456', 'lixiaohuan', charset='utf8',
                             cursorclass=pymysql.cursors.DictCursor)
        cur = db.cursor()
        cur.execute('select cateids from user where userid=%s',(userid))
        cateids= cur.fetchone()
        cateids = ' '+cateids['cateids'][0:-1]+' '
        cur.execute( 'select articleid,userid,a_time,up,imgurl from article where cateid in ('+ cateids +') order by articleid desc limit 5')
        data = cur.fetchall()
        for i in range(len(data)):
            cur.execute('select username,headurl from user where userid = %s',(data[i]['userid']))
            result = cur.fetchone()
            data[i].setdefault('username', result["username"])
            data[i].setdefault('headurl', result["headurl"])
            cur.execute('select count(commentid) from comment where articleid = %s', (data[i]['articleid']))

            comment_num = cur.fetchone()["count(commentid)"]
            data[i].setdefault('comment_num', comment_num)
            year=str(data[i]['a_time'].year)
            month=str(data[i]['a_time'].month)
            day=str(data[i]['a_time'].day)
            data[i]['a_time']=year+'.'+month+'.'+day
        db.close()
        cur.close()
        return render_template("index.html",data=data)
    else:
        return  redirect('/login')

#首页关注
@app.route('/gaze')
def gaze():
    userid = session.get("userid")
    db = pymysql.connect('localhost', 'root', '123456', 'lixiaohuan', charset='utf8',
                         cursorclass=pymysql.cursors.DictCursor)
    cur = db.cursor()
    cur.execute('select fallow from user where userid = %s', (userid))
    fallows = cur.fetchone()
    fallows = ' '+fallows['fallow'][0:-1]+' '
    cur.execute('select * from article where userid = '+fallows+' order by articleid desc limit 5')
    data=cur.fetchall()
    for i in range(len(data)):
        cur.execute('select username,headurl from user where userid = %s', (data[i]['userid']))
        result = cur.fetchone()
        data[i].setdefault('username', result["username"])
        data[i].setdefault('headurl', result["headurl"])
        cur.execute('select count(commentid) from comment where articleid = %s', (data[i]['articleid']))
        comment_num = cur.fetchone()["count(commentid)"]
        data[i].setdefault('comment_num',comment_num)
        year = str(data[i]['a_time'].year)
        month = str(data[i]['a_time'].month)
        day = str(data[i]['a_time'].day)
        data[i]['a_time'] = year + '.' + month + '.' + day
    db.close()
    cur.close()
    res = make_response(render_template('index2.html', data=data))
    return res

#消息中心
@app.route('/massage')
def massage():
    userid=session.get("userid")
    db = pymysql.connect('localhost', 'root', '123456', 'lixiaohuan', charset='utf8',
                         cursorclass=pymysql.cursors.DictCursor)
    cur = db.cursor()
    cur.execute('select articleid from article where userid = %s', (userid))
    articleid = cur.fetchall()
    aid=""
    for i in range(len(articleid)):
        aid=aid+articleid[i][articleid]+','
    aid=aid[0:-1]
    cur.execute('select * from comment where articleid = %s desc limit 10', (aid))
    data = cur.fetchall()
    for i in range(len(data)):
        cur.execute('select username,headurl from user where userid = %s', (data[i]["userid"]))
        result=cur.fetchone()
        data[i].setdefault('username', result["username"])
        data[i].setdefault('headurl', result["headurl"])
    db.close()
    cur.close()
    res = make_response(render_template('', data=data))
    return res

#我的粉丝
@app.route('/fans')
def fans():
    userid = session.get("userid")
    db = pymysql.connect('localhost', 'root', '123456', 'lixiaohuan', charset='utf8',
                         cursorclass=pymysql.cursors.DictCursor)
    cur = db.cursor()
    cur.execute('select fans from user where userid = %s', (userid))
    fans = cur.fetchall()
    fans = fans[0:-1]
    cur.execute('select * from user where userid = %s', (fans))
    data = cur.fetchall()
    db.close()
    cur.close()
    res = make_response(render_template('fans.html', data=data))
    return res

#我的关注
@app.route('/fallow')
def fallow():
    userid = session.get("userid")
    db = pymysql.connect('localhost', 'root', '123456', 'lixiaohuan', charset='utf8',
                         cursorclass=pymysql.cursors.DictCursor)
    cur = db.cursor()
    cur.execute('select fallow from user where userid = %s', (userid))
    fallow = cur.fetchall()
    fallow = fallow[0:-1]
    if fallow:
        cur.execute('select * from user where userid = %s', (fallow))
        data = cur.fetchall()
        db.close()
        cur.close()
    else:
        data=''
    res = make_response(render_template('mylike.html', data=data))
    return res

#加关注
@app.route('/addfollow/<userid>')
def addfollow(userid):
    myid = session.get("userid")
    db = pymysql.connect('localhost', 'root', '123456', 'lixiaohuan', charset='utf8',
                         cursorclass=pymysql.cursors.DictCursor)
    cur = db.cursor()
    #添加自己的fallow
    cur.execute('select fallow from user where userid = %s', (myid))
    fallow = cur.fetchone()
    fallow = fallow + userid + ","
    cur.execute('update user set fallow = %s where userid = %s',(fallow,myid))
    db.commit()
    #添加对方fans
    cur.execute('select fallow from user where userid = %s', (userid))
    fans = cur.fetchone()
    fans = fans + myid + ","
    cur.execute('update user set fans = %s where userid = %s', (fans, userid))
    db.commit()
    db.close()
    cur.close()
    return 'done'

#我的发布
@app.route('/myarticles')
def myarticles():
    userid = session.get("userid")
    db = pymysql.connect('localhost', 'root', '123456', 'lixiaohuan', charset='utf8',
                         cursorclass=pymysql.cursors.DictCursor)
    cur = db.cursor()
    cur.execute('select * from article where userid = %s and a_state = %s order by userid desc limit 1', (userid,1))
    data = cur.fetchall()
    db.close()
    cur.close()
    res = make_response(render_template('myfabu.html', data=data))
    return res

@app.route('/myarticles/del/<articleid>')
def delarticles(articleid):
    userid = session.get("userid")
    db = pymysql.connect('localhost', 'root', '123456', 'lixiaohuan', charset='utf8',
                         cursorclass=pymysql.cursors.DictCursor)
    cur = db.cursor()
    cur.execute('select userid from article where articleid = %s',(articleid))
    theuserid = cur.fetchone()
    if userid == theuserid:
        cur.execute('update article set a_state = %s where articleid = %s',(0,articleid))
        db.commit()
    db.close()
    cur.close()
    return redirect("/myarticles")

#预告提醒
@app.route('/notice')
def notice():
    db = pymysql.connect('localhost', 'root', '123456', 'lixiaohuan', charset='utf8',
                         cursorclass=pymysql.cursors.DictCursor)
    cur = db.cursor()
    cur.execute('select * from notice where n_state = 1 ')
    data = cur.fetchall()
    db.close()
    cur.close()
    res = make_response(render_template('foreshow.html', data=data))
    return res

#搜索
@app.route('/search',methods=["GET"])
def opensearch():
    return render_template("search.html")

@app.route('/searchhistory')
def searchhistory():
    return render_template("history.html")

#关键字搜索
import json
@app.route('/search',methods=["POST"])
def search():
    keys=request.form["keys"]
    db = pymysql.connect('localhost', 'root', '123456', 'lixiaohuan', charset='utf8',
                         cursorclass=pymysql.cursors.DictCursor)
    cur = db.cursor()
    cur.execute('select * from user where find_in_set(%s,username)',(keys))
    data1 = cur.fetchall()
    cur.execute('select * from article where find_in_set(%s,title)', (keys))
    data = cur.fetchall()
    db.close()
    cur.close()
    for i in range(len(data)):
        year = str(data[i]['a_time'].year)
        month = str(data[i]['a_time'].month)
        day = str(data[i]['a_time'].day)
        data[i]['a_time'] = year + '.' + month + '.' + day
    for i in range(len(data1)):
        year = str(data1[i]['r_time'].year)
        month = str(data1[i]['r_time'].month)
        day = str(data1[i]['r_time'].day)
        data1[i]['r_time'] = year + '.' + month + '.' + day
    return json.dumps({'data':data,'data1':data1})
    # return data,data1
    #data1博主 data文章

#类别搜索
@app.route('/search/<catename>')
def searchcate(catename):
    db = pymysql.connect('localhost', 'root', '123456', 'lixiaohuan', charset='utf8',
                         cursorclass=pymysql.cursors.DictCursor)
    cur = db.cursor()
    cur.execute('select * from article where cateid = and exists (select cateid from category where catename=%s) desc limit 5',(catename))
    data = cur.fetchall()
    for i in range(len(data)):
        cur.execute('select username,headurl from user where userid = %s', (data[i]['userid']))
        result = cur.fetchone()
        data[i].setdefault('username', result["username"])
        data[i].setdefault('headurl', result["headurl"])
        cur.execute('select count(commentid) from comment where articleid = %s', (data[i]['articleid']))
        comment_num = cur.fetchone()
        data[i].setdefault('comment_num', comment_num)
    db.close()
    cur.close()
    return data

#文章详情
@app.route('/article/<articleid>')
def article(articleid):
    db = pymysql.connect('localhost', 'root', '123456', 'lixiaohuan', charset='utf8',
                         cursorclass=pymysql.cursors.DictCursor)
    cur = db.cursor()
    cur.execute('select * from article where articleid = %s)',(articleid))
    data = cur.fetchall()
    cur.execute('select catename from category where cateid =%s',(data["cateid"]))
    catename = cur.fetchone()
    cur.execute('select * from comment where articleid = %s',(articleid))
    comment = cur.fetchall()
    db.close()
    cur.close()
    res = make_response(render_template('', data=data,catename=catename,comment=comment))
    return res

#评论文章
@app.route('/comment/<articleid>',methods=["POST"])
def comment(articleid):
    userid = session.get("userid")
    c_content = request.form["c_content"]
    db = pymysql.connect('localhost', 'root', '123456', 'lixiaohuan', charset='utf8',
                         cursorclass=pymysql.cursors.DictCursor)
    cur = db.cursor()
    cur.execute('insert into comment(articleid,userid,c_content) values (%s,%s,%s)',(articleid,userid,c_content))
    db.commit()
    db.close()
    cur.close()
    return redirect("/article/"+articleid)

#我的资料
@app.route('/aboutme')
def aboutme():
    userid = session.get("userid")
    db = pymysql.connect('localhost', 'root', '123456', 'lixiaohuan', charset='utf8',
                         cursorclass=pymysql.cursors.DictCursor)
    cur = db.cursor()
    cur.execute('select * from user where userid = %s',(userid))
    data = cur.fetchone()
    data.setdefault('fallownum', data["fallow"].count(","))
    data.setdefault('fansnum', data["fans"].count(","))
    res = make_response(render_template('myself.html', data=data))
    return res

#查看他人资料
@app.route('/user/<userid>')
def user(userid):
    db = pymysql.connect('localhost', 'root', '123456', 'lixiaohuan', charset='utf8',
                         cursorclass=pymysql.cursors.DictCursor)
    cur = db.cursor()
    cur.execute('select * from user where userid = %s)', (userid))
    data = cur.fetchone()
    data.setdefault('fallownum', data["fallow"].count(","))
    data.setdefault('fansnum', data["fans"].count(","))
    cur.execute('select * from article where userid = %s desc limit 2)', (userid))
    article = cur.fetchall()
    db.close()
    cur.close()
    return render_template("otheruser.html",data=data,article=article)

#设置
@app.route('/setting')
def setting():
    res = make_response(render_template('setting.html'))
    return res



@app.route('/setting/message')
def settingmessage():
    res = make_response(render_template('shezhi.html'))
    return res

@app.route('/setting/myinfo',methods=["GET"])
def opensettingmyinfo():
    userid = session.get("userid")
    db = pymysql.connect('localhost', 'root', '123456', 'lixiaohuan', charset='utf8',
                         cursorclass=pymysql.cursors.DictCursor)
    cur = db.cursor()
    cur.execute('select username,autograph,sex from user where userid = %s', (userid))
    data = cur.fetchone()
    db.close()
    cur.close()
    print(data)
    return render_template('editmyinfo.html',data=data)

@app.route('/setting/myinfo',methods=["POST"])
def settingmyinfo():
    userid = session.get("userid")
    username = request.form["username"]
    autograph = request.form["autograph"]
    sex = request.form["sex"]
    db = pymysql.connect('localhost', 'root', '123456', 'lixiaohuan', charset='utf8',
                         cursorclass=pymysql.cursors.DictCursor)
    cur = db.cursor()
    cur.execute('update user set username=%s,autograph=%s,sex=%s  where userid = %s', (username,autograph,sex,userid))
    db.commit()
    cur.close()
    db.close()
    return redirect("/aboutme")

#登录
@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/checklogin',methods=["POST"])
def checklogin():
    usertel = request.form["usertel"]
    password = request.form["password"]
    db = pymysql.connect('localhost', 'root', '123456', 'lixiaohuan', charset='utf8',
                         cursorclass=pymysql.cursors.DictCursor)
    cur = db.cursor()
    cur.execute('select * from user where usertel=%s and password=%s',(usertel,password))
    result=cur.fetchone()
    db.commit()
    db.close()
    cur.close()
    # 用户ID
    session["userid"] = str(result["userid"])
    if(result["isfinished"]==0):
        return redirect('/register/uphead')
    elif(result["isfinished"]==1):
        return redirect('/register/upinterest')
    elif(result["isfinished"]==2):
        res = make_response(redirect('/'))
        # 登录状态
        session["login"]="yes"
        # 用户名
        session["username"]=result["username"]
        return res
    else:
         return render_template('login.html',isTure='no')

#注册
@app.route('/register',methods=["GET"])
def openregister():
    return render_template('register.html')

@app.route('/register',methods=["POST"])
def register():
    usertel = request.form["usertel"] or ''
    password = request.form["password"] or ''
    repassword = request.form["repassword"] or ''
    if password != repassword or password == '' or usertel == '':
        return redirect('/register')
    db = pymysql.connect('localhost', 'root', '123456', 'lixiaohuan', charset='utf8',
                         cursorclass=pymysql.cursors.DictCursor)
    cur = db.cursor()
    cur.execute('select * from user where usertel=%s', (usertel))
    result = cur.fetchone()
    if result:
        return render_template('register.html',isRepeat='yse')
    cur.execute('insert into user (usertel,username,password,isfinished) values (%s,%s,%s,%s)',(usertel,usertel,password,0))
    session["usertel"] = usertel
    return redirect('/register/uphead')

@app.route('/register/uphead',methods=["GET"])
def openregister_uphead():
    return render_template("register2.html")

@app.route('/register/uphead',methods=["POST"])
def register_uphead():
    usertel = session.get('usertel')
    db = pymysql.connect('localhost', 'root', '123456', 'lixiaohuan', charset='utf8',
                         cursorclass=pymysql.cursors.DictCursor)
    cur = db.cursor()
    headurl = 'unknow'
    if usertel:
        cur.execute('update user set headurl = %s,isfinished = %s where usertel = %s',(headurl,usertel,'1'))
    else:
        userid=session.get('userid')
        cur.execute('update user set headurl = %s,isfinished = %s where userid = %s', (headurl, userid, '1'))
    db.commit()
    db.close()
    cur.close()
    return redirect('/register/upinterest')

@app.route('/register/upinterest',methods=["GET"])
def openregister_upinterest():
    return render_template("register3.html")

@app.route('/register/upinterest',methods=["POST"])
def register_upinterest():
    username = request.form["username"]
    sex = request.form["sex"]
    cateids = request.form["cateids"]
    usertel = session.get('usertel') or ''
    db = pymysql.connect('localhost', 'root', '123456', 'lixiaohuan', charset='utf8',
                         cursorclass=pymysql.cursors.DictCursor)
    cur = db.cursor()
    if usertel:
        cur.execute('update user set username = %s,sex = %s,cateids = %s,isfinished = %s where usertel = %s', (username,sex,cateids,'2',usertel))
        session.pop("usertel")
        return redirect('/login')
    else:
        userid = session.get('userid')
        cur.execute('update user set username = %s,sex = %s,cateids = %s,isfinished = %s where userid = %s',
                    (username, sex, cateids, '2',userid))
        return redirect('/')

#登出
@app.route('/logout')
def logout():
    res = make_response(redirect('/'))
    session.pop("login")
    session.pop("userid")
    session.pop("username")
    return res


if __name__ == '__main__':
    app.run()
