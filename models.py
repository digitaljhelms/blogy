from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.utils.translation import ugettext_lazy as _
from django.utils.html import strip_tags
from django.contrib.contenttypes import generic
from django.core.urlresolvers import reverse

from tagging.models import Tag
from tagging.fields import TagField
from tagging.utils import parse_tag_input
#from pingback import Pingback, create_ping_func
#from pingback import ping_external_links, ping_directories
from template_utils.markup import formatter
from jellyroll.models import Item
from blogy.managers import PublicPostManager

import datetime
import markdown
#import xmlrpc


class Series(models.Model):
    """

    """
    title = models.CharField(_(u'title'), max_length=255)
    slug = models.SlugField(_(u'slug'), max_length=32, unique=True)
    summary = models.TextField(_(u'summary'), blank=True)

    created_on = models.DateTimeField(_(u'created on'), default=datetime.datetime.now, editable=False)
    updated_on = models.DateTimeField(_(u'updated on'), default=None, editable=False, null=True)

    class Meta:
        ordering = ('-updated_on', )
        verbose_name_plural = 'Series'

    def __unicode__(self):
        return u'%s' % self.title

class Post(models.Model):
    """
    
    """
    title = models.CharField(_(u'title'), max_length=128)
    slug = models.SlugField(_(u'slug'), max_length=32, blank=True, unique_for_date="published_on")
    summary = models.TextField(_(u'summary'), blank=True)
    tags = TagField()

    raw_text = models.TextField(_(u'content'))
    rendered_text = models.TextField(_(u'rendered text'), editable=False)

    created_on = models.DateTimeField(_(u'created on'), default=datetime.datetime.now, editable=False)
    updated_on = models.DateTimeField(_(u'updated on'), default=None, editable=False, null=True)
    published_on = models.DateTimeField(_(u'published on'), default=None, editable=False, null=True)

    is_draft = models.BooleanField(verbose_name=_(u'draft'), default=False)
    enable_comments = models.BooleanField(_(u'comments enabled'),default=False)

    author = models.ForeignKey(User, related_name='user_posts')
    series = models.ForeignKey(Series, related_name='posts', blank=True, null=True)
    #pingbacks = generic.GenericRelation(Pingback)

    objects = models.Manager()
    published = PublicPostManager()

    class Meta:
        ordering = ['-published_on']
        get_latest_by = '-published_on'
        unique_together = ('slug', 'published_on')

    def __unicode__(self):
        return self.title

	@models.permalink
    def get_absolute_url(self):
        return ('post_detail', (), {
            'slug':self.slug,
            'year':self.published_on.year,
            'month':self.published_on.strftime('%m'),
            'day':self.published_on.strftime('%d'),
            })

    def _get_url(self):
        """
        The implementation of this method is a frustrating reality. It appears
        that because by default ``URLField``s have ``verify_exists=True``, 
        ``jellyroll.Item``'s autodetection of a url attribute on the followed model
        will fail if this property is not expressed as protocol://domain/path.

        """
        site = Site.objects.get_current()
        site_prefix = site.domain
        if not site.domain.startswith('http'):
            site_prefix = "http://%s"%site.domain
        return "%s%s"%(site_prefix,self.get_absolute_url())
    url = property(_get_url)

    def save(self, *args, **kwargs):
        current_timestamp = datetime.datetime.now()
        self.rendered_text = formatter(self.raw_text)

        if not self.pk and not settings.DEBUG:
            from django.contrib.sitemaps import ping_google
            try:
                ping_google()
            except:
                pass

        if not self.is_draft:
            if not self.published_on:
                self.published_on = current_timestamp
            self.updated_on = current_timestamp

        super(Post, self).save(*args, **kwargs)

    def _get_draft(self):
        return not self.is_draft
    jellyrollable = property(_get_draft)

    def _get_timestamp(self):
        return self.published_on
    timestamp = property(_get_timestamp)

Item.objects.follow_model(Post)


# Pingback and directory ping handling
#def pingback_blog_handler(year, month, day, slug, **kwargs):
#    from datetime import time, date, datetime
#    from time import strptime
#    d = date(*strptime(year + month + day, '%Y%m%d')[:3])
#    r = (datetime.combine(d, time.min), datetime.combine(d, time.max))
#    return Post.objects.filter(published_on__range=r).get(slug=slug)

#ping_details = {'post_detail': pingback_blog_handler}
#xmlrpc.dispatcher.register_function(create_ping_func(**ping_details), 'pingback.ping')

#ping_links = ping_external_links(content_attr='rendered_text', url_attr='get_absolute_url',
#                                 filtr=lambda x: not x.is_draft)
#ping_dirs = ping_directories(content_attr='rendered_text', url_attr='get_absolute_url',
#                             filtr=lambda x: not x.is_draft)

#models.signals.post_save.connect(ping_links, sender=Post)
#models.signals.post_save.connect(ping_dirs, sender=Post)
