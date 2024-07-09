from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Count
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import CommentForm, PostForm, UserForm
from .models import Category, Comment, Post, User

POSTS_LIMIT = 10


def get_post_queryset():
    return Post.objects.select_related(
        'author', 'category', 'location').filter(
        is_published=True,
        category__is_published=True,
        pub_date__date__lt=timezone.now()).annotate(
        comment_count=Count('comments')).order_by('-pub_date')


def get_page_obj(request, data_list):
    paginator = Paginator(data_list, POSTS_LIMIT)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)


def index(request):
    post_list = get_post_queryset()
    page_obj = get_page_obj(request, post_list)
    return render(request, 'blog/index.html', {'page_obj': page_obj})


def post_detail(request, pk):
    post = get_object_or_404(Post.objects.select_related(
        'author', 'category', 'location'), pk=pk)
    if (post.author != request.user
        and (post.is_published is False
             or post.category.is_published is False
             or post.pub_date > timezone.now())):
        raise Http404
    form = CommentForm()
    comments = Comment.objects.select_related(
        'author').filter(post_id=pk)
    context = {'post': post,
               'form': form,
               'comments': comments}
    return render(request, 'blog/detail.html', context)


def category_posts(request, category_slug):
    category = get_object_or_404(
        Category,
        slug=category_slug,
        is_published=True
    )
    post_list = get_post_queryset().filter(category=category)
    page_obj = get_page_obj(request, post_list)
    context = {'category': category,
               'page_obj': page_obj}
    return render(request, 'blog/category.html', context)


def profile(request, username):
    profile = get_object_or_404(
        User,
        username=username
    )
    if request.user == profile:
        post_list = Post.objects.select_related(
            'author', 'category', 'location').filter(author=profile).annotate(
                comment_count=Count('comments')).order_by('-pub_date')
    else:
        post_list = get_post_queryset().filter(author=profile)
    page_obj = get_page_obj(request, post_list)
    context = {'profile': profile,
               'page_obj': page_obj}
    return render(request, 'blog/profile.html', context)


@login_required
def edit_profile(request):
    instance = get_object_or_404(User, username=request.user)
    form = UserForm(request.POST or None, instance=instance)
    context = {'form': form}
    if form.is_valid():
        form.save()
    return render(request, 'blog/user.html', context)


def save_form(request, form):
    post = form.save(commit=False)
    post.author = request.user
    post.save()


@login_required
def create_post(request):
    form = PostForm(request.POST or None,
                    files=request.FILES or None)
    context = {'form': form}
    if form.is_valid():
        save_form(request, form)
        return redirect('blog:profile', username=request.user)
    return render(request, 'blog/create.html', context)


@login_required
def edit_post(request, pk):
    instance = get_object_or_404(Post, pk=pk)
    if request.user != instance.author:
        return redirect('blog:post_detail', pk=pk)
    form = PostForm(request.POST or None,
                    files=request.FILES or None,
                    instance=instance)
    context = {'form': form}
    if form.is_valid():
        save_form(request, form)
        return redirect('blog:post_detail', pk=pk)
    return render(request, 'blog/create.html', context)


@login_required
def delete_post(request, pk):
    instance = get_object_or_404(Post, pk=pk)
    if request.user != instance.author:
        return redirect('blog:post_detail', pk=pk)
    form = PostForm(request.POST or None,
                    files=request.FILES or None,
                    instance=instance)
    context = {'form': form}
    if request.method == 'POST':
        instance.delete()
        return redirect('blog:profile', username=request.user)
    return render(request, 'blog/create.html', context)


@login_required
def add_comment(request, pk):
    post = get_object_or_404(Post, pk=pk)
    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post_id = post.id
        comment.save()
    return redirect('blog:post_detail', pk=pk)


@login_required
def edit_comment(request, post_pk, pk):
    instance = get_object_or_404(Comment, pk=pk)
    if request.user != instance.author:
        return redirect('blog:post_detail', pk=post_pk)
    form = CommentForm(request.POST or None, instance=instance)
    context = {'form': form, 'comment': instance}
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post_id = post_pk
        comment.save()
        return redirect('blog:post_detail', pk=post_pk)
    return render(request, 'blog/comment.html', context)


@login_required
def delete_comment(request, post_pk, pk):
    instance = get_object_or_404(Comment, pk=pk)
    if request.user != instance.author:
        return redirect('blog:post_detail', pk=post_pk)
    context = {'comment': instance}
    if request.method == 'POST':
        instance.delete()
        return redirect('blog:post_detail', pk=post_pk)
    return render(request, 'blog/comment.html', context)
