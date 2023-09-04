from django.conf import settings


def group_names(request):
    return {"GROUP_NAMES": settings.GROUP_NAMES}
