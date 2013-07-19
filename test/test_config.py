import os, sys
import logging

logging.basicConfig(level=10)
logger = logging.getLogger(__name__)

parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parentdir)

logger.debug("parentdir: %s" % parentdir)

from discogstagger.tagger_config import TaggerConfig

def test_default_values():

    config = TaggerConfig(os.path.join(parentdir, "test/empty.conf"))

    assert config.getboolean("details", "keep_original")
    assert not config.getboolean("details", "use_style")
    assert config.getboolean("details", "use_lower_filenames")

    assert config.get("file-formatting", "images") == "image"

def test_set_values():

    config = TaggerConfig(os.path.join(parentdir, "test/test_values.conf"))

    assert not config.getboolean("details", "keep_original")
    assert config.getboolean("details", "use_style")

    assert config.get("file-formatting", "images") == "XXIMGXX"

    # not overwritten value should stay the same
    assert config.getboolean("details", "use_lower_filenames")

def test_id_tag_name():

    config = TaggerConfig(os.path.join(parentdir, "test/emtpy.conf"))

    assert config.id_tag_name == "discogs_id"

def test_get_without_quotation():

    config = TaggerConfig(os.path.join(parentdir, "test/emtpy.conf"))

# if the value in the config file contains quotation marks, remove those
    assert config.get_without_quotation("details", "join_genres_and_styles") == " & "

def test_get():

    config = TaggerConfig(os.path.join(parentdir, "test/emtpy.conf"))

# if the value is emtpy in the config file, it is returned as None
    assert config.get("tags", "encoder") == None