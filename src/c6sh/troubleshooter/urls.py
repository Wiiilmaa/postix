from django.conf.urls import url

from . import views

urlpatterns = [
    url('^login/$', views.LoginView.as_view(), name='login'),
    url('^logout/$', views.logout_view, name='logout'),

    url('^constraints/(?P<pk>[0-9]+)/$', views.ListConstraintDetailView.as_view(), name='constraint-detail'),
    url('^constraints/$', views.ListConstraintListView.as_view(), name='constraint-list'),

    url('^transactions/(?P<pk>[0-9]+)/reprint/$', views.transaction_reprint, name='transaction-reprint'),
    url('^transactions/(?P<pk>[0-9]+)/invoice/$', views.transaction_invoice, name='transaction-invoice'),
    url('^transactions/(?P<pk>[0-9]+)/cancel-position/$', views.transaction_position_cancel, name='transaction-position-cancel'),
    url('^transactions/(?P<pk>[0-9]+)/cancel/$', views.transaction_cancel, name='transaction-cancel'),
    url('^transactions/(?P<pk>[0-9]+)/$', views.TransactionDetailView.as_view(), name='transaction-detail'),
    url('^transactions/$', views.TransactionListView.as_view(), name='transaction-list'),

    url('^$', views.main_view, name='main'),
]
