import datetime
import random

from django.conf import settings
from django.contrib.auth.signals import user_logged_in
from django.db import models
from django.db.models.signals import post_save
from django.utils import timezone

from .signals import membership_dates_update
from .utils import update_braintree_subscription


def user_logged_in_receiver(sender, user, **kwargs):
	try:
		update_braintree_subscription(user)
	except:
		pass

user_logged_in.connect(user_logged_in_receiver)


class Membership(models.Model):
	user = models.OneToOneField(settings.AUTH_USER_MODEL)
	date_start = models.DateTimeField(default=timezone.now(), verbose_name='Start Date')
	date_end = models.DateTimeField(default=timezone.now(), verbose_name='End Date')

	def __unicode__(self):
		return str(self.user.username)

	def update_status(self):
		if self.date_end >= timezone.now():
			self.user.is_member = True
			self.user.save()
		elif self.date_end < timezone.now():
			self.user.is_member = False
			self.user.save()
		else:
			pass


def update_membership_status(sender, instance, created, **kwargs):
	if not created:
		instance.update_status()

post_save.connect(update_membership_status, sender=Membership)

def membership_update_dates_receiver(sender, new_date_start, **kwargs):
	membership = sender
	current_date_end = membership.date_end
	if not new_date_start or current_date_end >= new_date_start:
		# Append new_start date plus offset to end date of the instance
		membership.date_end = current_date_end + datetime.timedelta(days=30, hours=10)
		membership.save()
	else:
		# Set a new start date and new end date with the same offset.
		membership.date_start = new_date_start
		membership.date_end = new_date_start + datetime.timedelta(days=30, hours=10)
		membership.save()

membership_dates_update.connect(membership_update_dates_receiver)


class TransactionManager(models.Manager):
	def create_new(self, user, transaction_id,
	               amount, card_type, success=None,
	               transaction_status=None, last_four=None):
		if not user:
			raise ValueError("Must be a user")
		if not transaction_id:
			raise ValueError("Must complete a transaction to create new one in database.")
		new_order_id = "%s%s%s" % (transaction_id[:2], random.randint(1, 23423), transaction_id[2:])
		new_trans = self.model(
			user=user,
			transaction_id=transaction_id,
			order_id=new_order_id,
			amount=amount,
			card_type=card_type
		)
		if success:
			new_trans.success = success
			new_trans.transaction_status = transaction_status
		if last_four:
			new_trans.last_four = last_four
		new_trans.save(using=self._db)
		return new_trans

	def all_for_user(self, user):
		return super(TransactionManager, self).filter(user=user)

	def get_recent_for_user(self, user, num):
		return self.all_for_user(user)[:num]


class Transaction(models.Model):
	user = models.ForeignKey(settings.AUTH_USER_MODEL)
	# for braintree or stripe
	transaction_id = models.CharField(max_length=120)
	# for internal use
	order_id = models.CharField(max_length=120)
	amount = models.DecimalField(max_digits=100, decimal_places=2)
	success = models.BooleanField(default=True)
	transaction_status = models.CharField(max_length=220, null=True, blank=True)
	card_type = models.CharField(max_length=120)
	last_four = models.PositiveIntegerField(null=True, blank=True)
	timestamp = models.DateTimeField(auto_now_add=True, auto_now=False)

	objects = TransactionManager()

	def __unicode__(self):
		return self.order_id

	class Meta:
		ordering = ['-timestamp']


class UserMerchantId(models.Model):
	user = models.OneToOneField(settings.AUTH_USER_MODEL)
	customer_id = models.CharField(max_length=120)
	subscription_id = models.CharField(max_length=120, null=True, blank=True)
	plan_id = models.CharField(max_length=120, null=True, blank=True)
	merchant_name = models.CharField(max_length=120, default="Braintree")

	def __unicode__(self):
		return self.customer_id
