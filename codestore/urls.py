from django.conf.urls.defaults import *

import views

urlpatterns = patterns('',
     (r'^$', views.index, {}, 'codestore_index'),
     (r'^code/(?P<code_name>.*)/$', views.index, {}, 'codestore_load'),
     (r'^save/(?P<code_name>.*)$', views.action, {'action':'save'}, 'codestore_save'),
     (r'^delete/(?P<code_name>.*)$', views.action, {'action':'delete'}, 'codestore_delete'),
     (r'^run/(?P<code_name>.*)$', views.run, {}, 'codestore_run'),
     (r'^run/$', views.run, {}, 'codestore_run'),

     (r'^tools/(?P<code_name>.*)/$', views.tools, {}, "codestore_toolsload"),
     (r'^tools/$', views.tools, {}, "codestore_tools"),
)