Django-Codestore
----------------

Codestore is a pluggable django app that enables you to edit and run simple python scripts online. This can be useful when you want

* to quickly implement some helper snippets and dont wanna change your repositories.
* to debug a runtime problem
* to examine or modify runtime data
* to implement a quick web page with runtime data and show someone

Features
--------

* Syntax highlight (powered by codemirror)
* Run online in the context of your django backend
* Save scripts to db
* Expose scripts via a Tools page to anonymous users
* Optionally take user input before running
* Optionally render html as result

Usage
-----

1. add `codestore` into `settings.installed_apps`
2. include `codestore.urls` into your `urlpatterns`
3. `{% url codestore_index %}` for editor url. `{% url codestore_tools %` for tools page url. Put them anywhere you like.

Scripts API
--

In addition to all the python stuff you know, there are several special variables and functions you should know.

**input_data**

This is the input data from the "input textarea"

**request**

This is the http request.

**log(*args)**

This is the primary output function. `print` won't work.

**render_response(context, template = None, request = None)**

This renders the response as html instead of plain text. `context` is a dict. `template` will be copied from `input_data` if None. `request` will be set as the current request if None.