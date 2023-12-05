from django import template

register = template.Library()


@register.simple_tag(takes_context=True)
def param_replace(context, **kwargs):
    """
    Solution found on https://cheat.readthedocs.io/en/latest/django/filter.html#combining-filtering-and-pagination
    Based on
    https://stackoverflow.com/questions/22734695/next-and-before-links-for-a-django-paginated-query/22735278#22735278
    """
    query_dict = context["request"].GET.copy()
    for k, v in kwargs.items():
        query_dict[k] = v
    for k in [k for k, v in query_dict.items() if not v]:
        del query_dict[k]
    return query_dict.urlencode()
