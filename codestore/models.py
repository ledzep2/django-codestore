from django.db import models
from django.contrib.admin import site, ModelAdmin
from django.utils.translation import ugettext as _

# Create your models here.
class CodeStore(models.Model):
    name = models.CharField(_("Name"), max_length=40, blank=False, default="", unique=True)
    tag = models.CharField(_("Tag"), max_length=40, blank=True, default="")
    code = models.TextField(_("Code"), default = '', blank = False, null = False)
    data = models.TextField(_("Data"), default = '', blank = False, null = False)
    allow_anonymous = models.BooleanField(_("Allow Anonymous"), blank=False, default = False)
    allow_input = models.BooleanField(_("Allow input"), blank=False, default = False)
    description = models.TextField(_("Description"), blank=True, default='')
    show = models.BooleanField(_("Show in admin"), blank=False, default = False)


class CodeStoreAdmin(ModelAdmin):
    list_display = ('name', 'show', 'allow_anonymous', 'allow_input', 'description')

site.register(CodeStore, CodeStoreAdmin)