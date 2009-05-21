# -*- coding: utf-8 -*-
"""
    >>> flak = Flaker()

    >>> flak.show(9)  # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
        Flak(...)

    >>> flak.query(tag="python", limit=1, sort='asc') # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
        [Flak(...)]

    >>> flak.friends(login="szopa")  # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
    ([Flak(...), ...], [FlakUser(...), ...])

    >>> flak.submit(text="The best blog in the world ;-)", link="http://gryziemy.net")
    Traceback (most recent call last):
      File "/Library/Frameworks/Python.framework/Versions/2.6/lib/python2.6/doctest.py", line 1231, in __run
        compileflags, 1) in test.globs
      File "<doctest __main__[4]>", line 1, in <module>
        flak.submit(text="The best blog in the world ;-)", link="http://gryziemy.net")
      File "__init__.py", line 81, in _wrapper
        raise FlakConfigurationError("You must provide some credentials in order to perform this action.")
    FlakConfigurationError: You must provide some credentials in order to perform this action.

    >>> flak.auth() # doctest: +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
      File "<ipython console>", line 1, in <module>
      File "flaker/__init__.py", line 81, in _wrapper
        raise FlakConfigurationError("You must provide some credentials in order to perform this action.")
    FlakConfigurationError: You must provide some credentials in order to perform this action.

    >>> flak.authorize('flakotest', '__XXX__') # doctest: +SKIP

    >>> flak.auth() # doctest: +SKIP
    True

    >>> flak.submit(text="The best blog in the world ;-)", link="http://gryziemy.net") # doctest: +SKIP
    u'http://flaker.pl/f/1707491'

    >>> flak.submit(text="The best blog in the world", link="http://gryziemy.net") # doctest: +SKIP, +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
      File "/Library/Frameworks/Python.framework/Versions/2.6/lib/python2.6/doctest.py", line 1231, in __run
        compileflags, 1) in test.globs
      File "<doctest __main__[7]>", line 1, in <module>
        flak.submit(text="The best blog in the world", link="http://gryziemy.net") # doctest: +SKIP
      File "__init__.py", line 66, in _wrapper
        return fun(self, *a, **kw)
      File "__init__.py", line 308, in submit
        return self.request(data=data, authorize=True, type='submit')['status']['info']
      File "__init__.py", line 183, in request
        raise FlakDuplicateMessageError
    FlakDuplicateMessageError

    >>> flaker.query(tag="python", from_=1) # doctest: +SKIP, +IGNORE_EXCEPTION_DETAIL
    [Flak(...), ...]

"""

import urllib2
from urllib import urlencode
from datetime import datetime
try:
    import json
except ImportError:
    import simplejson as json
import base64



DEBUG=False

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
        if not (self.login and self.password):
            raise FlakConfigurationError("You must provide some credentials in order to perform this action.")
        else:
            return fun(self, *a, **kw)

    return _wrapper

def flak_decoding(fun):
    def wrapper(self, *a, **kw):
        res = fun(self, *a, **kw)
        if 'friends' in res:
            return [self.flak_class(**e) for e in res['entries']], [self.flakuser_class(**e) for e in res['friends']]
        else:
            return [self.flak_class(**e) for e in res['entries']]
    return wrapper

class FlakUser(object):
    def __init__(self, login=None, url=None, avatar=None, sex=None, action=None):
        self.login = login
        self.url = url
        self.avatar = avatar
        self.sex = sex # is this used anywhere?
        self.action = action

    def __eq__(self, other):
        return self.login == other.login and self.url == other.url

    def __repr__(self):
        return "FlakUser(login=%r, url=%r, avatar=%r, sex=%r)" % (self.login, self.url, self.avatar, self.sex)

class Flak(object):
    flakuser_class = FlakUser
    def __init__(self,
                 permalink=None,
                 time=None,
                 timestamp=None,
                 comments=None,
                 source=None,
                 link=None,
                 video=None,
                 photo=None,
                 user=None,
                 text=None,
                 has_photo=None,
                 data=None,
                 id=None,
                 **kw):
        self.permalink = permalink
        self.video = video
        self.comments = comments
        self.source = source
        self.link = link
        self.user = user if isinstance(user, FlakUser) else self.flakuser_class(**user)



        self.text = text
        self.photo = photo
        self.data = data
        self.id = id

        # kludge, we are loosing tz information. note that datetime is
        # in kw, not in normal args, because we don't want to shadow
        # datetime
        if isinstance(kw['datetime'], datetime):
            self.datetime = kw['datetime']
        else:
            self.datetime = datetime.fromtimestamp(float(timestamp))
    def __str__(self):
        return ("%s@%s: %s" % (self.user.login, self.datetime, self.text)).encode('utf-8')

    def __repr__(self):
        return "Flak(permalink=%r, datetime=%r, comments=%r, source=%r, link=%r, video=%r, photo=%r, user=%r, text=%r, data=%r, id=%r)" % \
            (self.permalink, self.datetime, self.comments,
             self.source, self.link, self.video,
             self.photo, self.user, self.text, self.data, self.id)



