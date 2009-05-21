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

    return _wrapper


class Flak(object):
    def __init__(self, **kw):
        self.data = kw

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

    def request(self, data=None, authorize=False, **kw):

        url = self.URI + '/'.join("%s:%s" % (k, self.translate_value(v)) for k, v in kw.iteritems())

        req = urllib2.Request(url, data = data)

        if authorize:
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
            elif code == 400:
                raise FlakError(url)
            else:
                raise

        try:
            response = json.load(handle)
        except ValueError,e:
            print h
            raise FlakError(h)

        return response

    @login_required
    def auth(self):
        r = self.request(type='auth', authorize=True)['status']
        if r['text'] == "OK":
            return True

    def bookmarks(self, login):
        return [Flak(**dict((str(k), v) for k, v in e.items())) for e in self.request(login=login)['entries']]

    @login_required
    def tags(self):
        return self.request(type='tags', authorize=True, login=self.login)['tags']

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
        return self.request(data=data, authorize=True, type='submit')['status']['info']


if __name__=="__main__":
    import sys

    login, password = sys.argv[1], sys.argv[2]
    print login, password
    flak = Flaker(login=login, password=password)
    print flak.auth()
    print flak.tags()
#     print
#     for f in flak.bookmarks(login="hazan"):
#         for k,v in f.data.items():
#             print "%s: %s"%(k,v)
#         print
