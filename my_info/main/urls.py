from django.conf.urls import patterns, include, url

urlpatterns = patterns(
    'my_info.main.views',

    url(r'^$', "home", name="home"),
    url(r'^get_data/$', "get_data", name="get_data"),

    #url(r'^my_tweets/$', "my_tweets", name="my_tweets"),
    #url(r'^geocoder/$', "geocoder", name="geocoder"),
)
