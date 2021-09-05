import uuid

from django.db import models


# Create your models here.
class BaseModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, null=False)
    updated_at = models.DateTimeField(auto_now=True, null=False)

    class Meta:
        abstract = True


class Work(BaseModel):
    title = models.CharField(max_length=32, blank=False, null=False)
    iswc = models.CharField(max_length=32, null=True, unique=True, blank=False)

    # def clean(self):
    #     from django.core.exceptions import ValidationError
    #     import pdb;pdb.set_trace()
    #     if self.title == '':
    #         raise ValidationError('Empty error message')

    def save(self, **kwargs):
        self.full_clean()
        return super(Work, self).save(**kwargs)


class Contributor(BaseModel):
    full_name = models.CharField(max_length=64, unique=True, null=False, blank=False)
    work = models.ManyToManyField(Work, related_name='contributors')






