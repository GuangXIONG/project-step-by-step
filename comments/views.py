from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, Http404, HttpResponseRedirect, get_object_or_404, redirect

from accounts.models import MyUser
from notifications.signals import notify
from videos.models import Video

from .models import Comment
from .forms import CommentForm


@login_required
def comment_thread(request, comment_id):
	comment = get_object_or_404(Comment, id=comment_id)
	form = CommentForm()
	context = {
		"form": form,
		"comment": comment,
	}
	return render(request, "comments/comment_thread.html", context)


def comment_create_view(request):
	if request.method == "POST" and request.user.is_authenticated():
		parent_id = request.POST.get('parent_id')
		video_id = request.POST.get("video_id")
		origin_path = request.POST.get("origin_path")
		try:
			video = Video.objects.get(id=video_id)
		except:
			video = None

		parent_comment = None
		if parent_id:
			try:
				parent_comment = Comment.objects.get(id=parent_id)
			except:
				parent_comment = None

			if parent_comment and parent_comment.video:
				video = parent_comment.video

		form = CommentForm(request.POST)
		if form.is_valid():
			comment_text = form.cleaned_data['comment']
			if parent_comment:
				new_comment = Comment.objects.create_comment(
					user=request.user,
					path=parent_comment.get_origin,
					text=comment_text,
					video=video,
					parent=parent_comment
				)
				affected_users = parent_comment.get_affected_users()
				notify.send(
					request.user,
					action=new_comment,
					target=parent_comment,
					recipient=parent_comment.user,
					affected_users=affected_users,
					verb='replied to'
				)
				messages.success(request, "Thank you for your response.", extra_tags='safe')
				return HttpResponseRedirect(parent_comment.get_absolute_url())
			else:
				new_comment = Comment.objects.create_comment(
					user=request.user,
					path=origin_path,
					text=comment_text,
					video=video
				)
				# option to send to super user or staff users
				notify.send(
					request.user,
					recipient=MyUser.objects.get(username='admin'),
					action=new_comment,
					target=new_comment.video,
					verb='commented on'
				)
				messages.success(request, "Thank you for the comment.")
				return HttpResponseRedirect(new_comment.get_absolute_url())
		else:
			messages.error(request, "There was an error with your comment.")
			return HttpResponseRedirect(origin_path)
	else:
		return redirect('login')
