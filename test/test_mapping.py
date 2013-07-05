#!/usr/bin/python
# -*- coding: utf-8 -*-
import os, sys
import logging

logging.basicConfig(level=10)
logger = logging.getLogger(__name__)

parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parentdir)

logger.debug("parentdir: %s" % parentdir)

from discogstagger.discogsalbum import DiscogsAlbum

class DummyResponse:
    def __init__(self, releaseid):
        __location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
        json_file_name =  "%s/release.json" % releaseid
        json_file_path = os.path.join(__location__, json_file_name)
        json_file = open(json_file_path, "r")

        self.status_code = 200
        self.content = json_file.read()

def test_map_multidisc():
    ogsrelid = "1448190"

    discogs_album = DiscogsAlbum(ogsrelid)
    # mock response, so that the unit tests do not ask for the http connection
    # every time
    discogs_album.release._cached_response = DummyResponse(ogsrelid)

    album = discogs_album.map()

    assert len(album.labels) == 1
    assert album.labels[0] == "Polystar"

    assert len(album.catnumbers) == len(album.labels)
    assert album.catnumbers[0] == "560 938-2"

    assert len(album.images) == 4
    assert album.images[0] == "http://api.discogs.com/image/R-1448190-1220476110.jpeg"

    assert len(album.artists) == 1
    assert album.artists[0] == "Various"

    assert len(album.genres) == 4

    assert len(album.styles) == 4

    assert album.is_compilation

    assert album.disctotal == 2
    assert len(album.discs) == album.disctotal

    assert len(album.discs[0].tracks) == 20
    assert len(album.discs[1].tracks) == 20

# first track on first disc
    track = album.discs[0].tracks[0]

    assert track.tracknumber == 1
    assert track.discnumber == 1
    assert track.title == "La Passion (Radio Cut)"
    assert track.artists[0] == "Gigi D'Agostino"

# last track on first disc
    track = album.discs[0].tracks[19]

    assert track.tracknumber == 20
    assert track.discnumber == 1
    assert track.title == "Last Resort (Album Version Explizit)"
    assert track.artists[0] == "Papa Roach"

# first track on second disc
    track = album.discs[1].tracks[0]

    assert track.tracknumber == 1
    assert track.discnumber == 2
    assert track.title == "Ich Will, Dass Du Mich Liebst (Radio Edit)"
    assert track.artists[0] == "Die 3. Generation"

# last track on first disc
    track = album.discs[1].tracks[19]

    assert track.tracknumber == 20
    assert track.discnumber == 2
    assert track.title == "I Just Wanna Love U (Give It 2 Me) (Radio Edit)"
    assert track.artists[0] == "Jay-Z"

# special character handling
    track = album.discs[1].tracks[18]

    logger.debug("track.artists: %s" % track.artists[1])
    assert track.artists[1] == u"Eißfeldt"

#    logger.debug("album.labels: %s" % album.labels[0])
#    logger.debug("album.catnumbers: %s" % album.catnumbers)
#    logger.debug("album.images %s" % album.images)
#    logger.debug("album.artists %s" % album.artists)
#    logger.debug("album.title %s" % album.title)
#    logger.debug("album.genres %s" % album.genres)
#    logger.debug("album.styles %s" % album.styles)
#    logger.debug("album.discs %s" % len(album.discs))
#    logger.debug("album.discs[0].tracks %s" % len(album.discs[0].tracks))
#    logger.debug("album.discs[1].tracks %s" % len(album.discs[1].tracks))
#    logger.debug("track.title %s" % track.title)

#   assert false

def test_map_multidisc_with_disctitle():
    ogsrelid = "288308"

    discogs_album = DiscogsAlbum(ogsrelid)
    # mock response, so that the unit tests do not ask for the http connection
    # every time
    discogs_album.release._cached_response = DummyResponse(ogsrelid)

    album = discogs_album.map()

    assert len(album.labels) == 1
    assert album.labels[0] == "Epic"

    assert len(album.catnumbers) == len(album.labels)
    assert album.catnumbers[0] == "E2K 69635"

    assert len(album.images) == 4
    assert album.images[0] == "http://api.discogs.com/image/R-288308-1333554422.jpeg"

    assert album.title == "Ladies & Gentlemen - The Best Of George Michael"

    assert len(album.artists) == 1
    logger.debug("album.artists %s" % album.artists[0])
    assert album.artists[0] == "George Michael"

    assert len(album.genres) == 2
    assert album.genres[0] == "Electronic"
    assert album.genres[1] == "Pop"

    assert len(album.styles) == 2
    assert album.styles[0] == "Downtempo"
    assert album.styles[1] == "Synth-pop"

