(function () {
  var $cluster = $('#cluster')
    , width = $cluster.width()
    , height = $(document).height()
    , padding = 1.5 // separation between same-color circles
    , clusterPadding = 10 // separation between different-color circles
    , maxRadius = 12
    ;

  $.get(window.my_info.urls.cluster).done(function (data) {
    var clusters = new Array(data.clusters.length)
      , clusterNodes = new Array(data.clusters.length)
      , nodes = []
      , tip
      , color
      , force
      , svg
      , circle
      ;

    $cluster.html('');

    $.each(data.clusters, function (i, el) {
      $.each(el, function (url, size) {
        var r = size * 10
          , d = {
            cluster: i,
            radius: r,
            url: url
          };

        if (!clusters[i] || (r > clusters[i].radius))
          clusters[i] = d;

        if (!clusterNodes[i])
          clusterNodes[i] = [];

        clusterNodes[i].push(d);
        nodes.push(d);
      })
    });

    tip = d3.tip()
      .attr('class', 'd3-tip')
      .html(function (d) {
        return decodeURIComponent(d.url.split("/").pop().replace(/_/g, " "));
      })
      .direction('e')
      .offset([0, 3]);

    color = d3.scale.category20().domain(d3.range(nodes.length));

    force = d3.layout.force()
      .nodes(nodes)
      .size([width, height])
      .gravity(.02)
      .charge(0)
      .on("tick", tick)
      .start();

    svg = d3.select("#cluster").append("svg")
      .attr("width", width)
      .attr("height", height)
      .call(tip);

    circle = svg.selectAll("circle")
      .data(nodes)
      .enter().append("circle")
      .attr("r", function (d) {
        return d.radius;
      })
      .attr("fill", function (d) {
        return color(d.cluster);
      })
      .attr('data-topic', function (d) {
        return d.url.split('/').pop();
      })
      .on('mouseover', tip.show)
      .on('mouseout', tip.hide)
      .on('click', showTweets)
      .call(force.drag);

    function tick(e) {
      circle
        .each(cluster(10 * e.alpha * e.alpha))
        .each(collide(.5))
        .attr("cx", function (d) {
          return d.x;
        })
        .attr("cy", function (d) {
          return d.y;
        });
    }

    function cluster(alpha) {  // Move d to be adjacent to the cluster node.
      return function (d) {
        var cluster = clusters[d.cluster]
          , x, y, l, r;

        if (cluster === d) return;
        x = d.x - cluster.x;
        y = d.y - cluster.y;
        l = Math.sqrt(x * x + y * y);
        r = d.radius + cluster.radius;

        if (l != r) {
          l = (l - r) / l * alpha;
          d.x -= x *= l;
          d.y -= y *= l;
          cluster.x += x;
          cluster.y += y;
        }
      };
    }

    function collide(alpha) {  // Resolves collisions between d and all other circles.
      var quadtree = d3.geom.quadtree(nodes);
      var r, nx1, nx2, ny1, ny2;
      return function (d) {
        r = d.radius + maxRadius + Math.max(padding, clusterPadding);
        nx1 = d.x - r;
        nx2 = d.x + r;
        ny1 = d.y - r;
        ny2 = d.y + r;

        quadtree.visit(function (quad, x1, y1, x2, y2) {
          var x, y, l, r;
          if (quad.point && (quad.point !== d)) {
            x = d.x - quad.point.x;
            y = d.y - quad.point.y;
            l = Math.sqrt(x * x + y * y);
            r = d.radius + quad.point.radius + (d.cluster === quad.point.cluster ? padding : clusterPadding);

            if (l < r) {
              l = (l - r) / l * alpha;
              d.x -= x *= l;
              d.y -= y *= l;
              quad.point.x += x;
              quad.point.y += y;
            }
          }
          return x1 > nx2 || x2 < nx1 || y1 > ny2 || y2 < ny1;
        });
      };
    }

    function toggleOverlay() {
      var container = document.querySelector('div.tweet-and-cluster')
        , overlay = document.querySelector('div.overlay')
        , transEndEventNames = {
          'WebkitTransition': 'webkitTransitionEnd',
          'MozTransition': 'transitionend',
          'OTransition': 'oTransitionEnd',
          'msTransition': 'MSTransitionEnd',
          'transition': 'transitionend'
        }
        , transEndEventName = transEndEventNames[ Modernizr.prefixed('transition') ]
        , support = { transitions: Modernizr.csstransitions };

      if (classie.has(overlay, 'open')) {
        classie.remove(overlay, 'open');
        classie.remove(container, 'overlay-open');
        classie.add(overlay, 'close');

        var onEndTransitionFn = function (ev) {
          if (support.transitions) {
            if (ev.propertyName !== 'visibility') return;
            this.removeEventListener(transEndEventName, onEndTransitionFn);
          }
          classie.remove(overlay, 'close');
        };

        if (support.transitions)
          overlay.addEventListener(transEndEventName, onEndTransitionFn);
        else onEndTransitionFn();
      }
      else if (!classie.has(overlay, 'close')) {
        classie.add(overlay, 'open');
        classie.add(container, 'overlay-open');
      }
    }

    function hexToRgb(hex) {
      var color = parseInt(hex.slice(1), 16)
        , r = (color >> 16) & 255
        , g = (color >> 8) & 255
        , b = color & 255;
      return r + "," + g + "," + b;
    }

    function showTweets(d) {
      var cluster = clusterNodes[d.cluster]
        , topics = [];

      for (var i in cluster)
        topics.push(cluster[i].url);

      $.get(window.my_info.urls.tweets, {'topics': JSON.stringify(topics)}).done(function (data) {
        var tmplTweets = $("#tweets-template").html()
          , tmplTweet = '<%= prev %><%= current %><%= next %>'
          , tmplCurrent = '<span class="annotated-entity"><%= spot %></span>'
          , tweets = [];

        $.each(data, function (i, ell) {
          var el = ell[0]
            , tweet = {
              'url': el.url,
              'text': el.text,
              'user': el.user
            }
            , text = el.text
            , sortedList = el.annotations.sort(function (a, b) {
              return a['start'] - b['start']
            })
            , offset = 0
            , current
            , start
            , end
            , item;

          for (var j in sortedList) {
            item = sortedList[j];
            start = item['start'];
            end = item['end'];
            current = _.template(tmplCurrent, {
              'spot': item['spot']
            });

            text = _.template(tmplTweet, {
              'prev': text.substr(0, start + offset),
              'current': current,
              'next': text.substr(end + offset)
            });
            offset += current.length - (end - start);
          }

          tweet['text'] = text;
          tweets.push(tweet);
        });

        $('#tweets').html(_.template(tmplTweets, {'tweets': tweets}));
        toggleOverlay();
        $('.overlay').css('background', "rgba(" + hexToRgb(color(d.cluster)) + ", .9)");
        $('.overlay-close').on('click', toggleOverlay);
      });
    }
  });
})();