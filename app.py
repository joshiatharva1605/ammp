from flask import Flask,render_template,request,redirect
from config import db,cursor

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("login.html")

@app.route("/login",methods=["POST"])
def login():

    username=request.form["username"]
    password=request.form["password"]
    role=request.form["role"]

    query="SELECT * FROM login WHERE username=%s AND password=%s AND role=%s"
    cursor.execute(query,(username,password,role))

    user=cursor.fetchone()

    if user:

        if role=="admin":
            return redirect("/admin")

        elif role=="supervisor":
            return redirect("/supervisor")

    else:
        return "Invalid Login"


@app.route("/admin")
def admin():
    return render_template("admin_dashboard.html")


@app.route("/supervisor")
def supervisor():
    return render_template("supervisor_dashboard.html")


if __name__=="__main__":
    app.run(debug=True)