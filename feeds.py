from django.contrib.comments.feeds import LatestCommentFeed
from django.contrib.comments.models import Comment
from django.contrib.syndication.feeds import Feed
from django.utils.feedgenerator import Atom1Feed
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse

from blogy.models import Post

BLOGY_LATEST_POSTS_COUNT = 25
BLOGY_LATEST_COMMENTS_COUNT = 25
try:
    from django.conf.settings import BLOGY_LATEST_POSTS_COUNT
    from django.conf.settings import BLOGY_LATEST_COMMENTS_COUNT
except:
    pass

class LatestPostsBaseFeed(Feed):

    link = reverse('post_list',urlconf='blogy.urls')

    def title(self):
        if not hasattr(self, '_site'):
            self._site = Site.objects.get_current()
        return u"%s posts" % self._site.name

    def description(self):
        if not hasattr(self, '_site'):
            self._site = Site.objects.get_current()
        return u"Latest posts on %s" % self._site.name

    def items(self):
        return Post.published.all()[:BLOGY_LATEST_POSTS_COUNT]

    def item_pubdate(self, item):
        return item.published_on

class LatestPostsFeed(LatestPostsBaseFeed):
    feed_type = Atom1Feed
    subtitle = LatestPostsBaseFeed.description

class LatestCommentsBaseFeed(LatestCommentFeed):

    def items(self):
        return Comment.objects.for_model(Post)[:BLOGY_LATEST_COMMENTS_COUNT]

    def item_pubdate(self, item):
        return item.submit_date

class LatestCommentsFeed(LatestCommentsBaseFeed):
    feed_type = Atom1Feed
    subtitle = LatestCommentFeed.description
