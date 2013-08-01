#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import errno
import shutil
import logging
import sys
import imghdr
import glob
import ConfigParser
from optparse import OptionParser
from ext.mediafile import MediaFile
from discogstagger.taggerutils import (
    TaggerUtils,
    create_nfo,
    create_m3u,
    get_images)
from discogstagger.tagger_config import TaggerConfig

import os, errno


p = OptionParser()
p.add_option("-r", "--releaseid", action="store", dest="releaseid",
             help="The discogs.com release id of the target album")
p.add_option("-s", "--source", action="store", dest="sourcedir",
             help="The directory that you wish to tag")
p.add_option("-d", "--destination", action="store", dest="destdir",
             help="The (base) directory to copy the tagged files to")
p.add_option("-c", "--conf", action="store", dest="conffile",
             help="The discogstagger configuration file.")

p.set_defaults(conffile="/etc/discogstagger/discogs_tagger.conf")
(options, args) = p.parse_args()

if not options.sourcedir or not os.path.exists(options.sourcedir):
    p.error("Please specify a valid source directory ('-s')")

tagger_config = TaggerConfig()
tagger_config.read(options.conffile)
config = tagger_config.config

logging.basicConfig(level=config.getint("logging", "level"))
logger = logging.getLogger(__name__)

# read necessary config options for batch processing
id_file = config.get("batch", "id_file")
dir_format_batch = "dir"
dir_format = None

# read tags from batch file if available
tagger_config.read(os.path.join(options.sourcedir, id_file))

if config.get("source", "id"):
    releaseid = config.get("source", "id").strip()

# command line parameter overwrites config parameter in file
if options.releaseid:
    releaseid = options.releaseid

if not releaseid:
    p.error("Please specify the discogs.com releaseid ('-r')")

# read destination directory
if not options.destdir:
    destdir = options.sdir
else:
    destdir = options.destdir
    logger.info("destdir set to %s", options.destdir)

logger.info("Using destination directory: %s", destdir)

discogs_album = DiscogsAlbum(self.ogsrelid, tagger_config)
album = discogs_album.map()

taggerutils = TaggerUtils(options.sourcedir, options.destdir, releaseid,
                          tagger_config, album)

# !TODO - make this a check during the taggerutils run
# ensure we were able to map the release appropriately.
#if not release.tag_map:
#    logger.error("Unable to match file list to discogs release '%s'" %
#                  releaseid)
#    sys.exit()

logger.info("Tagging album '%s - %s'" % (artist, release.album.title))

dest_dir_name = release.dest_dir_name

if os.path.exists(dest_dir_name):
    logger.error("Destination already exists %s" % dest_dir_name)
    sys.exit("%s directory already exists, aborting." % dest_dir_name)
else:
    logger.info("Creating destination directory '%s'" % dest_dir_name)
    mkdir_p(dest_dir_name)

logger.info("Downloading and storing images")
taggerutils.get_images(dest_dir_name)

## !TODO remove all the following stuff, should be done in the taggerutils (rename
## to taghandler?) or in a new class, this wrapper should just provide all needed
## information for the real tagging and thats it.
#disc_names = dict()
#folder_names = dict()
#if release.album.disctotal > 1 and split_discs_folder:
#    logger.debug("Creating disc structure")
#    for i in range(1, release.album.disctotal + 1):
#        folder_name = "%s%.d" % (release.album_folder_name, i)
#        disc_dir_name = os.path.join(dest_dir_name, folder_name)
#        mkdir_p(disc_dir_name)
##This is duplicate, remove one of the following statements
#        disc_names[i] = disc_dir_name
#        folder_names[i] = folder_name
#else:
#    folder_names[1] = ""
##        # copy only if necessary (on request) - otherwise attach original
##        for filename in glob.glob(os.path.join(dest_dir_name, '*.jpg')):
##            shutil.copy(filename, disc_dir_name)
##    # delete only on request
##    for filename in glob.glob(os.path.join(dest_dir_name, '*.jpg')):
##        os.remove(os.path.join(dest_dir_name, filename))

for track in release.tag_map:
    # copy old file into new location
    if release.album.disctotal > 1 and split_discs_folder:
        target_folder = disc_names[int(track.discnumber)]
    else:
        target_folder = dest_dir_name

    logger.debug("Source file %s" % os.path.join(options.sdir,
                 track.orig_file))
    logger.info("Writing file %s" % os.path.join(target_folder, track.new_file))
    logger.debug("metadata -> %.2d %s - %s" % (track.tracknumber, track.artist,
                 track.title))
    logger.debug("----------> %s" % track.new_file)

    shutil.copyfile(track.orig_file,
                    os.path.join(target_folder, track.new_file))

    # load metadata information
    metadata = MediaFile(os.path.join(target_folder, track.new_file))

#    if split_discs_folder and release.album.disctotal > 1:
#        # the fileext should be stored on the album/track as well
#        fileext = os.path.splitext(track.orig_file)[1]
#        disc_title_extension = release._value_from_tag_format(split_discs_extension, 
#            track.tracknumber, track.position - 1, fileext)
#        metadata.album = "%s%s" % (metadata.album, disc_title_extension)

#    if track.discsubtotal:
#        metadata.discsubtotal = track.discsubtotal

    # it does not make sense to store this in the "common" configuration, but only in the 
    # id.txt. we use a special naming convention --> most probably we should reuse the 
    # configuration parser for this one as well, no?
    for name, value in release_tags.items():
        if name.startswith("tag:"):
            name = name.split(":")
            name = name[1]
            setattr(metadata, name, value)

    first_image_name = release.first_image_name

#
# start supplementary actions
#
# adopt for multi disc support (copy to disc folder, add disc number, ...)
logger.info("Generating .nfo file")
create_nfo(release.album.album_info, dest_dir_name, release.nfo_filename)

# adopt for multi disc support
logger.info("Generating .m3u file")
create_m3u(release.tag_map, folder_names, dest_dir_name, release.m3u_filename)


logger.info("Tagging complete.")
