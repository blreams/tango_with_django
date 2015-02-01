from django.conf.urls import patterns, url
from rango import views

urlpatterns = patterns('',
        url(r'^$', views.index, name='index'),
        url(r'^about/$', views.about, name='about'),
        url(r'^category/(?P<category_name_slug>[\w\-]+)/$', views.category, name='category'),
        url(r'^add_category/$', views.add_category, name='add_category'),
        url(r'^category/(?P<category_name_slug>[\w\-]+)/add_page/$', views.add_page, name='add_page'),
        url(r'^goto/$', views.track_url, name='goto'),

        # AJAX URLs
        url(r'^like_category/$', views.like_category, name='like_category'),
        url(r'^suggest_category/$', views.suggest_category, name='suggest_category'),

#UNUSED#        url(r'^register/$', views.register, name='register'),
#UNUSED#        url(r'^login/$', views.user_login, name='login'),
#UNUSED#        url(r'^logout/$', views.user_logout, name='logout'),
        url(r'^restricted/', views.restricted, name='restricted'),
        )

