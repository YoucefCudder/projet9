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
import review.views
from LITReview import views as v

urlpatterns = [

    path('admin/', admin.site.urls),
    path('login/', auth_views.LoginView.as_view(
        template_name='user/login.html',
        redirect_authenticated_user=True
    ), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('', review.views.home, name='home'),
    path('signup/', v.signup_page, name='signup'),
    path('user/password_change/',
         auth_views.PasswordChangeView.as_view(
             template_name='user/password_change.html'),
         name="password_change"
         ),
    path('user/password_change_done/',
         auth_views.PasswordResetDoneView.as_view(
             template_name='user/password_change_done.html'
         ),
         name='password_change_done'),
    path('ticket/create_ticket/',
         review.views.create_ticket, name='create_ticket'),
    path('ticket/<int:pk>',
         review.views.ticket_detail, name='ticket_snippet'),
    path('ticket/delete/<int:pk>',
         review.views.DeleteTicketView.as_view(), name='delete_ticket'),
    path('ticket/update/<int:pk>',
         review.views.update_ticket, name='update_ticket'),
    path('review/new/',
         review.views.review_with_ticket, name='create_review'),
    path('review/<int:pk>',
         review.views.review_detail, name='review_snippet'),
    path('review/update/<int:pk>',
         review.views.update_review, name='update_review'),
    path('review/response/<int:pk>',
         review.views.review_response, name='review_response'),
    path('review/<int:pk>/delete',
         review.views.DeleteReviewView.as_view(), name='delete_review'),
    path('follow_users/', review.views.follow_users, name='follow_users'),
    path('follow_users/unfollow/<int:pk>',
         review.views.Unfollow.as_view(), name='unfollow'),
    path('profile/', review.views.profile_view, name='profile'),

]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
