from flask import *
from PIL import Image
from datetime import  datetime
from resizeimage import resizeimage
import glob
import sqlite3
import os
app = Flask(__name__)
app.config['UPLOAD_DIR'] = 'static/Uploads'
root_dir = 'static/Uploads'
def get_post(id):
    con = sqlite3.connect("users.db")
    con.row_factory = sqlite3.Row
    user = con.execute('SELECT * FROM users WHERE id = ?',(id,)).fetchone()
    con.close()
    if user is None:
        abort(404)
    return user


@app.route("/")
def index():
    return render_template("index.html");

@app.route("/add")
def add():   
    return render_template("add.html")

@app.route("/savedetails",methods = ["POST","GET"])
def saveDetails():
    msg = "msg"
    if request.method == "POST":
        try:
            name = request.form["name"]
            email = request.form["email"]
            gender = request.form["gender"]
            contact = request.form["contact"]
            dob = request.form["dob"]
            file = request.files["profile_pic"]
            file.save(os.path.join(app.config['UPLOAD_DIR'],file.filename))
            with sqlite3.connect("users.db") as con:
                cur = con.cursor()   
                cur.execute("INSERT into users(name, email, gender, contact, dob, profile_pic) values (?,?,?,?,?,?)",(name,email,gender,contact,dob,file.filename))
                con.commit()   
        except:
            con.rollback()
            msg = "We can not add User to the list"
        finally:
            return redirect(url_for('add'))
            con.close()

@app.route("/view")
def view():    
    con = sqlite3.connect("users.db")
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    cur.execute("select * from users")   
    rows = cur.fetchall()
    return render_template("view.html",rows = rows,)

@app.route("/<int:id>/view_user", methods=("GET", "POST"))
def view_user(id):
    row = get_post(id)
    with sqlite3.connect("users.db") as con:
        cur = con.cursor()
        filename_or = row["profile_pic"]
        packages =  con.execute('Select date(dob) FROM users WHERE id = ?', (id,)).fetchone()
        for dob in packages:
            dob = datetime.strptime(dob, '%Y-%m-%d')
            age = (datetime.today() - dob).days/365
            age = round(age, 1)
    return render_template("view_user.html",row = row, now_date = age,)

@app.route("/<int:id>/resize_user", methods=("GET", "POST"))
def resize_user(id):
    row = get_post(id)
    with sqlite3.connect("users.db") as con:
        cur = con.cursor()
        filename_or = row["profile_pic"]
        with open('static/Uploads/' + filename_or, 'r+b') as f:
            with Image.open(f) as image:
                cover = resizeimage.resize_cover(image, [200, 200])
                cover.save('static/Uploads/' + filename_or, image.format)      
    return redirect(url_for('view'))

@app.route("/<int:id>/edit_user", methods=("GET", "POST"))
def edit_user(id):
    user = get_post(id)

    if request.method == 'POST':
        name = request.form["name"]
        email = request.form["email"]
        gender = request.form["gender"]
        contact = request.form["contact"]
        dob = request.form["dob"]
        with sqlite3.connect("users.db") as con:
            cur = con.cursor()
            query = '''
	    UPDATE users
	    SET name = ?, email = ?, gender = ?, contact = ?, dob = ? where id = ?
            '''
            cur.execute(query,(name,email,gender,contact,dob,id))
            con.commit()
            return redirect(url_for('view'))
    return render_template('edit_user.html', user = user)

@app.route('/<int:id>/delete_user', methods=("GET", "POST"))
def delete_user(id):
    user = get_post(id)
    with sqlite3.connect("users.db") as con:
        cur = con.cursor() 
        con.execute('DELETE FROM users WHERE id = ?', (id,))
        con.commit()
        return redirect(url_for('view'))
    

if __name__ == "__main__":
    app.run(debug = True)  