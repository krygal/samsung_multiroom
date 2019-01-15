Samsung Multiroom (WIP)
=======================

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


Example speaker control
-----------------------

**Initialise**

.. code:: python

    from samsung_multiroom import SamsungMultiroomSpeaker

    # initialise (replace with your speaker's ip address)
    speaker = SamsungMultiroomSpeaker('192.168.1.129')

    # get speaker name
    speaker.get_name()


**Basic functions**

.. code:: python

    # get/set volume
    volume = speaker.get_volume()
    print(volume)

    speaker.set_volume(10)

    # switch source to connect with your samsung tv
    speaker.set_source('soundshare')

    # mute/unmute
    speaker.mute()
    speaker.unmute()


**Audio source browsers**

.. code:: python

    # browse dlna device called nas
    browser = speaker.service('dlna').browser
    # or shorter
    browser = speaker.browser('dlna')
    browser = browser.browse('/nas/Music/By Folder/Air/Moon Safari/CD 1')

    for item in browser:
        print(item.object_type, item.object_id, item.artist, '-',  item.name)


    # browse TuneIn radios
    browser = speaker.service('tunein').browser
    browser = browser.browse('/Trending/')

    for item in browser:
        print(item.object_type, item.object_id, item.name)


**App integrations**

.. code:: python

    # check available services
    names = speaker.get_services_names()
    print(names)

    # authenticate (unless you've done it already via mobile app)
    speaker.service('Deezer').login('your email', 'your password')

    browser = speaker.service('Deezer').browser
    browser = browser.browse('/Browse/Rock/Artists/Queen')

    for item in browser:
        print(item.object_type, item.object_id, item.name)


**Player functions**

.. code:: python

    # create playlist from browser items (see above) and play
    speaker.player.play(browser)

    # pause/resume
    speaker.player.pause()
    speaker.player.resume()

    # get track info
    track = speaker.player.get_current_track()
    print(track)


**Equalizer functions**

.. code:: python

    # get preset names
    presets = speaker.equalizer.get_presets_names()
    print(presets)

    # set predefined equalizer settings
    speaker.equalizer.set('Pop')

    # set adhoc settings
    speaker.equalizer.set([4,3,2,1,2,3,0]) # <-6, 6>

    # overwrite current preset
    speaker.equalizer.save()

    # ... or save as a new preset
    speaker.equalizer.save('Experimental')


**Clock functions**

.. code:: python

    # set alarm
    browser = speaker.service('tunein').browser
    browser = browser.browse('/Trending/')

    speaker.clock.alarm.slot(0).set(
        time='17:28',
        weekdays=[0,1,5], # Mon, Tue, Fri
        playlist=browser,
    )

    # enable/disable alarm 0
    speaker.clock.alarm.slot(0).enable()
    speaker.clock.alarm.slot(0).disable()

    # sleep after 30 seconds
    speaker.clock.timer.start(300)

    remaining_time = speaker.clock.timer.get_remaining_time()
    print(remaining_time)


**Speaker discovery**

.. code:: python

    from samsung_multiroom import SamsungSpeakerDiscovery
    speakers = SamsungSpeakerDiscovery().discover() # takes some time

    for s in speakers:
        print(s.get_name(), '@', s.ip_address)


**Speaker grouping**

.. code:: python

    # (after speaker discovery)
    main_speaker = speakers[0]
    rest_speakers = speakers[1:]

    speaker_group = main_speaker.group('My first group', rest_speakers)

    # now use speaker group like a speaker
    speaker_group.set_volume(10)

    browser = speaker_group.service('dlna').browser
    browser = browser.browse('/nas/Music/By Folder/Air/Moon Safari/CD 1')

    speaker_group.player.play(browser)



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
