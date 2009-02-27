from django.db import models


class PublicPostManager(models.Manager):
    def get_query_set(self):
        qs = super(PublicPostManager, self).get_query_set()
        return qs.filter(is_draft=False)
