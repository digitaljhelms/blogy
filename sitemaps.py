import datetime

from django.contrib.contenttypes.models import ContentType
from django.contrib.comments.models import Comment
from django.contrib.sitemaps import Sitemap
from blogy.models import Post

COMMENT_PRIORITY_THRESHOLD = 50.0

class BlogSitemap(Sitemap):

    def changefreq(self, obj):
        stale = obj.updated_on - datetime.datetime.now()
        if obj.updated_on > obj.published_on and \
                stale.days < 3:
            return "daily"
        return "never"

    def lastmod(self, obj):
        return obj.updated_on

    def priority(self, obj):
        pk = str(obj.pk)
        count = Comment.objects.for_model(Post).filter(object_pk=pk).count()
        return 0.5 + min(count/COMMENT_PRIORITY_THRESHOLD,0.5)

    def items(self):
        return Post.published.all()

