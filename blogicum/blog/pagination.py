from django.conf import settings
from django.core.paginator import Paginator


def get_page_obj(request, data_list):
    paginator = Paginator(data_list, settings.POSTS_LIMIT)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)
