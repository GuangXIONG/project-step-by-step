import json

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render, Http404, HttpResponseRedirect, redirect, get_object_or_404

from .models import Notification


@login_required
def all_for_user(request):
	notifications = Notification.objects.all_for_user(request.user)
	context = {
		"notifications": notifications,
	}
	return render(request, "notifications/all.html", context)


@login_required
def read(request, id):
	notification = get_object_or_404(Notification, id=id)
	next_url = request.GET.get('next', None)
	try:
		if notification.recipient == request.user:
			notification.read = True
			notification.save()
			return HttpResponseRedirect(next_url) if next_url else redirect("notifications_all")
	except:
		raise Http404


@login_required
def get_notifications_ajax(request):
	if request.is_ajax() and request.method == "POST":
		notifications = Notification.objects.all_for_user(request.user).recent()
		count = notifications.count()
		notes = []
		for note in notifications:
			notes.append(str(note.get_link))
		data = {
			"notifications": notes,
			"count": count,
		}
		print data
		json_data = json.dumps(data)
		print json_data
		return HttpResponse(json_data, content_type='application/json')
	else:
		raise Http404
