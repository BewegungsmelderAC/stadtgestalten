import re

import django
from django.db import models

import core
from features.contributions import models as contributions


EXCLUDE_RE = r'Content-Type: application/pgp-signature'


class FileManager(models.Manager):
    def create_from_message(self, message, attached_to):
        for attachment in message.attachments.all():
            if re.search(EXCLUDE_RE, attachment.headers):
                continue
            f = self.create(file=attachment.document)
            contributions.Contribution.objects.create(
                    container_id=attached_to.container_id,
                    container_type=attached_to.container_type,
                    contribution_id=f.id,
                    contribution_type=f.content_type,
                    author=attached_to.author,
                    attached_to=attached_to)


class File(core.models.Model):
    file = models.FileField()

    contribution = django.contrib.contenttypes.fields.GenericRelation(
            'contributions.Contribution',
            content_type_field='contribution_type',
            object_id_field='contribution_id',
            related_query_name='file')

    objects = FileManager()