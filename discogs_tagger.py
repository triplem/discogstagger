#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import errno
import logging
import sys

from optparse import OptionParser

from discogstagger.tagger_config import TaggerConfig
from discogstagger.discogsalbum import DiscogsAlbum
from discogstagger.taggerutils import TaggerUtils, TagHandler, FileHandler

import os, errno

def read_id_file(dir, file_name, options):
    # read tags from batch file if available
    idfile = os.path.join(dir, file_name)
    if os.path.exists(idfile):
        tagger_config.read(idfile)
        releaseid = tagger_config.get("source", "id")
    elif options.releaseid:
        releaseid = options.releaseid

    return releaseid

def walk_dir_tree(start_dir, id_file):
    for root, dirs, files in os.walk(start_dir):
        if id_file in files:
            print(root)

p = OptionParser()
p.add_option("-r", "--releaseid", action="store", dest="releaseid",
             help="The release id of the target album")
p.add_option("-s", "--source", action="store", dest="sourcedir",
             help="The directory that you wish to tag")
p.add_option("-d", "--destination", action="store", dest="destdir",
             help="The (base) directory to copy the tagged files to")
p.add_option("-c", "--conf", action="store", dest="conffile",
             help="The discogstagger configuration file.")
p.add_option("--recursive", action="store_true", dest="recursive",
             help="Should albums be searched recursive in the source directory?")
p.add_option("-f", "--force", action="store_true", dest="forceUpdate",
             help="Should albums be updated even though the done token exists?")

p.set_defaults(conffile="conf/empty.conf")
p.set_defaults(recursive=False)
p.set_defaults(forceUpdate=False)
(options, args) = p.parse_args()

if not options.sourcedir or not os.path.exists(options.sourcedir):
    p.error("Please specify a valid source directory ('-s')")

print 'conffile: ' + options.conffile

tagger_config = TaggerConfig(options.conffile)

logging.basicConfig(level=tagger_config.getint("logging", "level"))
logger = logging.getLogger(__name__)

# read necessary config options for batch processing
id_file = tagger_config.get("batch", "id_file")

if options.recursive:
    source_dirs = walk_dir_tree(options.sourcedir, id_file)
else:
    logger.debug("using sourcedir: %s" % options.sourcedir)
    source_dirs = [options.sourcedir]

for source_dir in source_dirs:
    releaseid = read_id_file(source_dir, id_file, options)

    if not releaseid:
        p.error("Please specify the discogs.com releaseid ('-r')")

    # read destination directory
    # !TODO if both are the same, we are not copying anything,
    # this should be "configurable"
    if not options.destdir:
        destdir = source_dir
    else:
        destdir = options.destdir
        logger.info("destdir set to %s", options.destdir)

    logger.info("Using destination directory: %s", destdir)

    logger.info("starting tagging...")
    discogs_album = DiscogsAlbum(releaseid, tagger_config)
    album = discogs_album.map()

    logger.info("Tagging album '%s - %s'" % (album.artist, album.title))

    taggerUtils = TaggerUtils(source_dir, destdir, releaseid,
                              tagger_config, album)

    tagHandler = TagHandler(album, tagger_config)
    fileHandler = FileHandler(album, tagger_config)

    taggerUtils._get_target_list()

    fileHandler.copy_files()

    logger.info("Tagging files")
    tagHandler.tag_album()

    logger.info("Copy other interesting files (on request)")
    fileHandler.copy_other_files()

    logger.info("Downloading and storing images")
    fileHandler.get_images()

    logger.info("Embedding Albumart")
    fileHandler.embed_coverart_album()

    logger.info("Generate m3u")
    taggerUtils.create_m3u(album.target_dir)

    logger.info("Generate nfo")
    taggerUtils.create_nfo(album.target_dir)


    # !TODO - make this a check during the taggerutils run
    # ensure we were able to map the release appropriately.
    #if not release.tag_map:
    #    logger.error("Unable to match file list to discogs release '%s'" %
    #                  releaseid)
    #    sys.exit()


    #dest_dir_name = album.dest_dir_name

    # !TODO this needs to get "fixed" to allow tagging already existing files
    #if os.path.exists(dest_dir_name):
    #    logger.error("Destination already exists %s" % dest_dir_name)
    #    sys.exit("%s directory already exists, aborting." % dest_dir_name)
    #else:
    #    logger.info("Creating destination directory '%s'" % dest_dir_name)
    #    mkdir_p(dest_dir_name)

        # it does not make sense to store this in the "common" configuration, but only in the
        # id.txt. we use a special naming convention --> most probably we should reuse the
        # configuration parser for this one as well, no?
    # !TODO --- do not forget about this one
    #    for name, value in release_tags.items():
    #        if name.startswith("tag:"):
    #            name = name.split(":")
    #            name = name[1]
    #            setattr(metadata, name, value)

    #
    # start supplementary actions
    #
    # adopt for multi disc support (copy to disc folder, add disc number, ...)
    #logger.info("Generating .nfo file")
    #create_nfo(release.album.album_info, dest_dir_name, release.nfo_filename)

    # adopt for multi disc support
    #logger.info("Generating .m3u file")
    #create_m3u(release.tag_map, folder_names, dest_dir_name, release.m3u_filename)

logger.info("Tagging complete.")