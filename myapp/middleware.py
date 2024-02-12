from django.contrib.auth import get_user_model
from django.utils import timezone


class UpdateLastActivityMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        if request.user.is_authenticated:
            user_model = get_user_model()
            user = user_model.objects.get(pk=request.user.pk)
            user.last_activity_time = timezone.now()
            user.save(update_fields=['last_activity_time'])
        return response
