from flask import Flask, render_template, request, session, make_response

from scr.models.posts import Post
from scr.models.user import User
from scr.common.database import Database
from scr.models.blog import Blog

app = Flask(__name__)  # __main__
app.secret_key = 'sk'


@app.route('/register')
def register_template():
    return render_template('register.html')


@app.route('/')
def login_template():
    return render_template('login.html')


@app.before_first_request
def initialize_database():
    Database.initialize()


@app.route('/auth/login', methods=['POST'])
def login_user():
    email = request.form['email']
    password = request.form['password']

    if User.login_valid(email, password):
        # session['email'] = email
        User.login(email)
    else:
        session['email'] = None
    return render_template('profile.html', email=session['email'])


@app.route('/auth/register', methods=['POST'])
def register_user():
    email = request.form['email']
    password = request.form['password']

    User.register(email, password)

    return render_template('profile.html', email=session['email'])


@app.route('/blogs/<string:user_id>')
@app.route('/blogs')
def user_blog(user_id=None):
    if user_id is not None:
        user = User.get_by_id(user_id)
    else:
        user = User.get_by_email(session['email'])
    blogs = user.get_blogs()

    return render_template("user_blogs.html", blogs=blogs, email=user.email)


@app.route('/blog/new', methods=['POST', 'GET'])
def creat_new_blog():
    if request.method == 'GET':
        return render_template('new_blog.html')
    else:
        title = request.form["title"]
        description = request.form["description"]
        user = User.get_by_email(session["email"])

        new_blog = Blog(author=user.email, title=title, description=description, author_id=user._id)
        new_blog.save_to_mongo()

        return make_response(user_blog(user._id))


@app.route('/post/new/<string:blog_id>', methods=['POST', 'GET'])
def creat_new_post(blog_id):
    if request.method == 'GET':
        return render_template('new_post.html', blog_id=blog_id)
    else:
        title = request.form["title"]
        content = request.form["content"]
        user = User.get_by_email(session['email'])

        new_post = Post(blog_id=blog_id, title=title, content=content, author=user.email)
        new_post.save_to_mongo()

        return make_response(blog_posts(blog_id))


@app.route('/posts/<string:blog_id>')
def blog_posts(blog_id):
    blog = Blog.from_mongo(blog_id)
    posts = blog.get_posts()

    return render_template("posts.html", posts=posts, blog_title=blog.title, blog_id=blog._id)


if __name__ == "__main__":
    app.debug = True
    app.run()
