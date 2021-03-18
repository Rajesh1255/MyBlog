import os
import random
from flask import Flask, request, render_template, session, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy, event
from slugify import slugify
import pymysql
pymysql.install_as_MySQLdb()
from datetime import datetime
from werkzeug.utils import secure_filename
from flask_mail import Mail


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://{user}:{password}@{server}/{database}'.format(user='root', password='', server='localhost', database='myblog')
db = SQLAlchemy(app)
app.config['UPLOAD_FOLDER'] = 'static/upload/'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = '465'
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USERNAME'] = 'sr.rajeshsarkar@gmail.com'
app.config['MAIL_PASSWORD'] = 'rajesh_123'
mail = Mail(app)



app.secret_key = 'ItShouldBeAnythingButSecret'
user = {'username': "abc", 'firstname': "xyz"}

# image upload funtionalities
def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
def upload_image():
   if ('file' not in request.files):
      flash('No file part')
      return render_template('create.html', Title="Create", user = user['firstname'], end="Logout")
   file = request.files['file']
   if file.filename == '':
      flash('No image selected for uploading')
      return render_template('create.html', Title="Create", user = user['firstname'], end="Logout")
   if file and allowed_file(file.filename):
      filename = secure_filename(file.filename)
      file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
      return filename
   else:
      flash('Allowed image types are -> png, jpg, jpeg, gif')
      return render_template('create.html', Title="Create", user = user['firstname'], end="Logout")

# Post table in database
class Post(db.Model):
   sno = db.Column(db.Integer, nullable=True, primary_key=True)
   email = db.Column(db.String(120), nullable=False)
   fname = db.Column(db.String(120), nullable=False)
   title = db.Column(db.String(120), nullable=False)
   sub_title = db.Column(db.String(120), nullable=False)  
   update_date = db.Column(db.String(50), nullable=True)
   content = db.Column(db.String(500), nullable=False)
   slug = db.Column(db.String(120), nullable=False)
   mod_slug = db.Column(db.String(50), nullable=False)
   img = db.Column(db.String(120), nullable=False)
   date = db.Column(db.String(50), nullable=False)


class Signup(db.Model):
   sno = db.Column(db.Integer, nullable=True, primary_key=True)
   first_name = db.Column(db.String(120), nullable=False)
   last_name = db.Column(db.String(120), nullable=False)
   username = db.Column(db.String(120), nullable=True)
   bio = db.Column(db.String(120), nullable=True)
   img = db.Column(db.String(120), nullable=False)
   email = db.Column(db.String(120), nullable=False)
   password = db.Column(db.String(120), nullable=False)


@app.route("/")
def home():
   Posts = Post.query.filter_by().all()
   if('user' in session and session['user'] == user['username']):
      return render_template('home.html', Title="Home", user = user['firstname'], end="Logout", posts = Posts)
   return render_template('home.html', Title="Home", user="Login", end="Sign Up", posts = Posts)


@app.route("/create", methods = ['GET', 'POST'])
def create():
   if('user' in session and session['user'] == user['username']):
      if(request.method=='POST'):
         title = request.form.get('title')
         subtitle = request.form.get('subtitle')
         content = request.form.get('Content')
         slug = slugify(title)
         total_slug_with_same_pattern = Post.query.filter_by(slug = slug).count()
         mod_slug = slug + "+" + str((total_slug_with_same_pattern+1))
         email = user['username']
         fname = Signup.query.filter_by(email=email).first().first_name
         # image upload section
         file = upload_image()
         new= Post(title = title, sub_title=subtitle, content=content, slug = slug, mod_slug = mod_slug,email=email,fname=fname,img= file, date=datetime.now())
         db.session.add(new)
         db.session.flush()
         db.session.commit()
      return render_template('create.html', Title="Create", user = user['firstname'], end="Logout")
   else:
      return redirect('/login')

@app.route('/myblog')
def myblog():
   if('user' in session and session['user'] == user['username']):
      Posts = Post.query.filter_by(email = user['username']).all()
      Signups = Signup.query.filter_by(email=user['username']).first()
      default_path = "../static/profilepic.jpg"
      return render_template('myblog.html', Title="My Blog", user = user['firstname'], end="Logout", posts=Posts, signup=Signups,none=None)
   else:
      return redirect('/login')   

