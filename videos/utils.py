# Get next video instance based on direction and current video instance


def get_vid_for_direction(instance, direction):
	proj = instance.proj
	video_qs = proj.video_set.all()
	if direction == "next":
		new_qs = video_qs.filter(order__gt=instance.order)
	else:
		new_qs = video_qs.filter(order__lt=instance.order).reverse()
		# new_qs = video_qs.filter(order__lt=instance.order)
	next_vid = None
	if len(new_qs) >= 1:
		try:
			next_vid = new_qs[0]
		except IndexError:
			next_vid = None
	return next_vid
