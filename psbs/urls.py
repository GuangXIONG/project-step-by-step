from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin
from django.views.generic import TemplateView

urlpatterns = [
    url(r'^$', 'psbs.views.home', name='home'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^contact/$', TemplateView.as_view(template_name='contact_us.html'), name='contact_us'),

    # Projects and their videos
    url(r'^projects/$', 'videos.views.project_list', name='projects'),
    url(r'^projects/(?P<proj_slug>[\w-]+)/$', 'videos.views.project_detail', name='project_detail'),
    url(r'^projects/(?P<proj_slug>[\w-]+)/(?P<vid_slug>[\w-]+)/$', 'videos.views.video_detail', name='video_detail'),

    # Comment Thread
    url(r'^comment/(?P<comment_id>\d+)$', 'comments.views.comment_thread', name='comment_thread'),
    url(r'^comment/create/$', 'comments.views.comment_create_view', name='comment_create'),

    # Auth login/logout
    url(r'^account/$', 'accounts.views.account_home', name='account_home'),
    url(r'^logout/$', 'accounts.views.auth_logout', name='logout'),
    url(r'^login/$', 'accounts.views.auth_login', name='login'),
    url(r'^register/$', 'accounts.views.auth_register', name='register'),

    # Billing
    url(r'^upgrade/$', 'billing.views.upgrade', name='account_upgrade'),
    url(r'^billing/$', 'billing.views.billing_history', name='billing_history'),
    url(r'^billing/cancel/$', 'billing.views.cancel_subscription', name='cancel_subscription'),

    # Notifications for ContentType
    url(r'^notifications/$', 'notifications.views.all_for_user', name='notifications_all'),
    url(r'^notifications/ajax/$', 'notifications.views.get_notifications_ajax', name='get_notifications_ajax'),
    url(r'^notifications/(?P<id>\d+)/$', 'notifications.views.read', name='notifications_read'),
]

# if settings.DEBUG:
#     urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
#     urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
