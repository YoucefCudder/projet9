"""LITReview URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls.static import static
from django.conf import settings
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path
import review
from LITReview import views
from review.views import TicketView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', auth_views.LoginView.as_view(
        template_name='user/login.html',
        redirect_authenticated_user=True
    ), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('home/', review.views.home, name='home'),
    path('signup/', views.signup_page, name='signup'),
    path('user/password_change/', auth_views.PasswordChangeView.as_view(template_name='user/password_change.html'),
         name="password_change"),
    path('user/password_change_done/',
         auth_views.PasswordResetDoneView.as_view(template_name='user/password_change_done.html'),
         name='password_change_done'),
    path('ticket/create_ticket/', review.views.create_ticket, name='create_ticket'),
    path('ticket/<int:pk>', TicketView.as_view(), name='ticket_snippet'),
    path('ticket/<int:pk>/create_review', review.views.review_response, name='create_review'),
    path('ticket/<int:pk>/delete', review.views.delete_ticket, name='delete'),
    path('ticket/<int:pk>/update', review.views.update, name='update'),
    path('review/new/', review.views.review_for_ticket, name='review_new'),
    path('feed/', review.views.feed, name='feed'),
    path('follow_users/', review.views.follow_users, name='follow_users'),
    path('profile/', review.views.profile_view, name='profile'),

]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
