from django.conf.urls import patterns, include, url

urlpatterns = patterns(
    'my_info.main.views',
    url(r'^my_tweets/$', "my_tweets", name="my_tweets"),

)
