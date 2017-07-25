from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy 

# Note: the connection string after :// contains the following info:
# user:password@server:portNumber/databaseName

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI']='mysql+pymysql://blogz:blogz@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key= "derp"



class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(300))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner= owner

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20))
    password = db.Column(db.String(20))
    blog = db.relationship('Blog', backref='owner')


    def __init__(self, username, password):
        self.username = username
        self.password = password

@app.before_request
def require_login():
    allowed_routes = ['login', 'signup', 'index', 'blogs']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

@app.route("/newpost", methods=['POST', 'GET'])
def newpost():
    blog_owner = User.query.filter_by(username= session['username']).first()
    title = ''
    body = ''

    if request.method=='POST':
        title = request.form['title']
        body = request.form['body']
        if title and body:
            new_post = Blog(title, body, blog_owner)
            db.session.add(new_post)
            db.session.commit()
            return redirect('./ind-blog?id=' + str(new_post.id))
        else:
            if not title:
                flash("please enter a title", "error0")
            if not body:
                flash("please enter a body", "error1")
            

    return render_template('newpost.html', title=title, body=body)



@app.route('/ind-blog', methods=['POST', 'GET'])
def ind_blog():
    post_id= int(request.args.get("id"))
    posting = Blog.query.filter_by(id=post_id)
    return render_template("ind-blog.html", posting=posting, username=session['username'])


@app.route('/signup', methods=['POST','GET'])
def signup():
    
    if request.method=='POST':
        errors=[]
        username= request.form["username"]
        password = request.form["password"]
        verify = request.form["verify"]

        error1=''
        if len(username) <4 or username.isalpha()==False: #verify username
            error1 = 'Please enter a valid username' 
            errors.append(error1)

        error2=''
        if len(password) < 4: #verify password
            error2= "Please enter a valid password of atleast 3 characters."
            errors.append(error2)
    
        error3=''
        if verify != password: # verify verification password.
            error3 = "Password does not match"
            errors.append(error3)
        if not verify:
            error3="Please re-enter password to verify"
    
        if len(errors) > 0:# if errors render template with errors
            return render_template('signup.html', error1=error1, error2=error2,error3=error3)
        
        #Check if user exists if not add to session and commit to database
        existing_user = User.query.filter_by(username=username).first()
        if not existing_user:
            new_user = User(username,password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            flash("logged in")
            return redirect('/newpost')
        else:
            flash("User account already exists",'error')
            return render_template('signup.html')

    return render_template('signup.html')

@app.route('/login', methods=['POST','GET'])
def login():
    if request.method=='POST':
        username= request.form['username']
        password= request.form['password']
        user_check= User.query.filter_by(username=username).first()
        
        if user_check == None:
            flash('Username does not exist')
            return render_template('login.html')

        if password != user_check.password:
            flash('Password is incorrect')
            return render_template('login.html')

        if password == user_check.password:
            session['username']=user_check.username
            flash('You are logged in as '+user_check.username)
            return render_template('login.html')


    return render_template('login.html')


@app.route('/logout', methods=['POST','GET'])
def logout():
    del session['username']
    return redirect('/login')
    
@app.route('/blogs', methods=['GET', 'POST'])
def blogs():
    user_id= request.args.get('userid')
    ses_username=request.args.get('username')

    if user_id:
        user = User.query.filter_by(id=user_id).first()
        users_blogs= Blog.query.filter_by(owner_id= user.id).all()
        return render_template('blog.html', blog=users_blogs, user=user)
    if ses_username:
        user= User.query.filter_by(username = ses_username).first()
        users_blogs = Blog.query.filter_by(owner_id=user.id).all()
        return render_template('blog.html', blog=users_blogs, user=user)

    


@app.route('/', methods=['POST', 'GET'])
def index():
    users = User.query.all()
    return render_template("index.html", users=users)







if __name__ == '__main__':
    app.run()