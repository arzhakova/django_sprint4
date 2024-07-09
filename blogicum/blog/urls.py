from django.urls import path

from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.index, name='index'),
    path('posts/<int:pk>/', views.post_detail, name='post_detail'),
    path('posts/<int:pk>/edit/', views.edit_post, name='edit_post'),
    path('posts/<int:pk>/delete/', views.delete_post, name='delete_post'),
    path('posts/<int:pk>/comment/', views.add_comment, name='add_comment'),
    path('posts/<int:post_pk>/edit_comment/<int:pk>/',
         views.edit_comment, name='edit_comment'),
    path('posts/<int:post_pk>/delete_comment/<int:pk>/',
         views.delete_comment, name='delete_comment'),
    path('posts/create/', views.create_post, name='create_post'),
    path('category/<slug:category_slug>/', views.category_posts,
         name='category_posts'),
    path('profile/edit_profile/',
         views.edit_profile, name='edit_profile'),
    path('profile/<slug:username>/', views.profile, name='profile'),
]
