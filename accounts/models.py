from django.contrib.auth.models import BaseUserManager, AbstractBaseUser
from django.db import models
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.signals import user_logged_in
from django.db.models.signals import post_save
from django.utils import timezone

from billing.models import Membership, UserMerchantId
from notifications.signals import notify

import braintree

braintree.Configuration.configure(
	braintree.Environment.Sandbox,
	merchant_id=settings.BRAINTREE_MERCHANT_ID,
	public_key=settings.BRAINTREE_PUBLIC_KEY,
	private_key=settings.BRAINTREE_PRIVATE_KEY
)


class MyUserManager(BaseUserManager):
	def create_user(self, username=None, email=None, password=None):
		if not username:
			raise ValueError('Must provide username !')

		if not email:
			raise ValueError('Users must have an email address !')

		user = self.model(username=username, email=self.normalize_email(email))
		user.set_password(password)
		user.save(using=self._db)
		return user

	def create_superuser(self, username, email, password):
		user = self.create_user(username=username, email=email, password=password)
		user.is_admin = True
		user.save(using=self._db)
		return user


class MyUser(AbstractBaseUser):
	username = models.CharField(max_length=255, unique=True)
	email = models.EmailField(verbose_name='email address', max_length=255, unique=True)
	first_name = models.CharField(max_length=120, null=True, blank=True)
	last_name = models.CharField(max_length=120, null=True, blank=True)
	is_member = models.BooleanField(default=False, verbose_name='Is Paid Member')
	is_active = models.BooleanField(default=True)
	is_admin = models.BooleanField(default=False)

	objects = MyUserManager()

	# A string describing the name of the field on the User model that is used as the UNIQUE identifier
	USERNAME_FIELD = 'username'
	# A list of the field names that will be prompted for when creating a user via the createsuperuser
	REQUIRED_FIELDS = ['email']

	def __unicode__(self):
		return self.username

	def get_full_name(self):
		return "%s %s" % (self.first_name, self.last_name)

	def get_short_name(self):
		return self.first_name

	def has_perm(self, perm, obj=None):
		# "Does the user have a specific permission?"
		# Simplest possible answer: Yes, always
		return True

	def has_module_perms(self, app_label):
		# "Does the user have permissions to view the app `app_label`?"
		# Simplest possible answer: Yes, always
		return True

	@property
	def is_staff(self):
		# "Is the user a member of staff?"
		# Simplest possible answer: All admins are staff
		return self.is_admin

def user_logged_in_membership(sender, request, user, **kwargs):
	request.session.set_expiry(60 * 60)
	membership_obj, created = Membership.objects.get_or_create(user=user)
	if created:
		membership_obj.date_start = timezone.now()
		membership_obj.save()
		user.is_member = True
		user.save()
	user.membership.update_status()

user_logged_in.connect(user_logged_in_membership)


class UserProfile(models.Model):
	user = models.OneToOneField(MyUser)
	bio = models.TextField(null=True, blank=True)
	facebook_link = models.CharField(max_length=320, null=True, blank=True, verbose_name='Facebook profile url')

	def __unicode__(self):
		return self.user.username


def new_user_receiver(sender, instance, created, *args, **kwargs):
	if created:
		new_profile, is_created = UserProfile.objects.get_or_create(user=instance)
		print new_profile, is_created
		# Notify admin user of new users
		notify.send(instance, recipient=MyUser.objects.get(username='admin'), verb='New User Created.')

	# for each new user, try to create a merchant account customer id used in braintree (or stripe)
	try:
		merchant_obj = UserMerchantId.objects.get(user=instance)
	except:
		new_customer_result = braintree.Customer.create({
			"email": instance.email
		})
		if new_customer_result.is_success:
			merchant_obj, created = UserMerchantId.objects.get_or_create(user=instance)
			merchant_obj.customer_id = new_customer_result.customer.id
			merchant_obj.save()
			print "Customer created with id = {0}".format(new_customer_result.customer.id)
		else:
			print "Error: {0}".format(new_customer_result.message)
			# messages.error(request, "There was an error with your account. Please contact us.")
			messages.error(None, "There was an error with your account. Please contact us.")

		# Send email for verifying user email in future

post_save.connect(new_user_receiver, sender=MyUser)
