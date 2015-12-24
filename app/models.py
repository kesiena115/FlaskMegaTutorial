from app import db
from hashlib import md5
from app import app
import sys

if sys.version_info >= (3, 0):
    enable_search = False
else:
    enable_search = True
    import flask.ext.whooshalchemy as whooshalchemy


followers = db.Table('followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
)


class User(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	nickname = db.Column(db.String(64), index=True, unique=True)
	email = db.Column(db.String(120), index=True, unique=True)
	posts = db.relationship('Post', backref='author', lazy='dynamic')
	about_me = db.Column(db.String(140))
	last_seen = db.Column(db.DateTime)
	followed = db.relationship('User', 
								secondary=followers, 
								primaryjoin=(followers.c.follower_id == id), 
								secondaryjoin=(followers.c.followed_id == id), 
								backref=db.backref('followers', lazy='dynamic'), 
								lazy='dynamic')

	'''
		The is_authenticated property has a misleading name. In general this method should just return True unless the 
		object represents a user that should not be allowed to authenticate for some reason.
	'''
	@property
	def is_authenticated(self):
		return True

	# Should return True for users unless they are inactive, for example because they have been banned.
	@property
	def is_active(self):
		return True

	#  Should return True only for fake users that are not supposed to log in to the system.
	@property
	def is_anonymous(self):
		return False

	# Should return a unique identifier for the user, in unicode format.
	def get_id(self):
		try:
			return unicode(self.id)  # python 2
		except NameError:
			return str(self.id)  # python 3

	def __repr__(self):
		return'<User %r>' % (self.nickname)

	def avatar(self, size):
		'''
			Returns the URL of the user's avatar image, scaled to the requested size in pixels.
		'''
		return 'http://www.gravatar.com/avatar/%s?d=mm&s=%d' % (md5(self.email.encode('utf-8')).hexdigest(), size)

	def follow(self, user):
		'''
			The follow and unfollow methods are defined so that they return an object when they succeed or None when they fail. 
			When an object is returned, this object has to be added to the database session and committed.
		'''
		if not self.is_following(user):
			self.followed.append(user)
			return self

	def unfollow(self, user):
		'''
			The follow and unfollow methods are defined so that they return an object when they succeed or None when they fail. 
			When an object is returned, this object has to be added to the database session and committed.
		'''
		if self.is_following(user):
			self.followed.remove(user)
			return self

	def is_following(self, user):
		return self.followed.filter(followers.c.followed_id == user.id).count() > 0

	def followed_posts(self):
		'''
		This method returns a query object, not the results. This is similar to how relationships with lazy = 'dynamic' work. 
		It is always a good idea to return query objects instead of results, because that gives the caller the choice of adding more 
		clauses to the query before it is executed.
		'''
		return Post.query.join(followers, (followers.c.followed_id == Post.user_id)).filter(followers.c.follower_id == self.id).order_by(Post.timestamp.desc())

	@staticmethod
	def make_unique_nickname(nickname):
		if User.query.filter_by(nickname=nickname).first() is None:
			return nickname
		version = 2
		while True:
			new_nickname = nickname + str(version)
			if User.query.filter_by(nickname=new_nickname).first() is None:
				break
			version += 1
		return new_nickname


class Post(db.Model):
	__searchable__ = ['body'] # Required by whoosh

	id = db.Column(db.Integer, primary_key = True)
	body = db.Column(db.String(140))
	timestamp = db.Column(db.DateTime)
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

	def __repr__(self):
		return '<Post %r>' % (self.body)


if enable_search:
    whooshalchemy.whoosh_index(app, Post)