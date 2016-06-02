from django.conf.urls import url

from . import views

urlpatterns = [
    url('^login/$', views.LoginView.as_view(), name='login'),
    url('^logout/$', views.logout_view, name='logout'),

    url('^create_user/$', views.create_user_view, name='create-user'),

    url('^session/new/$', views.new_session, name='new-session'),
    url('^session/(?P<pk>[0-9]+)/edit/$', views.edit_session, name='edit-session'),
    url('^session/(?P<pk>[0-9]+)/resupply/$', views.resupply_session, name='resupply-session'),
    url('^session/(?P<pk>[0-9]+)/end/$', views.end_session, name='end-session'),
    url('^session/$', views.SessionListView.as_view(), name='session-list'),

    url('^$', views.main_view, name='main'),
]
