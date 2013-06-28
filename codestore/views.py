#! -*- coding: utf-8 -*-

from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import user_passes_test
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response
from django.template import RequestContext, loader
from django.http import *
from django.utils.http import urlquote
from django.utils.html import linebreaks, escape
from django.utils.simplejson import dumps, loads
from django.views.decorators.csrf import csrf_exempt
from StringIO import StringIO
import os, sys, traceback, random

from models import *

# Load your custom modules
from django.db.models import Q

#################### Inner functions #########################
def formatExceptionInfo(maxTBlevel=5):
    cla, exc, trbk = sys.exc_info()
    excName = cla.__name__
    try:
        excArgs = exc.__dict__["args"]
    except KeyError:
        excArgs = "<no args>"
        excTb = traceback.format_tb(trbk, maxTBlevel)
    return (excName, excArgs, excTb)

def exceptionInfo(maxTBlevel=5):
    (excName, excArgs, excTb) = formatExceptionInfo(maxTBlevel)
    return str(excName) + ":" + ";".join(excArgs) + "\nStack Trace:\n" + "\n".join(excTb)

class RunObj(object):
    """ Run a piece of code in customized global context """
    def __init__(self, request, code, input_data):
        self.request = request
        self.input_data = input_data
        self.code = code

        self._out = StringIO()
        self.error = None

    def __call__(self):

        ## inner methods
        def log(*args):
            for i in range(0,len(args)):
                self._out.write(unicode(args[i]) + u" ")
            self._out.write(u"<BR>")

        def render_response(context, template = None, r = None):
            if not template:
                template = self.input_data

            if not r:
                r = self.request

            t = loader.get_template_from_string(template);
            self._out.write(t.render(RequestContext(r, context)))

        ## end of methods list

        local = locals().copy()
        local.pop('self')
        local.update({
            'request': self.request,
            'input_data': self.input_data,
        })

        try:
            self.code = self.code.replace(u'\r\n', u'\n')
            _t = compile(self.code, "", "exec")
            eval(_t, local, {})
        except Exception, e:
            self.error = e
            out = self._out
            out.write(u'\n' + unicode(e.message))
            out.write(u'\n' + exceptionInfo(5))
            if self.request.user.is_superuser:
                out.write(u'\n\nSource:\n<pre>')
                l_no = 1
                for i in self.code.split('\n'):
                    out.write(unicode(l_no).ljust(2) + u"  " + i + u'\n')
                    l_no += 1
                out.write(u'</pre>')

        return self._out.getvalue()


###############################################################

@user_passes_test(lambda u:u.is_authenticated() and u.is_superuser)
@csrf_exempt
def index(request, code_name = ''):
    ctx = {}
    code_list = CodeStore.objects.all()


    try:
        c = CodeStore.objects.get(name = code_name)
    except CodeStore.DoesNotExist:
        c = CodeStore()

    if request.POST:
        action = request.POST.get('action', 'save')

        if action == 'delete':
            if c.pk:
                c.delete()
                return HttpResponseRedirect(reverse('codestore_index'))

    ctx = {
        'c': c,
        'clist': code_list,
    }

    return render_to_response('codestore/index.html', ctx,
        RequestContext(request))

@user_passes_test(lambda u:u.is_authenticated() and u.is_superuser)
@csrf_exempt
def action(request, code_name, action):
    if not request.POST:
        return HttpResponse(dumps({"result": False}))

    try:
        c = CodeStore.objects.get(name = code_name)
    except CodeStore.DoesNotExist:
        c = CodeStore()

    ret = {
        "result": True
    }

    if action == 'save':
        c.code = request.POST['code']
        c.name = request.POST.get('name', '').strip()
        c.tag = request.POST.get('tag', '').strip()
        c.allow_anonymous = request.POST.get('aa', False) != False
        c.allow_input = request.POST.get('ai', False) != False
        c.description = request.POST.get('desc', '')
        c.show = request.POST.get('show_in_tools', False) != False
        save_data = request.POST.get('sd', False) != False
        if save_data:
            c.data = request.POST.get('data', '')
        c.save()
        if c.name != code_name:
            ret['redirect'] = reverse("codestore_load", args=[c.name])
    elif action == 'delete':
        if c.pk: c.delete()
        ret['redirect'] = reverse("codestore_index")

    return HttpResponse(dumps(ret))

@csrf_exempt
def run(request, code_name = ''):
    code_name = code_name.strip()

    if request.POST:
        data = request.POST.copy()
    else:
        data = request.GET.copy()

    try:
        if code_name:
            c = CodeStore.objects.get(name = code_name)

            if not c.allow_anonymous and not (request.user.is_authenticated() and request.user.is_superuser):
                return HttpResponseForbidden()

            code = c.code
            input_data = c.data
            desc = c.description or ''
        else:
            if not (request.user.is_authenticated() and request.user.is_superuser):
                return HttpResponseForbidden()

            c = None
            code = data.get('code', '')
            desc = ''
            input_data = ''

        input_data = data.get('data', input_data)

        runobj = RunObj(request, code, input_data)
        out = runobj()

        tmp = u"<div style='font-weight:bold;'>%s</div>" % linebreaks(desc)
        tmp2 = u"<form method='post'><input type=submit value=Refresh><br><textarea name='data' cols=50 rows=5>%s</textarea></form><br>" % input_data

        out = linebreaks(out)
        if c and c.allow_input:
            out = tmp + tmp2 + out
        else:
            out = tmp + out
        return HttpResponse(out)

    except CodeStore.DoesNotExist, e:
        if request.user.is_authenticated() and request.user.is_superuser:
            return HttpResponse(unicode(e))
        else:
            raise Http404

@user_passes_test(lambda u:u.is_authenticated() and u.is_superuser)
def tools(request, code_name = ''):
    c = CodeStore.objects.filter(show = True)
    out = ""
    if code_name:
        response = run(request, code_name)
        out = response.content

    data = {
        "codes": c,
        "out": out,
    }
    return render_to_response("codestore/tools.html", RequestContext(request, data))

