from django.conf import settings
from django.core.paginator import Paginator
from django.db.models import Count
from django.utils import timezone

from .models import Post


def get_post_queryset(flag1=False, flag2=False):
    query_set = Post.objects.select_related('author', 'category', 'location')
    if flag1:
        query_set = query_set.filter(is_published=True,
                                     category__is_published=True,
                                     pub_date__date__lt=timezone.now())
    if flag2:
        query_set = query_set.annotate(comment_count=Count('comments')
                                       ).order_by('-pub_date')
    return query_set


def get_page_obj(request, data_list):
    paginator = Paginator(data_list, settings.POSTS_LIMIT)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)
