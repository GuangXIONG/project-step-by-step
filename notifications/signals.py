from django.dispatch import Signal
from django.contrib.contenttypes.models import ContentType

from .models import Notification

def new_notification(sender, **kwargs):
	recipient = kwargs.get("recipient")
	verb = kwargs.get("verb")
	affected_users = kwargs.get('affected_users', None)

	if affected_users:
		for affected_user in affected_users:
			if affected_user == sender:
				pass
			else:
				print "user %s affected" % affected_user
				new_note = Notification(
					recipient=affected_user,
					verb=verb,
					sender_content_type=ContentType.objects.get_for_model(sender),
					sender_object_id=sender.id,
				)
				for option in ("target", "action"):
					try:
						obj = kwargs.get(option)
						if obj:
							setattr(new_note, "%s_content_type" % option, ContentType.objects.get_for_model(obj))
							setattr(new_note, "%s_object_id" % option, obj.id)
					except:
						pass
				new_note.save()
				print new_note
	else:
		new_note = Notification(
			recipient=recipient,
			verb=verb,  # smart_text
			sender_content_type=ContentType.objects.get_for_model(sender),
			sender_object_id=sender.id,
		)
		for option in ("target", "action"):
			obj = kwargs.get(option, None)
			if obj:
				setattr(new_note, "%s_content_type" % option, ContentType.objects.get_for_model(obj))
				setattr(new_note, "%s_object_id" % option, obj.id)
		new_note.save()


notify = Signal(providing_args=['recipient', 'verb', 'action', 'target', 'affected_users'])
notify.connect(new_notification)

"""below is the logic of notification"""

# another_user  (AUTH_USER_MODEL)
# has commented ("verb")
# with a Comment (id=32) (instance of action_object)
# on your Comment (id=12) (instance of target)
# so now you should know about it (AUTH_USER_MODEL)

# <instance of a user>
# <something> #verb to
# <instance of a model> #to
# <instance of a model> #tell
# <instance of a user>

"""

sender_content_type = models.ForeignKey(ContentType, related_name='nofity_sender')
sender_object_id = models.PositiveIntegerField()
sender_object = GenericForeignKey("sender_content_type", "sender_object_id")

verb = models.CharField(max_length=255)

action_content_type = models.ForeignKey(ContentType, related_name='notify_action', 
	null=True, blank=True)
action_object_id = models.PositiveIntegerField()
action_object = GenericForeignKey("action_content_type", "action_object_id")

target_content_type = models.ForeignKey(ContentType, related_name='notify_target', 
	null=True, blank=True)
target_object_id = models.PositiveIntegerField()
target_object = GenericForeignKey("target_content_type", "target_object_id")

recipient = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='notifications')

#read
#unread
timestamp = models.DateTimeField(auto_now_add=True, auto_now=False)
"""
