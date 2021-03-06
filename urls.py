from django.contrib.auth.decorators import login_required
from django.views.generic import date_based, create_update
from django.views.decorators.cache import never_cache
from django.conf.urls.defaults import *
from django.conf import settings

from blogy.forms import PostEditForm
from blogy.models import Post


info_dict_edit = {
    'form_class': PostEditForm,
    }
info_dict_detail = {
    'queryset': Post.published.all(),
    'date_field': 'published_on',
    'slug_field': 'slug',
    'month_format': '%m',
    }
info_dict_preview = {
    'queryset': Post.objects.all(),
    'date_field': 'created_on',
    'slug_field': 'slug',
    'month_format': '%m',
    'template_name': 'blogy/post_preview.html',
    }
info_dict_year = {
    'queryset': Post.published.all(),
    'date_field': 'published_on',
    'make_object_list': True,
    'allow_empty': True,
    }
info_dict_month = {
    'queryset': Post.published.all(),
    'date_field': 'published_on',
    'month_format': '%m',
    'allow_empty': True,
    }
info_dict_archive = {
    'queryset': Post.published.all(),
    'date_field': 'published_on',
    'template_object_name': 'object_list',
    }


urlpatterns = patterns('blogy.views',
    url(r'^$', date_based.archive_index, info_dict_archive, name="post_list"),

    url(r'^(?P<year>\d{4})/(?P<month>\d{1,2})/(?P<day>\d{1,2})/(?P<slug>[-\w]+)/$', 
        never_cache(date_based.object_detail), info_dict_detail, name="post_detail"),

    url(r'^edit/(?P<object_id>\d+)/$', 
        login_required(never_cache(create_update.update_object)), info_dict_edit, name="post_edit"),

    url(r'^(?P<year>\d{4})/(?P<month>\d{1,2})/(?P<day>\d{1,2})/(?P<slug>[-\w]+)/preview/$', 
        login_required(never_cache(date_based.object_detail)), info_dict_preview, name="post_preview"),

    url(r'^(?P<year>\d{4})/$',
        date_based.archive_year, info_dict_year, name="year_archive"),
    url(r'^(?P<year>\d{4})/(?P<month>\d{1,2})/$', 
        date_based.archive_month, info_dict_month, name="month_archive"),
    url(r'^(?P<year>\d{4})/(?P<month>\d{1,2})/(?P<day>\d{1,2})/$', 
        never_cache(date_based.archive_day), info_dict_month, name="day_archive"),
)
