import sys
from my_info.cluster.cache.rediscache import RedisCache

red = RedisCache()
pages = sys.argv[1:]

for topic1 in pages:
    for topic2 in pages:
        if topic1 < topic2:
            # topics = sorted([topic1, topic2])
            # topic1, topic2 = topics[0], topics[1]
            cache_key = "{}-{}:relatedness".format(topic1, topic2)
            try:

                print topic1[29:], topic2[29:], red.get(cache_key)
            except:
                print "ERRORE", cache_key

            print

