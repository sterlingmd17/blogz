from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy 

# Note: the connection string after :// contains the following info:
# user:password@server:portNumber/databaseName

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI']='mysql+pymysql://build-a-blog:build-a-blog@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key= "derp"

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(300))

    def __init__(self, title, body):
        self.title = title
        self.body = body


@app.route("/newpost", methods=['POST', 'GET'])
def newpost():
    title = request.form['title']
    body = request.form['body']
    if request.method=='POST':
        if title and body:
            new_post = Blog(title, body)
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
    return render_template("ind-blog.html", posting=posting)


@app.route('/', methods=['POST', 'GET'])
def index():
    posts = Blog.query.all()
    return render_template("blog.html", posts=posts)

if __name__ == '__main__':
    app.run()