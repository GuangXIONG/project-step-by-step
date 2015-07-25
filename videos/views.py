from django.core.urlresolvers import reverse
from django.shortcuts import render, HttpResponseRedirect, get_object_or_404

from analytics.signals import page_view
from comments.forms import CommentForm
from .models import Video, Project


def project_list(request):
	queryset = Project.objects.all()
	context = {
		"queryset": queryset,
	}
	return render(request, "videos/project_list.html", context)


def project_detail(request, proj_slug):
	proj = get_object_or_404(Project, slug=proj_slug)
	video_queryset = proj.video_set.all()
	page_view.send(request.user, page_path=request.get_full_path(), primary_obj=proj)
	context = {
		"project": proj,
		"queryset": video_queryset,
	}
	return render(request, "videos/project_detail.html", context)


def video_detail(request, proj_slug, vid_slug):
	proj = get_object_or_404(Project, slug=proj_slug)
	vid = get_object_or_404(Video, slug=vid_slug, proj=proj)
	page_view.send(
		request.user,
		page_path=request.get_full_path(),
		primary_obj=vid,
		secondary_obj=proj
	)
	if request.user.is_authenticated() or vid.has_preview:
		if vid.has_preview or request.user.is_member:
			comments = vid.comment_set.all()
			for comment in comments:
				comment.get_children()
			comment_form = CommentForm()
			context = {
				"video": vid,
				"comments": comments,
				"comment_form": comment_form
			}
			return render(request, "videos/video_detail.html", context)
		else:
			# upgrade account and set the current video url as the next url once the upgrade completes.
			next_url = vid.get_absolute_url()
			return HttpResponseRedirect("%s?next=%s" % (reverse('account_upgrade'), next_url))
	else:
		# let visitor login and set the current video url as the next usl once the login completes.
		next_url = vid.get_absolute_url()
		return HttpResponseRedirect("%s?next=%s" % (reverse('login'), next_url))
