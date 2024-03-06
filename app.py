from flask import Flask, render_template, request , redirect
from flask_login import LoginManager, login_user , logout_user , UserMixin , current_user
from flask_sqlalchemy import SQLAlchemy
import datetime as dt

app = Flask(__name__)

# Tells flask-sqlalchemy what database to connect to
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.sqlite"
# Enter a secret key
app.config["SECRET_KEY"] = "KEY"
# Initialize flask-sqlalchemy extension
db = SQLAlchemy()

login_manager = LoginManager()
login_manager.init_app(app)

class Users(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(250), unique=True,
                         nullable=False)
    password = db.Column(db.String(250),
                         nullable=False)
    
class Notes(db.Model):
    note_id = db.Column(db.Integer, primary_key=True)
    id = db.Column(db.Integer)
    note = db.Column(db.String(250),
                         nullable=False)
    date = db.Column(db.DateTime,nullable=False,default=dt.datetime.now)
 
# Initialize app with extension
db.init_app(app)
# Create database within app context
 
with app.app_context():
    db.create_all()


@login_manager.user_loader
def loader_user(user_id):
    return Users.query.get(user_id)


@app.route('/', methods=['GET'])
def index():

    if current_user.is_authenticated:
        out_notes = Notes.query.filter(Notes.id == current_user.get_id())
      
        lis ={}
        for obj in out_notes.all():
            lis.update({obj.note_id : {'note':obj.note,'date':obj.date.strftime('%d-%m-%Y %H:%M %p')}})

        if out_notes is not None:
           
            return render_template("home.html", notes=lis)
    else:
        return render_template("home.html")


@app.route('/', methods = ['POST'])
def add_to_list():

        
    if current_user.is_authenticated:
        id = current_user.get_id()
        note = request.form.get("note")
        if note:
          note = note[0:249]
          in_note = Notes(id = id, note=note)
          db.session.add(in_note)
          db.session.commit() 
    return redirect('/', code=303)


@app.route('/login',methods = ['POST','GET'])
def login():

    if request.method == "POST":
        user = Users.query.filter_by(
            username=request.form.get("username")[0:19]).first()
      
        if user:
           
            if user.password == request.form.get("password"):
              
                login_user(user)
                return redirect("/")
           
    return render_template("login.html")



@app.route('/register', methods=['POST','GET'])
def register():

    if request.method == "POST":
        username=request.form.get("username")[0:19]
        password=request.form.get("password")[0:19]

        if username and password:
            user = Users.query.filter_by(username=username).first()
           
            if user:
                return render_template("register.html" , message="User Already Exist, Try another username")
            else:
                user = Users(username = username,password = password)
               
                db.session.add(user)
               
                db.session.commit()
                
                return redirect("/login")
    return render_template("register.html",message="")

@app.route('/logout',methods = ['POST','GET'])
def logout():
    logout_user()
    return redirect('/')

@app.route('/delete/<id>')
def delete_note(id):
  
    Notes.query.filter(Notes.note_id == id[0:19]).delete()
    db.session.commit()
    return redirect('/')

@app.route('/edit', methods=['POST','GET'])
def edit_note():
    data = request.json
    Notes.query.filter(Notes.note_id==data['id']).update({
        'note': data['edited_note'].strip()[0:249],
         'date': dt.datetime.now() })
    db.session.commit()
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)