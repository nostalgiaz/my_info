from ajaxutils.decorators import ajax

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from my_info.cluster.clusterify.spectralclusterify import SpectralClusterify
from my_info.cluster.clusterify.starclusterify import StarClusterify
from my_info.cluster.reader import TwitterReader


@login_required
def home(request):
    return render(request, "main/my_info.html", {
    })


@login_required
@ajax()
def cluster(request):
    tweets = TwitterReader(request.user.username)
    clusterify = SpectralClusterify(tweets, 20)
    # clusterify = StarClusterify(tweets)
    clusterify.annotate()
    return clusterify.do_cluster()
