from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import CommentForm, PostForm, UserForm
from .models import Category, Comment, Post, User
from .tools import get_page_obj, get_post_queryset


def index(request):
    post_list = get_post_queryset(True, True)
    page_obj = get_page_obj(request, post_list)
    return render(request, 'blog/index.html', {'page_obj': page_obj})


def post_detail(request, post_id):
    post = get_object_or_404(get_post_queryset(), pk=post_id)
    if (post.author != request.user
        and (post.is_published is False
             or post.category.is_published is False
             or post.pub_date > timezone.now())):
        raise Http404
    form = CommentForm()
    comments = Comment.objects.select_related(
        'author').filter(post_id=post_id)
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
    post_list = get_post_queryset(True, True).filter(category=category)
    page_obj = get_page_obj(request, post_list)
    context = {'category': category,
               'page_obj': page_obj}
    return render(request, 'blog/category.html', context)


def profile(request, username):
    profile = get_object_or_404(
        User,
        username=username
    )
    flag1 = False if request.user == profile else True
    post_list = get_post_queryset(flag1, True).filter(author=profile)
    page_obj = get_page_obj(request, post_list)
    context = {'profile': profile,
               'page_obj': page_obj}
    return render(request, 'blog/profile.html', context)


@login_required
def edit_profile(request):
    instance = request.user
    form = UserForm(request.POST or None, instance=instance)
    context = {'form': form}
    if form.is_valid():
        form.save()
        return redirect('blog:profile', username=request.user)
    return render(request, 'blog/user.html', context)


@login_required
def create_post(request):
    form = PostForm(request.POST or None,
                    files=request.FILES or None)
    context = {'form': form}
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('blog:profile', username=request.user)
    return render(request, 'blog/create.html', context)


@login_required
def edit_delete_post(request, post_id):
    instance = get_object_or_404(Post, pk=post_id)
    if request.user != instance.author:
        return redirect('blog:post_detail', post_id=post_id)
    form = PostForm(request.POST or None,
                    files=request.FILES or None,
                    instance=instance)
    context = {'form': form}
    if form.is_valid():
        form.save()
        return redirect('blog:post_detail', post_id=post_id)
    if request.method == 'POST':
        instance.delete()
        return redirect('blog:profile', username=request.user)
    return render(request, 'blog/create.html', context)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post_id = post.id
        comment.save()
    return redirect('blog:post_detail', post_id=post_id)


@login_required
def edit_comment(request, post_id, comment_id):
    instance = get_object_or_404(Comment, pk=comment_id, post_id=post_id)
    if request.user != instance.author:
        return redirect('blog:post_detail', post_id=post_id)
    form = CommentForm(request.POST or None, instance=instance)
    context = {'form': form, 'comment': instance}
    if form.is_valid():
        form.save()
        return redirect('blog:post_detail', post_id=post_id)
    return render(request, 'blog/comment.html', context)


@login_required
def delete_comment(request, post_id, comment_id):
    instance = get_object_or_404(Comment, pk=comment_id, post_id=post_id)
    if request.user != instance.author:
        return redirect('blog:post_detail', post_id=post_id)
    context = {'comment': instance}
    if request.method == 'POST':
        instance.delete()
        return redirect('blog:post_detail', post_id=post_id)
    return render(request, 'blog/comment.html', context)
