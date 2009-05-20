# -*- coding: utf-8 -*-

import urllib2
from urllib import urlencode
try:
    import json
except ImportError:
    import simplejson as json
import base64

class FlakError(Exception):
    "Basic Flaker error."
    pass

class FlakAuthorizationError(FlakError):
    pass

class FlakDuplicateMessageError(FlakError):
    pass

class FlakConfigurationError(FlakError):
    pass

def login_required(fun):
    def _wrapper(self, *a, **kw):
        if not self.login and self.password:
            raise FlakConfigurationError("You must provide some credentials in order to perform this action.")
        else:
            return fun(self, *a, **kw)

class Flaker(object):

    URI = 'http://api.flaker.pl/api/'

    def __init__(self, login=None, password=None):
        if login and password:
            self.login, self.password = login, password
        elif password:
            raise FlakConfigurationError("If you provide a password you should also provide a login")
        else:
            self.login = self.password = None

    def translate_value(self, val):
        if isinstance(val, bool):
            return "true" if val else "false"
        else:
            return val

    @login_required
    def submit(self, text, link=None, photo=None):
        "Submit a status to Flaker."
        data = {'text': text}
        if link:
            data['link'] = link
        if photo:
            # if it's not a file assume it is a URL to one.
            try:
                data['photo'] = open(photo)
            except IOError:
                data['link'] = photo

        req = urllib2.Request(self.prepare_url(type='submit'),
                              data = data)

        authheader = "Basic %s" % base64.encodestring("%s:%s"% (login, password))[:-1]
        req.add_header("Authorization", authheader)


        try:
            handle = urllib2.urlopen(req)
        except urllib2.HTTPError, e:
            code = e.getcode()
            if code == 409:
                raise FlakDuplicateMessageError
            elif code == 401:
                raise FlakAuthorizationError

        try:
            response = json.load(handle)['status']
        except ValueError,e:
            raise FlakError(e)
        if int(response['code']) == 200 and response['text'] == 'OK':
            return response['info']
        else:
            raise FlakError(response)


    def prepare_url(self, **kw):
        return self.URI + '/'.join("%s:%s" % (k, v) for k, self.translate_value(v) in kw.iteritems())

