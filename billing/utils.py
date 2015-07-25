import datetime

from django.conf import settings
from django.utils import timezone

from .signals import membership_dates_update

import braintree

braintree.Configuration.configure(
	braintree.Environment.Sandbox,
	merchant_id=settings.BRAINTREE_MERCHANT_ID,
	public_key=settings.BRAINTREE_PUBLIC_KEY,
	private_key=settings.BRAINTREE_PRIVATE_KEY
)


def check_braintree_subscription_status(subscription_id):
	# Checking in braintree
	subscription = braintree.Subscription.find(subscription_id)
	if subscription.status == "Active":
		status = True
		next_billing_date = subscription.next_billing_date
	else:
		status = False
		next_billing_date = None

	return status, next_billing_date


def update_braintree_subscription(user):
	membership = user.membership
	subscription_id = user.usermerchantid.subscription_id
	if membership.date_end <= timezone.now() and subscription_id:
		status, next_billing_date = check_braintree_subscription_status(subscription_id)
		if status:
			small_time = datetime.time(0, 0, 0, 1)
			datetime_obj = datetime.datetime.combine(next_billing_date, small_time)
			datetime_aware = timezone.make_aware(datetime_obj, timezone.get_current_timezone())
			membership_dates_update.send(membership, new_date_start=datetime_aware)
		else:
			membership.update_status()
	elif not subscription_id:
		membership.update_status()
	else:
		pass


