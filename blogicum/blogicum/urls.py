from django.contrib import admin
from django.urls import include, path

from pages import views

urlpatterns = [
    path('', include('blog.urls', namespace='blog')),
    path('pages/', include('pages.urls', namespace='pages')),
    path('admin/', admin.site.urls),
    path('auth/', include('django.contrib.auth.urls')),
    path('auth/registration/', views.RegistrationPage.as_view(),
         name='registration'),
]

handler404 = 'pages.views.page_not_found'
handler500 = 'pages.views.server_error'
