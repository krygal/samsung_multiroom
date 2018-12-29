Samsung Multiroom (unstable)
======================

Control Samsung Multiroom speakers.

.. image:: https://img.shields.io/travis/krygal/samsung_multiroom/master.svg
    :target: https://travis-ci.org/krygal/samsung_multiroom
.. image:: https://img.shields.io/librariesio/github/krygal/samsung_multiroom.svg
.. image:: https://img.shields.io/codeclimate/maintainability-percentage/krygal/samsung_multiroom.svg
    :target: https://codeclimate.com/github/krygal/samsung_multiroom
.. image:: https://img.shields.io/codeclimate/coverage/krygal/samsung_multiroom.svg
    :target: https://codeclimate.com/github/krygal/samsung_multiroom
.. image:: https://img.shields.io/pypi/v/samsung_multiroom.svg
    :target: https://pypi.org/project/samsung_multiroom/
.. image:: https://img.shields.io/pypi/pyversions/samsung_multiroom.svg
.. image:: https://img.shields.io/pypi/l/samsung_multiroom.svg


Installation
-------------

 .. code:: bash

    pip install samsung_multiroom


Example
-------

.. code:: python

    from samsung_multiroom import SamsungMultiroomSpeaker

    # replace with your speaker's ip address
    ip_address = '192.168.1.129'
    speaker = SamsungMultiroomSpeaker(ip_address)

    # get speaker name
    speaker.get_name()

    # switch source to connect with your samsung tv
    speaker.set_source('soundshare')

    # set volume
    speaker.set_volume(20)

    # play current wifi source
    speaker.set_source('wifi')
    speaker.get_player().resume()

    # pause
    speaker.get_player().pause()

    # get track info
    track = speaker.get_player().get_current_track()
    print(track)


License
-------

MIT License

Copyright (c) 2018 Krystian Galutowski

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
