from django.template import loader, RequestContext
from django.core.exceptions import ObjectDoesNotExist
from django.core.xheaders import populate_xheaders
from django.db.models.fields import DateTimeField
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.forms import ModelForm
import datetime
import time


def object_edit(request, year, month, day, queryset, date_field, form_class=None,
                month_format='%b', day_format='%d', object_id=None, slug=None,
                slug_field='slug', template_name=None, template_name_field=None,
                template_loader=loader, extra_context=None, context_processors=None,
                template_object_name='object', mimetype=None, allow_future=False):
    """
    Generic detail view from year/month/day/slug or year/month/day/id structure.

    Templates: ``<app_label>/<model_name>_detail.html``
    Context:
        object:
            the object to be detailed
    """
    if extra_context is None: extra_context = {}
    try:
        date = datetime.date(*time.strptime(year+month+day, '%Y'+month_format+day_format)[:3])
    except ValueError:
        raise Http404

    model = queryset.model
    now = datetime.datetime.now()

    if isinstance(model._meta.get_field(date_field), DateTimeField):
        lookup_kwargs = {'%s__range' % date_field: (datetime.datetime.combine(date, datetime.time.min), datetime.datetime.combine(date, datetime.time.max))}
    else:
        lookup_kwargs = {date_field: date}

    # Only bother to check current date if the date isn't in the past and future objects aren't requested.
    if date >= now.date() and not allow_future:
        lookup_kwargs['%s__lte' % date_field] = now
    if object_id:
        lookup_kwargs['%s__exact' % model._meta.pk.name] = object_id
    elif slug and slug_field:
        lookup_kwargs['%s__exact' % slug_field] = slug
    else:
        raise AttributeError, "Generic edit view must be called with either an object_id or a slug/slugfield"
    try:
        obj = queryset.get(**lookup_kwargs)
    except ObjectDoesNotExist:
        raise Http404, "No %s found for" % model._meta.verbose_name

    if not form_class:
        class FormClass(ModelForm):
            class Meta:
                model = queryset.model
        form_class = FormClass

    if request.method == "POST":
        form = form_class(request.POST, instance=obj)
        if form.is_valid():
            obj = form.save()
            return HttpResponseRedirect(obj.get_absolute_url())
    else:
        form = form_class(instance=obj)
    extra_context['form'] = form

    if not template_name:
        template_name = "%s/%s_edit.html" % (model._meta.app_label, model._meta.object_name.lower())
    if template_name_field:
        template_name_list = [getattr(obj, template_name_field), template_name]
        t = template_loader.select_template(template_name_list)
    else:
        t = template_loader.get_template(template_name)
    c = RequestContext(request, {
        template_object_name: obj,
    }, context_processors)
    for key, value in extra_context.items():
        if callable(value):
            c[key] = value()
        else:
            c[key] = value
    response = HttpResponse(t.render(c), mimetype=mimetype)
    populate_xheaders(request, response, model, getattr(obj, obj._meta.pk.name))
    return response
