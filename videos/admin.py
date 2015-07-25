from django.contrib import admin

from .models import Video, Project


# class ProjectAdmin(admin.ModelAdmin):
# 	class Meta:
# 		model = Project

admin.site.register(Project)


class VideoAdmin(admin.ModelAdmin):
	list_display = ["__unicode__", 'slug']
	fields = ['title', 'order', 'share_message', 'embed_code',
	          'active', 'slug', 'featured', 'free_preview', 'proj']
	prepopulated_fields = {
		'slug': ["title"],
	}

	class Meta:
		model = Video

admin.site.register(Video, VideoAdmin)


