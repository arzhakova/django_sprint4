from django.db.models import Count
from django.utils import timezone

from .models import Post


def get_post_queryset(filters=False, annotation=False,
                      model_manager=Post.objects):
    query_set = model_manager.select_related('author', 'category', 'location')
    if filters:
        query_set = query_set.filter(is_published=True,
                                     category__is_published=True,
                                     pub_date__date__lt=timezone.now())
    if annotation:
        query_set = query_set.annotate(comment_count=Count('comments')
                                       ).order_by('-pub_date')
    return query_set
