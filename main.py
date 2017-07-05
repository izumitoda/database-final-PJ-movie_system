from flask import Flask,render_template,request, session,redirect, flash
import pymssql

conn=pymssql.connect(host='DELL\\MSSQLSERVER1',user='erika',password='sql960930',database='film',charset='utf8',)

app = Flask(__name__)
app.secret_key = '123456'

@app.route('/logout')
def logout():
    if len(session)!=0:
        del session['username']
    return redirect('/index')

@app.route('/login')
def page_login():
    return render_template('login.html')

@app.route('/login', methods=["POST"])
def login():
    username = request.form['user_name']
    password = request.form['password']
    cursor = conn.cursor()
    str='select username,password from user_info where username='+'\''+username+'\''
    cursor.execute(str)
    result = cursor.fetchall()
    if len(result) == 0:
        flash('用户名不存在','error')
        return redirect('/login')
    if password != result[0][1]:
        flash('密码错误','error')
        return redirect('/login')
    session['username'] = username
    conn.commit()
    return redirect('/index')
    return render_template("login.html")

@app.route('/movie')
def movie_page():
    cursor=conn.cursor()
    cursor.execute('select * from film_info')
    result=cursor.fetchall()
    return render_template("movie.html",film=result)

@app.route('/')
def welcome():
    return redirect('/index')

@app.route('/register')
def reg_page():
    return render_template("register.html")

@app.route('/register',methods=['POST'])
def register():
    username=request.form['user_name']
    password=request.form['password']
    contact=request.form['contact']
    cursor = conn.cursor()
    str = 'select username,password from user_info where username=' + '\'' + username + '\''
    cursor.execute(str)
    result=cursor.fetchall()
    if len(result)!=0:
        flash("用户名已被占用",'error')
        return redirect('/register')
    if len(password)<6:
        flash("密码至少6个字符",'error')
        return redirect('/register')
    str='insert into user_info values(\''+username+'\',\''+contact+'\',\''+password+'\')'
    session['username']=username
    cursor.execute(str)
    conn.commit()
    return redirect('/index')

@app.route('/index')
def index_page():
    return render_template('index.html')

@app.route('/movie-<num>')
def single_movie(num):
    cursor=conn.cursor()
    cursor.execute('select * from film_info where num=%d',num)
    result=cursor.fetchall()
    cursor.execute('select * from have_seen where num=%d',num)
    review=cursor.fetchall()
    cursor.execute('select * from wanna_see where num=%d', num)
    wanna = cursor.fetchall()
    have=0
    want=0
    havesession=0
    if len(session)!=0:
        havesession=1
        for a in review:
            if a[0]==session['username']:
                have=1
                break
        for a in wanna:
            if a[0]==session['username']:
                want=1
                break
    return render_template('single.html',single=result,review=review,havesession=havesession,session=session,have=have,want=want)

@app.route('/movie-<num>',methods=['POST'])
def add_review(num):
    if len(session)==0:
        return redirect('/login')
    score = int(request.form['score'])
    review = request.form['short-review']
    name = session['username']
    strr = 'insert into have_seen values(' + '\'' + name + '\',' + str(num) + ',' + str(score) + ',\'' + review + '\')'
    cursor = conn.cursor()
    cursor.execute(strr)
    strr='delete from wanna_see where username=\''+session['username']+'\' and num='+str(num)
    cursor.execute(strr)
    strrr='/movie-'+str(num)
    conn.commit()
    return redirect(strrr)

@app.route('/search-<info>')
def search(info):
    cursor=conn.cursor()
    string='select * from film_info where film like'+'\'%'+info+'%'+'\''
    cursor.execute(string)
    result=cursor.fetchall()
    if len(result)==0:
        return redirect('/search-fail')
    return render_template('search.html',film=result)

@app.route('/searchdir-<director>')
def searchdir(director):
    cursor = conn.cursor()
    string = 'select * from film_info where director like' + '\'%' + director + '%' + '\''
    cursor.execute(string)
    result = cursor.fetchall()
    if len(result) == 0:
        return redirect('/search-fail')
    return render_template('search.html', film=result)
@app.route('/searchcountry-<country>')
def searchcon(country):
    cursor = conn.cursor()
    string = 'select * from film_info where country='+'\''+country+'\''
    cursor.execute(string)
    result = cursor.fetchall()
    if len(result) == 0:
        return redirect('/search-fail')
    return render_template('search.html', film=result)

@app.route('/search-fail')
def searchfail():
    return render_template('404.html')
@app.route('/movie-<num>-<username>-delete')
def delete_review(num,username):
    strr='delete from have_seen where username=\''+username+'\' and num='+str(num)
    cursor=conn.cursor()
    cursor.execute(strr)
    conn.commit()
    strrr = '/movie-' + str(num)
    return redirect(strrr)

@app.route('/movie-<num>-<username>-edit')
def edit(num,username):
    strr='select * from have_seen where username=\''+username+'\' and num='+str(num)
    cursor=conn.cursor()
    cursor.execute(strr)
    myreview=cursor.fetchall()
    cursor.execute('select * from film_info where num=%d',num)
    result=cursor.fetchall()
    cursor.execute('select * from have_seen where num=%d',num)
    review=cursor.fetchall()
    return render_template('edit.html',single=result,review=review,myreview=myreview)

