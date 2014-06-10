Introduction
============

Python wrapper for Basecamp REST API.

The only Python wrapper that doesn't make you parse xml response but provides
native Python objects as response from Basecamp API call.

Usage
-----

Quick example on how to use it. Here we are counting all our hours logged in
during November 2012::

    >>> from basecamp.api import Basecamp
    >>> bc = Basecamp('https://example.basecamphq.com/', 'my_username', 'pass')

    >>> me = bc.getCurrentPerson().id

    >>> total = 0.0
    >>> for te in bc.getEntriesReport('2012-11-01, '2012-11-30', subject_id=me):
    ...     print '%s: %0.2f' % (te.description, float(te.hours))

As you see as response from 'getEntriesReport' we have got list of time entry
objects that have 'description' and 'hours' attributes. No xml parsing.

Authors
-------

Vitaliy Podoba vitaliypodoba [at] gmail dot com