# profile
@app.route('/profile')
def profile():
   if('user' in session and session['user'] == user['username']):
      Posts = Signup.query.filter_by(email = user['username']).first()
      return render_template('profile.html', Title="My Profile", user = user['firstname'], end="Logout", posts=Posts)
   return redirect('/login')

#Change First Name
@app.route('/FirstName', methods=['GET', 'POST'])
def FirstName():
   if('user' in session and session['user'] == user['username']):
      if (request.method=='POST'):
         fname = request.form.get('fname')
         Signup.query.filter_by(email = user['username']).update({Signup.first_name: fname}, synchronize_session = False)
         db.session.commit()
         return redirect("/profile")
   return redirect('/login')


#Change Second Name
@app.route('/SecondName', methods=['GET', 'POST'])
def SecondName():
   if('user' in session and session['user'] == user['username']):
      if (request.method=='POST'):
         sname = request.form.get('lname')
         Signup.query.filter_by(email = user['username']).update({Signup.last_name: sname}, synchronize_session = False)
         db.session.commit()
         return redirect("/profile")
   return redirect('/login')

#Change User Name
@app.route('/UserName', methods=['GET', 'POST'])
def UserName():
   if('user' in session and session['user'] == user['username']):
      if (request.method=='POST'):
         uname = request.form.get('uname')
         Signup.query.filter_by(email = user['username']).update({Signup.username: uname}, synchronize_session = False)
         db.session.commit()
         return redirect("/profile")
   return redirect('/login')

#Change Bio
@app.route('/Bio', methods=['GET', 'POST'])
def Bio():
   if('user' in session and session['user'] == user['username']):
      if (request.method=='POST'):
         bio = request.form.get('bio')
         Signup.query.filter_by(email = user['username']).update({Signup.bio: bio}, synchronize_session = False)
         db.session.commit()
         return redirect("/profile")
   return redirect('/login')

#Change Password
@app.route('/Password', methods=['GET', 'POST'])
def Password():
   if('user' in session and session['user'] == user['username']):
      if (request.method=='POST'):
         password = request.form.get('password')
         cpassword = request.form.get('cpassword')
         if(password == cpassword):
            Signup.query.filter_by(email = user['username']).update({Signup.password: password}, synchronize_session = False)
            db.session.commit()
         else:
            flash("Password is wrong")
         return redirect("/profile")
   return redirect('/login')


#Change Profile Picture
@app.route('/Img', methods=['GET', 'POST'])
def Img():
   if('user' in session and session['user'] == user['username']):
      if (request.method=='POST'):
         img = upload_image()
         Signup.query.filter_by(email = user['username']).update({Signup.img: img}, synchronize_session = False)
         db.session.commit()
         return redirect("/profile")
   return redirect('/login')


# edit
@app.route('/edit/<string:mod_slug>', methods= ['GET', 'POST'])
def edit(mod_slug):
   if('user' in session and session['user'] == user['username']):
      Posts = Post.query.filter_by(mod_slug = mod_slug).first()
      if (request.method=='POST'):
         title = request.form.get('title')
         subtitle = request.form.get('subtitle')
         content = request.form.get('Content')
         file = upload_image()
         Post.query.filter_by(mod_slug = mod_slug).update({Post.title: title, Post.sub_title: subtitle, Post.content:content, Post.update_date: datetime.now(), Post.img: file}, synchronize_session = False)
         db.session.commit()
         return redirect("/myblog")
      else:   
         return render_template("edit.html", Title="My Content", user = user['firstname'], end="Logout", posts=Posts)
   return redirect('/') 


# delete
@app.route('/delete/<string:mod_slug>')
def delete(mod_slug):
   if('user' in session and session['user'] == user['username']):
      Post.query.filter_by(mod_slug = mod_slug).delete()
      db.session.commit()
   return redirect("/myblog")


# mycontent
@app.route('/mycontent/<string:mod_slug>')
def mycontent(mod_slug):
   if('user' in session and session['user'] == user['username']):
      Posts = Post.query.filter_by(mod_slug = mod_slug).first()
      return render_template('mycontent.html', Title="My Content", user = user['firstname'], end="Logout", posts=Posts)
   else:
      Posts = Post.query.filter_by(mod_slug = mod_slug).first()
      return render_template('mycontent.html', Title="My Content", user = "Login", end="Sign Up", posts=Posts)   