@app.route('/movie-<num>-<username>-edit',methods=['POST'])
def editing(num,username):
    score = int(request.form['score'])
    review = request.form['short-review']
    strr='update have_seen set score='+str(score)+','+'review=\''+review+'\''+'where username=\''+username+'\' and num='+str(num)
    cursor=conn.cursor()
    cursor.execute(strr)
    conn.commit()
    strrr='/movie-'+str(num)
    return redirect(strrr)

@app.route('/movie-<num>-<username>-wannasee')
def wannasee(num,username):
    strr='insert into wanna_see values(\''+username+'\','+str(num)+')'
    cursor=conn.cursor()
    cursor.execute(strr)
    conn.commit()
    strrr = '/movie-' + str(num)
    return redirect(strrr)
@app.route('/movie-<num>-<username>-cancel')
def cancel(num,username):
    strr='delete from wanna_see where username='+'\''+username+'\' and num='+str(num)
    cursor=conn.cursor()
    cursor.execute(strr)
    conn.commit()
    strrr = '/movie-' + str(num)
    return redirect(strrr)
@app.route('/mypage')
def mypage():
    if len(session)==0:
        return redirect('/index')
    username=session['username']
    return username

@app.route('/user')
def homepage():
    if len(session)==0:
        return redirect('/login')
    strr = 'select * from have_seen,film_info where username=\'' + session['username']+'\' and film_info.num=have_seen.num'
    cursor=conn.cursor()
    cursor.execute(strr)
    haveseen=cursor.fetchall()
    strr='select * from user_info where username=\'' + session['username']+'\''
    cursor.execute(strr)
    info=cursor.fetchall()
    strr = 'select * from wanna_see,film_info where username=\'' + session['username'] + '\' and film_info.num=wanna_see.num'
    cursor.execute(strr)
    wanna = cursor.fetchall()
    no=0
    nowant=0
    if len(haveseen)==0:
        no=1
    if len(wanna)==0:
        nowant=1
    return render_template('homepage.html',info=info,haveseen=haveseen,no=no,wanna=wanna,nowant=nowant)

@app.route('/user-<username>')
def other_user(username):
    strr = 'select * from have_seen,film_info where username=\'' + username + '\' and film_info.num=have_seen.num'
    cursor = conn.cursor()
    cursor.execute(strr)
    haveseen = cursor.fetchall()
    strr = 'select * from user_info where username=\'' + username + '\''
    cursor.execute(strr)
    info=cursor.fetchall()
    strr = 'select * from wanna_see,film_info where username=\'' + session[
        'username'] + '\' and film_info.num=wanna_see.num'
    cursor.execute(strr)
    wanna = cursor.fetchall()
    strr = 'select * from follow where follower=\'' + session[
        'username'] + '\' and followee=\''+username+'\''
    cursor.execute(strr)
    fo = cursor.fetchall()
    strr = 'select * from follow where follower=\'' + username+ '\' and followee=\'' + session[
        'username'] + '\''
    cursor.execute(strr)
    foo = cursor.fetchall()
    nofo=0
    if len(fo)==0:
        nofo=1
    if len(foo)==1 and len(fo)==1:
        nofo=2
    no = 0
    nowant = 0
    if len(haveseen) == 0:
        no = 1
    if len(wanna) == 0:
        nowant = 1
    return render_template('otheruser.html', info=info, haveseen=haveseen, no=no, wanna=wanna, nowant=nowant,nofo=nofo)
@app.route('/follow-<user>-<username>')
def follow(user,username):
    strr='insert into follow values(\''+user+'\',\''+username+'\')'
    cursor=conn.cursor()
    cursor.execute(strr)
    conn.commit()
    strrr='/user-'+username
    return redirect(strrr)

@app.route('/cancel-<user>-<username>')
def cancelfo(user,username):
    strr='delete from follow where follower=\'' + session[
        'username'] + '\' and followee=\''+username+'\''
    cursor=conn.cursor()
    cursor.execute(strr)
    conn.commit()
    strrr='/user-'+username
    return redirect(strrr)
@app.route('/can-<user>-<username>')
def canfo(user,username):
    strr='delete from follow where follower=\'' + session[
        'username'] + '\' and followee=\''+username+'\''
    cursor=conn.cursor()
    cursor.execute(strr)
    conn.commit()
    strrr=user+'-follow'
    return redirect(strrr)

@app.route('/<user>-follow')
def myfollow(user):
    strr='select * from follow,user_info where follower=\''+user+'\' and user_info.username=follow.followee intersect '+'select followee,follower,username,contact,password from follow,user_info where followee=\'' + user + '\' and user_info.username=follow.follower'
    cursor=conn.cursor()
    cursor.execute(strr)
    result=cursor.fetchall()
    strr = 'select * from follow,user_info where follower=\'' + user + '\' and user_info.username=follow.followee except ' + 'select followee,follower,username,contact,password from follow,user_info where followee=\'' + user + '\' and user_info.username=follow.follower'
    cursor.execute(strr)
    fo = cursor.fetchall()
    have=1
    if len(result)==0:
        if len(fo)==0:
            have=4
        else:
            have=2
    return render_template("follow.html",result=result,have=have,fo=fo)

if __name__ == '__main__':
    app.run(debug=True)