import urllib2

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models.signals import post_save
from django.utils.text import slugify

from .utils import get_vid_for_direction

DEFAULT_MESSAGE = "Hello World~! Check out this awesome project step by step~!"


class VideoQuerySet(models.query.QuerySet):
	def active(self):
		return self.filter(active=True)

	def featured(self):
		return self.filter(featured=True)

	def has_embed(self):
		return self.filter(embed_code__isnull=False).exclude(embed_code__exact="")


class VideoManager(models.Manager):
	def get_queryset(self):
		return VideoQuerySet(self.model, using=self._db)

	def get_featured(self):
		return self.get_queryset().active().featured()

	def all(self):
		return self.get_queryset().active().has_embed()


class Video(models.Model):
	proj = models.ForeignKey("Project", null=True, blank=True)
	# project = models.ForeignKey("Project", default=1)
	title = models.CharField(max_length=120)
	embed_code = models.CharField(max_length=500, null=True, blank=True)
	share_message = models.TextField(default=DEFAULT_MESSAGE)
	order = models.PositiveIntegerField(default=1)
	slug = models.SlugField(null=True, blank=True)
	active = models.BooleanField(default=True)
	featured = models.BooleanField(default=False)
	free_preview = models.BooleanField(default=False)
	timestamp = models.DateTimeField(auto_now_add=True, auto_now=False, null=True)
	updated = models.DateTimeField(auto_now_add=False, auto_now=True, null=True)

	objects = VideoManager()

	class Meta:
		unique_together = ('slug', 'proj')
		ordering = ['order', '-timestamp']

	def __unicode__(self):
		return self.title

	def get_absolute_url(self):
		return reverse("video_detail", kwargs={"vid_slug": self.slug, "proj_slug": self.proj.slug})

	def get_share_link(self):
		full_url = "%s%s" % (settings.FULL_DOMAIN_NAME, self.get_absolute_url())
		return full_url

	def get_share_message(self):
		full_url = "%s%s" % (settings.FULL_DOMAIN_NAME, self.get_absolute_url())
		return urllib2.quote("%s %s" % (self.share_message, full_url))

	def get_next_url(self):
		video = get_vid_for_direction(self, "next")
		if video:
			return video.get_absolute_url()
		return None

	def get_previous_url(self):
		video = get_vid_for_direction(self, "previous")
		if video:
			return video.get_absolute_url()
		return None

	@property
	def has_preview(self):
		if self.free_preview:
			return True
		return False


# Django Signals sent when a sender instance.save() get invoked
def video_post_save_receiver(sender, instance, created, *args, **kwargs):
	print "Signal sent after a video instance %s saved" % instance.id
	if created:
		title_slug = slugify(instance.title)
		new_slug = "%s%s%s" % (instance.title, instance.proj.slug, instance.id)
		try:
			vid_exists = Video.objects.get(slug=title_slug, proj=instance.proj)
			instance.slug = slugify(new_slug)
			instance.save()
			print("video exists, new slug generated")
		except Video.DoesNotExist:
			instance.slug = title_slug
			instance.save()
			print "video created, title slug applied"
		except Video.MultipleObjectsReturned:
			instance.slug = slugify(new_slug)
			instance.save()
			print "multiple videos exist, new slug generated"
		except:
			pass

post_save.connect(video_post_save_receiver, sender=Video)


class ProjectQuerySet(models.query.QuerySet):
	def active(self):
		return self.filter(active=True)

	def featured(self):
		return self.filter(featured=True)


class ProjectManager(models.Manager):
	def get_queryset(self):
		return ProjectQuerySet(self.model, using=self._db)

	def get_featured(self):
		return self.get_queryset().active().featured()

	def all(self):
		return self.get_queryset().active()


class Project(models.Model):
	title = models.CharField(max_length=120)
	description = models.TextField(max_length=5000, null=True, blank=True)
	image = models.ImageField(upload_to='images/', null=True, blank=True)
	slug = models.SlugField(default='abc', unique=True)
	active = models.BooleanField(default=True)
	featured = models.BooleanField(default=False)
	timestamp = models.DateTimeField(auto_now_add=True, auto_now=False)
	updated = models.DateTimeField(auto_now_add=False, auto_now=True)

	objects = ProjectManager()

	class Meta:
		ordering = ['title', 'timestamp']

	def __unicode__(self):
		return self.title

	def get_absolute_url(self):
		return reverse("project_detail", kwargs={"proj_slug": self.slug})

	def get_image_url(self):
		return "%s%s" % (settings.MEDIA_URL, self.image)
