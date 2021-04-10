#如何成功跑出CSS：https://yanwei-liu.medium.com/python%E7%B6%B2%E9%A0%81%E8%A8%AD%E8%A8%88-flask%E4%BD%BF%E7%94%A8%E7%AD%86%E8%A8%98-%E4%BA%8C-89549f4986de
#包含css一定要放進static裡面，html一定要放進templates裡面之類的
from flask import Flask #載入Flask
from flask import request #載入Request物件
from flask import render_template, redirect, session, url_for, jsonify
import mysql.connector


runapp=Flask(              #載入runapplication物件，可以設定靜態檔案的路徑處理
    __name__,
    #static_folder="templates",  #只能有一個靜態資料夾  #靜態檔案的資料夾名稱(可以自訂，但要記得實體資料夾名稱也要同時改)
)

# Set the secret key to some random bytes. Keep this really secret!
runapp.secret_key = b'\xe8s\xb9\x0e\xddZ \xc3\x80\xa5\x1a\x11\x99J\xe7V'


mydb = mysql.connector.connect(
    host="127.0.0.1",
    user="root",
    password="*********",
    database="website"
)

mycursor = mydb.cursor()

#===========================================================================================================================================
#起始頁
@runapp.route("/") #基本路由設定語法 @runapp.route("路徑") <-> 動態路由設定語法 @runapp.route("/固定字首/<參數名稱>")
def home():  
    return render_template("homeWork-6-home.html")

#會員頁
@runapp.route("/member")
def success():
    if session.get("user"): #抓得到名為user的session嗎?
        return render_template("homeWork-6-sucess.html", msg=session["user"][1]) #成功登入的話將名為user的session寫出來，但因為session["user"]是tuple，所以要加上[1]選我要的。
    else:
        return redirect("/")

#登入失敗，跳到failure頁面
@runapp.route("/error/")
def failure():
    message=request.args.get("message")  #2. 將在1. 設定的字串get出來
    return render_template("homeWork-6-failure.html",msg=message)   #3. mes=mssage意思是把後端的東西傳到前端

#註冊
@runapp.route("/signup", methods = ["POST"])
def signup():
    mycursor.execute(f"SELECT * FROM user where username ='{request.values['username']}'")  #先執行SQL命令，去看request.values['username']有沒有已經在DB
    myresult = mycursor.fetchone()
    if myresult:
        return redirect("/error/?message=帳號已經被註冊")
    else:
        sql = "INSERT INTO user (name, username, password) VALUES (%s, %s, %s)"
        val = (request.values['user'], request.values['username'], request.values['password'])  #request.values['name']跟HTML中的input的name="user"要一致(""裡面是自己命名)
        mycursor.execute(sql, val)
        mydb.commit()  #寫入DB
        return redirect("/")

#登入
@runapp.route("/signin", methods = ['POST'])
def signin():
    if request.method == "POST":
        mycursor.execute(f"SELECT * FROM user where username='{request.form['username']}'")
        myresult = mycursor.fetchone()  #使用fetchone就不用使用fetchall，因為fetchall還要使用for迴圈抓資料出來
        if myresult and myresult[2]==request.form["username"] and myresult[3]==request.form["password"]: #先確認myresult有沒有存在；再確認username跟password正不正確。注意[]欄位是第幾個欄位!
            session["user"]=myresult     #命名session為user       
        #一定要先登入成功才能走到紀錄session的階段。
            #print(session["user"]) 可以print出來看看在terminal上有沒有印出session成功，按F12在網頁上的session應該是要加密後的結果。 
            return redirect("/member")
        else:
            return redirect("/error/?message=帳號與密碼不正確")
    else:
        return redirect("/error/?message=帳號與密碼不正確")  #1. 設定網址/?message要顯現的字串，message會根據後面配的字串，表現在html中，所以不用寫if


#登出
@runapp.route("/signout")
def signout():
    # remove the username from the session if it's there
    session.pop("user", None) #session的名字命名為user
    return redirect(url_for("home"))


@runapp.route("/api/users")
def api():
    username = request.args.get('username')
    
    failmessage = {
        "data": None
    }
    
    sql = "SELECT username FROM user WHERE username=%s"
    val = (username,)
    mycursor.execute(sql, val)
    count = len(mycursor.fetchall())
    if count < 1:
        return jsonify(failmessage)
    else:
        sql = "SELECT id FROM user WHERE username=%s"
        val = (username, )
        mycursor.execute(sql, val)
        id = mycursor.fetchall()
        id = str(id)[2:len(id)-4]
        sql = "SELECT name FROM user WHERE username=%s"
        val = (username,)
        mycursor.execute(sql, val)
        name = mycursor.fetchall()
        name = str(name)[3:len(name)-5]
        successmessage = {
            "data": {
                "id": int(id),
                "name": name,
                "username": username
            }
        }
        return jsonify(successmessage)

#===========================================================================================================================================

if __name__ == '__main__':
    runapp.run(debug=True, port=3000)   #加上debug=True，就可以不用每次改內容，都要關掉網頁後再重新打開，不用關掉視窗，重新整理後就可以更新內容