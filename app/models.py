from app import db
from hashlib import md5

class User(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	nickname = db.Column(db.String(64), index=True, unique=True)
	email = db.Column(db.String(120), index=True, unique=True)
	posts = db.relationship('Post', backref='author', lazy='dynamic')
	about_me = db.Column(db.String(140))
	last_seen = db.Column(db.DateTime)

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

class Post(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Post %r>' % (self.body)