# in discogs it is a compilation
    assert album.is_compilation

    assert album.disctotal == 2
    assert len(album.discs) == album.disctotal

    assert len(album.discs[0].tracks) == 14
    assert len(album.discs[1].tracks) == 14

# first track on first disc
    track = album.discs[0].tracks[0]

    assert track.tracknumber == 1
    assert track.discnumber == 1
    assert track.discsubtitle == "For The Heart"
    assert track.title == "Jesus To A Child"
    assert track.artists[0] == "George Michael"

# last track on first disc
    track = album.discs[0].tracks[13]

    assert track.tracknumber == 14
    assert track.discnumber == 1
    assert track.discsubtitle == "For The Heart"
    assert track.title == "A Different Corner"
    assert track.artists[0] == "George Michael"

# first track on second disc
    track = album.discs[1].tracks[0]

    assert track.tracknumber == 1
    assert track.discnumber == 2
    assert track.title == "Outside"
    assert track.discsubtitle == "For The Feet"
    assert track.artists[0] == "George Michael"
    logger.debug("1discsubtitle: %s " % track.discsubtitle)

# last track on first disc
    track = album.discs[1].tracks[13]

    logger.debug("2discsubtitle: %s " % track.discsubtitle)

    assert track.tracknumber == 14
    assert track.discnumber == 2
    assert track.title == "Somebody To Love"
    assert track.discsubtitle == "For The Feet"
    assert track.artists[0] == "George Michael"

def test_map_multidisc_with_disctitle_for_tracks():
    ogsrelid = "282923"

    discogs_album = DiscogsAlbum(ogsrelid)
    # mock response, so that the unit tests do not ask for the http connection
    # every time
    discogs_album.release._cached_response = DummyResponse(ogsrelid)

    album = discogs_album.map()

    assert len(album.labels) == 1
    assert album.labels[0] == "Columbia"

    assert len(album.catnumbers) == len(album.labels)
    assert album.catnumbers[0] == "COL 513783 2"

    assert album.title == "Live In Concert 2002"

    assert len(album.artists) == 1
    logger.debug("album.artists %s" % album.artists[0])
    assert album.artists[0] == "Deine Lakaien"

    assert len(album.genres) == 1
    assert album.genres[0] == "Electronic"

    assert len(album.styles) == 1
    assert album.styles[0] == "Synth-pop"

    assert not album.is_compilation

    assert album.disctotal == 2
    assert len(album.discs) == album.disctotal

    assert len(album.discs[0].tracks) == 9
    assert len(album.discs[1].tracks) == 13

# first track on first disc
    track = album.discs[0].tracks[0]

    assert track.tracknumber == 1
    assert track.discnumber == 1
    assert not track.discsubtitle
    assert track.title == "Colour-Ize"
    assert track.artists[0] == "Deine Lakaien"

# first track on second disc
    track = album.discs[1].tracks[0]

    assert track.tracknumber == 1
    assert track.discnumber == 2
    assert track.title == "Silence In Your Eyes"
    assert track.discsubtitle == None
    assert track.artists[0] == "Deine Lakaien"

# last track without disctitle on second disc
    track = album.discs[1].tracks[10]

    assert track.tracknumber == 11
    assert track.discnumber == 2
    assert track.title == "Sometimes"
    assert track.discsubtitle == None
    assert track.artists[0] == "Deine Lakaien"

# first track with disctitle on second disc
    track = album.discs[1].tracks[11]

    assert track.tracknumber == 12
    assert track.discnumber == 2
    assert track.title == "Stupid"
    assert track.discsubtitle == "Bonustracks"
    assert track.artists[0] == "Deine Lakaien"