class Flaker(object):

    URI = 'http://api.flaker.pl/api/'
    flak_class = Flak
    flakuser_class = FlakUser


    def __init__(self, login=None, password=None):
        if login and password:
            self.login, self.password = login, password
        elif password:
            raise FlakConfigurationError("If you provide a password you should also provide a login")
        else:
            self.login = self.password = None

    def authorize(self, login, password):
        self.login, self.password = login, password

    def translate_value(self, val):
        if isinstance(val, bool):
            return "true" if val else "false"
        else:
            return val

    def request(self, data=None, authorize=False, **kw):

        url = self.URI + '/'.join("%s:%s" % (k, self.translate_value(v)) for k, v in kw.iteritems())
        if DEBUG:
            print url
        if data:
            data = urlencode(data)
        req = urllib2.Request(url, data = data)

        if authorize:
            authheader = "Basic %s" % base64.encodestring("%s:%s"% (self.login, self.password))[:-1]
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
            if DEBUG:
                h = handle.read()
                response = json.loads(h, object_hook=lambda d: dict((str(k), v) for k, v in d.iteritems()))
            else:
                response = json.load(handle, object_hook=lambda d: dict((str(k), v) for k, v in d.iteritems()))
                h = None
        except ValueError,e:
            if DEBUG:
                raise FlakError(h)
            else:
                raise FlakError

        return response

    @login_required
    def auth(self):
        r = self.request(type='auth', authorize=True)['status']
        if r['text'] == "OK":
            return True

    @flak_decoding
    def bookmarks(self, login):
        return self.request(login=login)

    @login_required
    def tags(self):
        return self.request(type='tags', authorize=True, login=self.login)['tags']

    def _bookmark(self, entry_id, bookmark):
        action = 'set' if bookmark else 'unset'
        r = self.request(type="bookmark", action=action, entry_id=entry_id, authorize=True)
        if r['status']['text'] == 'OK':
            return True
        else:
            raise FlakError(r)

    @login_required
    def bookmark(self, entry_id):
        return self._bookmark(entry_id, True)

    @login_required
    def unbookmark(self, entry_id):
        return self._bookmark(entry_id, False)


    def show(self, entry_id):
        return self.flak_class(**self.request(type='show', entry_id=entry_id)['entries'][0])

    def get_messages(self,
                     tag=None,
                     avatars='small',
                     limit=20,
                     from_=None,
                     start=None,
                     since=None,
                     sort='desc',
                     comments=False,
                     **kw):
        if tag:
            if tag == True:
                tag = 'all'
            kw['tag'] = tag
        kw['avatars'] = avatars
        kw['limit'] = limit
        if from_:
            kw['from'] = from_
        if start:
            kw['start'] = start
        if since:
            kw['since'] = since
        kw['sort'] = sort
        kw['comments'] = comments
        if DEBUG:
            print kw
        return self.request(**kw)

    @flak_decoding
    def friends(self, login):
        """Get all the friends of `login`.

        """
        return self.request(type='friends', login=login)

    @flak_decoding
    def query(self,
              user=None,
              site=None,
              source=None,
              **kw):
        if len([o for o in (user, site, source) if o]) > 1:
            raise FlakConfigurationError("You may provide at most one of `user`, `site` and `source`.")
        if user:
            kw['type'] = 'user'
            kw['login'] = user
        elif site:
            kw['type'] = 'site'
            kw['site'] = site
        elif source:
            kw['type'] = 'source'
            kw['source'] = source
        else:
            kw['type'] = 'flakosfera'
        return self.get_messages(**kw)

    @login_required
    def submit(self, text=None, link=None, photo=None):
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

if __name__ == "__main__":
    import doctest
    doctest.testmod()

# if __name__=="__main__":
#     import sys

#     login, password = sys.argv[1], sys.argv[2]
#     print login, password
#     flak = Flaker(login=login, password=password)
#     print flak.auth()

#     print flak.bookmarks('szopa')

#     print
#     for f in flak.bookmarks(login="hazan"):
#         for k,v in f.data.items():
#             print "%s: %s"%(k,v)
#         print
