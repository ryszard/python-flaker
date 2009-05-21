python-flaker
=============

This is the Python client library for [Flaker.pl](http://flaker.pl) (a
Polish service similar to [FriendFeed](http://friendfeed.com)).  It
allows you to interact with your account: submit messages, bookmark
them, browse your friends, and also query the service for messages
meeting certain criteria.

Installation
------------

The easiest way to install python-flaker is to use easy_install:
    $ easy_install python-flaker

If you prefer to use the development version, you can clone the git repository:

    $ git clone git://github.com/ryszard/python-flaker.git


Example
-------------

The library mostly follows the conventions from flaker's [REST
API](http://blog.flaker.pl/api/). Methods for querying messages have
been put together in one method, `query`.

Caveat: `from` is a reserved word in Python, so you should use `from_`
in situations when the API requires `from` (for example, in
`Flaker.query`).

    >>> from flaker import Flaker, FlakUser, Flak

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

Customization
-------------

The easiest way to customize the behavior is to subclass `Flaker`,
`Flak` and `FlakUser`. `Flaker` has two class variables,
`flakuser_class` and `flak_class` which govern the classes
chosen. Override them to use your custom classes.

Author & License
-------
The author of python-flaker is Ryszard Szopa <ryszard.szopa@gmail.com>

The code is distributed under the MIT license. Please see the file
`license.txt` for further details.
