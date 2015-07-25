from django.contrib.contenttypes.models import ContentType
from django.db.models import Count
from django.shortcuts import render

from accounts.forms import RegisterForm, LoginForm

from analytics.models import PageView
from analytics.signals import page_view
from comments.models import Comment
from videos.models import Video, Project


def home(request):
	page_view.send(request.user, page_path=request.get_full_path())

	if request.user.is_authenticated():
		page_view_list = request.user.pageview_set.get_videos()[:6]
		recent_videos = []
		for obj in page_view_list:
			if obj.primary_object not in recent_videos:
				recent_videos.append(obj.primary_object)
		recent_comments = Comment.objects.recent()

		# Top videos showed on homepage
		video_type = ContentType.objects.get_for_model(Video)
		popular_videos_list = PageView.objects.filter(primary_content_type=video_type) \
			.values("primary_object_id").annotate(the_count=Count("primary_object_id")) \
			.order_by("-the_count")[:5]
		popular_videos = []
		for item in popular_videos_list:
			try:
				new_video = Video.objects.get(id=item['primary_object_id'])
				popular_videos.append(new_video)
			except:
				pass

		print 'yoyoyo', popular_videos
		# !!!This is where recommended items and recommendation system play a role in future
		random_videos = Video.objects.all().order_by('?')[:10]
		# recommended_items = random_videos

		context = {
			"random_videos": random_videos,
			"recent_videos": recent_videos,
			"recent_comments": recent_comments,
			"popular_videos": popular_videos,
		}
		template = "accounts/home_logged_in.html"
	else:
		featured_categories = Project.objects.get_featured()
		featured_videos = Video.objects.get_featured()
		login_form = LoginForm()
		register_form = RegisterForm()
		template = "accounts/home_visitor.html"
		context = {
			"register_form": register_form,
			"login_form": login_form,
			"featured_videos": featured_videos,
			"featured_categories": featured_categories,
		}

	return render(request, template, context)

# @login_required(login_url='/staff/login/')
# def staff_home(request):
# 	context = {
#
# 	}
# 	return render(request, "home.html", context)


# def home(request):
# 	if request.user.is_authenticated():
# 		print
# 		name = "Justin"
# 		videos = Video.objects.all()
# 		embeds = []

# 		for vid in videos:
# 			code = mark_safe(vid.embed_code)
# 			embeds.append("%s" %(code))

# 		context = {
# 			"the_name": name,
# 			"number": videos.count(),
# 			"videos": videos,
# 			"the_embeds": embeds,
# 			"a_code": mark_safe(videos[0].embed_code)
# 		}
# 		return render(request, "home.html", context)
# 	#redirect to login
# 	else:
# 		return HttpResponseRedirect('/login/')
