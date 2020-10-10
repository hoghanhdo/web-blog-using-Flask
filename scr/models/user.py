from flask import session

from scr.common.database import Database
from scr.models.blog import Blog
import uuid
import datetime


class User(object):

    def __init__(self, email, password, _id=None):
        self.email = email
        self.password = password
        self._id = uuid.uuid4().hex if _id is None else _id

    @classmethod
    def get_by_email(cls, email):
        user = Database.find_one(collection='user', query={'email': email})
        if user is not None:
            return cls(**user)
        return None

    @classmethod
    def get_by_id(cls, _id):
        user = Database.find_one(collection='user', query={'_id': _id})
        if user is not None:
            return cls(**user)
        return None

    # Check combination of email and password
    @staticmethod
    def login_valid(email, password):
        user = User.get_by_email(email)
        if user is not None:
            return user.password == password
        return

    @classmethod
    def register(cls, email, password):
        user = User.get_by_email(email)
        if user is None:
            new_user = cls(email, password)
            new_user.save_to_mongo()
            session['email'] = email
            return True
        else:
            return False
        # change to exception handling

    def json(self):
        return {
            'email': self.email,
            '_id': self._id,
            'password': self.password
        }

    def save_to_mongo(self):
        Database.insert(collection='user', data=self.json())

    @staticmethod
    def login(email):
        session['email'] = email

    @staticmethod
    def logout(email):
        session['email'] = None

    def get_blogs(self):
        return Blog.find_by_author_id(self._id)

    def creat_new_blog(self, title, description):
        blog = Blog(author=self.email,
                    title=title,
                    description=description,
                    author_id=self._id)
        blog.save_to_mongo()

    # One user may own more than 1 blog, decide which blog to write a new post
    @staticmethod
    def create_new_post(blog_id, title, content, created_date=datetime.datetime.utcnow()):
        blog = Blog.from_mongo(blog_id)
        blog.write_new_post(title=title,
                            content=content,
                            created_date=created_date)
