from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    # path('', views.BlogListView.as_view(), name='home'),
    # path('', views.BlogListView.as_view(), name='home'),
    # path('login', views.login.as_view(), name='login'),
    path('login/', views.user_login, name='login'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('register/', views.register, name='register'),
    path('adduser/', views.adduser, name='adduser'),
    path('logout/', views.user_logout, name='logout'),
    path('profile/<int:uid>/', views.profile, name='profile'),
    path('edituser/<int:uid>/', views.edituser, name='edituser'),
    path('userlist/', views.userlist, name='userlist'),
    path('createassessment/', views.createassessment, name='createassessment'),
    path('viewassessment/', views.viewassessment, name='viewassessment'),
    path('compareassessment/', views.compareassessment, name='compareassessment'),

    path('country/', views.country, name='country'),
    path('industry/', views.industry, name='industry'),
    path('editindustry/<int:cid>/', views.editindustry, name='editindustry'),
    path('changeindustryaction/', views.changeindustryaction,
         name='changeindustryaction'),

    path('client/', views.client, name='client'),
    path('editclient/<int:cid>/', views.editclient, name='editclient'),
    path('changeclientaction/', views.changeclientaction,
         name='changeclientaction'),

    path('editcountry/<int:cid>/', views.editcountry, name='editcountry'),
    path('changecountryaction/', views.changecountryaction,
         name='changecountryaction'),
    path('getclients/<int:uid>/', views.get_clients, name='getclients'),
    path('getassessment/<int:uid>/', views.get_assessment, name='getassessment'),


    # path('post/<int:pk>/', views.BlogDetailView.as_view(), name='post_detail'),

]
