from django.conf.urls import url

from . import views

urlpatterns = [
    url('^login/$', views.LoginView.as_view(), name='login'),
    url('^logout/$', views.logout_view, name='logout'),

    url('^preorders/$', views.PreorderListView.as_view(), name='preorder-list'),
    url('^preorders/(?P<pk>[0-9]+)/$', views.PreorderDetailView.as_view(), name='preorder-detail'),

    url('^constraints/(?P<pk>[0-9]+)/$', views.ListConstraintDetailView.as_view(), name='constraint-detail'),
    url('^constraints/$', views.ListConstraintListView.as_view(), name='constraint-list'),

    url('^transactions/(?P<pk>[0-9]+)/reprint/$', views.transaction_reprint, name='transaction-reprint'),
    url('^transactions/(?P<pk>[0-9]+)/invoice/$', views.transaction_invoice, name='transaction-invoice'),
    url('^transactions/(?P<pk>[0-9]+)/$', views.TransactionDetailView.as_view(), name='transaction-detail'),
    url('^transactions/$', views.TransactionListView.as_view(), name='transaction-list'),

    url('^session/(?P<pk>[0-9]+)/resupply/$', views.confirm_resupply, name='confirm-resupply'),

    url('^$', views.main_view, name='main'),
]