# login
@app.route('/login', methods=['GET', 'POST'])
def login():
   if('user' in session and session['user'] == user['username']):
      return redirect('/profile')
   if(request.method=='POST'):
      email=request.form.get('email')
      password=request.form.get('password')
      if((email == Signup.query.filter_by(email = email).first().email) and (password == Signup.query.filter_by(email = email).first().password)):
         session['user'] = Signup.query.filter_by(email = email).first().email
         user['username'] = Signup.query.filter_by(email = email).first().email
         user['firstname'] = Signup.query.filter_by(email = email).first().first_name
         return redirect("/")
         # return render_template('home.html', Title="Home")
      else:
         return render_template('login.html', Title="Login", warning="User Name or Password is wrong")   
   return render_template('login.html', Title="Login")

# signup
ottpp1=None
user_email1=None
@app.route('/signup', methods=['GET', 'POST'])
def signup():
   if('user' in session and session['user'] == user['username']):
      return redirect("/logout")
   if(request.method=='POST'):
      fname=request.form.get('fname')
      lname=request.form.get('lname')
      email=request.form.get('email')
      global user_email1
      user_email1=email
      password=request.form.get('password')
      cpassword=request.form.get('cpassword')
      if(Signup.query.filter_by(email = email).first() != None):
         return render_template('signup.html', Title="SignUp", warning="Email already exists")
      if(cpassword != password):
         return render_template('signup.html', Title="SignUp", warning="password not match")
      else:
         otp = random.randint(0000,9999)
         global ottpp1
         ottpp1=str(otp)
         msg = mail.send_message("Mail from My Blog",
                              body = "Your OTP for 'My Blog' New Account Creation is "+ str(otp), 
                              sender = 'sr.rajeshsarkar@gmail.com',
                              recipients = [email]
                              )
         new=Signup(first_name=fname, last_name=lname,email=email,password=password, img="profilepic.jpg")
         db.session.add(new)
         db.session.flush()
         db.session.commit()
         return render_template("new.html")
   return render_template('signup.html', Title="SignUp")
# New Account
@app.route('/new', methods=['GET', 'POST'])
def new():
   if(request.method=='POST'):
      global user_email1
      global ottpp1
      otp = request.form.get('otp')
      if (ottpp1 == otp):
         ottpp1 = None
         user_email1=None
         return redirect("/")
      else:
         Signup.query.filter_by(email = user_email1).delete()
         db.session.commit()
         ottpp1 = None
         user_email1=None
         return redirect("/signup")
   else:
      return render_template("new.html")



ottpp=None
user_email=None
@app.route('/forgetpassword_page1', methods=['GET', 'POST'])
def forgetpassword_page1():
   if(request.method=='POST'):
      email = request.form.get('email')
      otp = random.randint(0000,9999)
      global ottpp 
      global user_email
      ottpp = str(otp)
      user_email = email
      msg = mail.send_message("Mail from My Blog",
                              body = "Your OTP for 'My Blog' password reset is "+ str(otp), 
                              sender = 'sr.rajeshsarkar@gmail.com',
                              recipients = [email]
                              )
      return redirect("/otp")
   else:
      return render_template("forgetpassword_page1.html")

@app.route('/otp', methods=['GET', 'POST'])
def otp():
   if(request.method=='POST'):
      otp = request.form.get('otp')
      global ottpp
      if (ottpp == otp):
         ottpp = None
         return redirect("/forgetpassword_page2")
      else:
         return redirect("/forgetpassword_page1")
   else:
      return render_template("otp.html")


@app.route('/forgetpassword_page2', methods=['GET', 'POST'])
def forgetpassword_page2():
   if(request.method=='POST'):
      global user_email
      password = request.form.get('password')
      cpassword = request.form.get('cpassword')
      if(password == cpassword):
         Signup.query.filter_by(email = user_email).update({Signup.password: password}, synchronize_session = False)
         db.session.commit()
         user_email=None
         return redirect("/")
      else:
         return redirect("/forgetpassword_page1")
   else:
      return render_template("forgetpassword_page2.html")      



@app.route('/logout')
def logout():
   session.pop('user',None)         
   return redirect('/')

app.run(port=5000)