from scr.models.posts import Post
from scr.common.database import Database
from scr.models.blog import Blog

Database.initialize()

blog = Blog(author="Emily", title="Ciao Italy", description="My summer holiday in Rome",
            author_id="37fa056e33d44f60a96f1f2ba2292052")
blog.save_to_mongo()

