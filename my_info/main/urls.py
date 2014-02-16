from django.conf.urls import patterns, url
from django.contrib.auth.views import logout
from django.views.generic import TemplateView

urlpatterns = patterns(
    'my_info.main.views',

    url(r'^$', "home", name="home"),
    url(
        r'login/$',
        TemplateView.as_view(template_name='registration/login.html'),
        name="login"
    ),
    url(r'logout/$', logout, name="logout")
)
