from django.conf import settings
from django.core.urlresolvers import reverse
from django.db import models
from django.utils.text import Truncator

from accounts.models import MyUser
from videos.models import Video


class CommentManager(models.Manager):
	def all(self):
		return super(CommentManager, self).filter(active=True).filter(parent=None)

	def recent(self):
		limit_to = settings.RECENT_COMMENT_NUMBER
		return self.get_queryset().filter(active=True).filter(parent=None)[:limit_to]

	def create_comment(self, user=None, text=None, path=None, video=None, parent=None):
		if not path:
			raise ValueError("Must include a path when adding a Comment")
		if not user:
			raise ValueError("Must include a user when adding a Comment")

		comment = self.model(user=user, path=path, text=text)
		if video:
			comment.video = video
		if parent:
			comment.parent = parent
		comment.save(using=self._db)
		return comment


class Comment(models.Model):
	user = models.ForeignKey(MyUser)
	parent = models.ForeignKey("self", null=True, blank=True)
	path = models.CharField(max_length=350)
	video = models.ForeignKey(Video, null=True, blank=True)
	text = models.TextField()
	updated = models.DateTimeField(auto_now=True, auto_now_add=False)
	timestamp = models.DateTimeField(auto_now=False, auto_now_add=True)
	active = models.BooleanField(default=True)

	objects = CommentManager()

	class Meta:
		ordering = ['-timestamp']

	def __unicode__(self):
		return self.text

	def get_absolute_url(self):
		return reverse('comment_thread', kwargs={"comment_id": self.id})

	@property
	def get_origin(self):
		return self.path

	@property
	def get_preview(self):
		return Truncator(self.text).chars(120)

	@property
	def get_comment(self):
		return self.text

	@property
	def is_child(self):
		return True if self.parent else False

	def get_children(self):
		return None if self.is_child else Comment.objects.filter(parent=self)

	def get_affected_users(self):
		""" 
		it needs to be a parent and have children, 
		the children, in effect, are the affected users.
		What's more, I think the parent user also need to be notified when thread changes.
		"""
		comment_children = self.get_children()
		if comment_children:
			users = set([comment.user for comment in comment_children])
			users.add(self.user)
			return users
		return None
