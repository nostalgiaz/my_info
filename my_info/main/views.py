from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from my_info.cluster.clusterify.starclusterify import StarClusterify
from my_info.cluster.reader import TwitterReader


@login_required
def home(request):
    tweets = TwitterReader(request.user.username)
    clusterify = StarClusterify(tweets)
    clusterify.annotate()
    twitter_cluster_data = clusterify.do_cluster()

    return render(request, "main/my_info.html", {
        'twitter_cluster_data': twitter_cluster_data
    })
