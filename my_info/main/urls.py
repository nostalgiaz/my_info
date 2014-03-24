from django.conf.urls import patterns, url
from django.contrib.auth.views import logout
from django.views.generic import TemplateView

urlpatterns = patterns(
    'my_info.main.views',

    url(r'^$', "home", name="home"),

    url(
        r'twitter_callback/$',
        "twitter_callback",
        name="twitter_callback"
    ),

    url(
        r'start_elaboration/$',
        "start_elaboration",
        name="start_elaboration"
    ),

    url(
        r'elaboration/(?P<elaboration_id>[0-9a-f]{5,40})/$',
        "elaboration",
        name="elaboration"
    ),

    url(
        r'get_process_status/(?P<elaboration_id>[0-9a-f]{5,40})/$',
        'get_process_status',
        name='get_process_status'
    ),

    url(
        r'show/(?P<elaboration_id>[0-9a-f]{5,40})/$',
        "show_info_page",
        name="show_info_page"
    ),

    url(
        r'show_cluster/(?P<elaboration_id>[0-9a-f]{5,40})/$',
        "show_cluster",
        name="show_cluster"
    ),

    url(
        r'show_tweets/(?P<elaboration_id>[0-9a-f]{5,40})/$',
        "show_tweets",
        name="show_tweets"
    ),

    url(
        r'login/$',
        TemplateView.as_view(template_name='registration/login.html'),
        name="login"
    ),

    url(
        r'complete_registration/$',
        TemplateView.as_view(template_name='main/complete_registration.html'),
        name="complete_registration"
    ),

    url(
        r'save_email/(?P<user_pk>\d+)/',
        "save_email",
        name="save_email"
    ),

    url(
        r'elaboration_history/(?P<user_pk>\d+)/',
        "elaboration_history",
        name="elaboration_history"
    ),

    url(
        r'logout/$',
        logout,
        {"next_page": "/login/"},
        name="logout",
    )
)
