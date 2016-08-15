"""Configuration for pytest."""

from babelfish.language import Language
import pytest
from sickbeard.common import DOWNLOADED, Quality
from sickbeard.indexers.indexer_config import INDEXER_TVDB
from sickbeard.tv import TVEpisode, TVShow
from subliminal.subtitle import Subtitle
from subliminal.video import Video
import yaml
from yaml.constructor import ConstructorError
from yaml.nodes import MappingNode, SequenceNode


def pytest_collection_modifyitems(config, items):
    """Disable test execution if -p no:unittest is defined."""
    plugins = config.getoption('plugins', default=None)
    if plugins and 'no:unittest' in plugins:
        for item in reversed(items):
            if isinstance(item, pytest.Function):
                items.remove(item)


def _construct_mapping(self, node, deep=False):
    """Custom yaml map constructor to allow lists to be key of a map.

    :param self:
    :param node:
    :param deep:
    :return:
    """
    if not isinstance(node, MappingNode):
        raise ConstructorError(None, None, 'expected a mapping node, but found %s' % node.id, node.start_mark)
    mapping = {}
    for key_node, value_node in node.value:
        is_sequence = isinstance(key_node, SequenceNode)
        key = self.construct_object(key_node, deep=deep or is_sequence)
        try:
            if is_sequence:
                key = tuple(key)
            hash(key)
        except TypeError as exc:
            raise ConstructorError('while constructing a mapping', node.start_mark,
                                   'found unacceptable key (%s)' % exc, key_node.start_mark)
        value = self.construct_object(value_node, deep=deep)
        mapping[key] = value
    return mapping


yaml.Loader.add_constructor('tag:yaml.org,2002:map', _construct_mapping)


def _patch_object(monkeypatch, target, **kwargs):
    for field, value in kwargs.items():
        target.__dict__[field] = value
        monkeypatch.setattr(type(target), field, lambda this: this.field, raising=False)
    return target


@pytest.fixture
def tvshow(create_tvshow):
    return create_tvshow(indexer=INDEXER_TVDB, indexerid=12, name='Show Name', imdbid='tt0000000')


@pytest.fixture
def tvepisode(tvshow, create_tvepisode):
    return create_tvepisode(show=tvshow, season=3, episode=4, indexer=34, file_size=1122334455,
                            name='Episode Title', status=Quality.compositeStatus(DOWNLOADED, Quality.FULLHDBLURAY),
                            release_group='SuperGroup')


@pytest.fixture
def video():
    return Video.fromname('Show.Name.S03E04.mkv')


@pytest.fixture
def create_sub(monkeypatch):
    def create(language, **kwargs):
        target = Subtitle(Language.fromopensubtitles(language))
        return _patch_object(monkeypatch, target, **kwargs)

    return create


@pytest.fixture
def create_tvshow(monkeypatch):
    def create(indexer=INDEXER_TVDB, indexerid=0, lang='', quality=Quality.UNKNOWN, flatten_folders=0,
               enabled_subtitles=0, **kwargs):
        monkeypatch.setattr('sickbeard.tv.TVShow._load_from_db', lambda method: None)
        target = TVShow(indexer=indexer, indexerid=indexerid, lang=lang, quality=quality,
                        flatten_folders=flatten_folders, enabled_subtitles=enabled_subtitles)
        return _patch_object(monkeypatch, target, **kwargs)

    return create


@pytest.fixture
def create_tvepisode(monkeypatch):
    def create(show, season, episode, filepath='', **kwargs):
        monkeypatch.setattr('sickbeard.tv.TVEpisode._specify_episode', lambda method, season, episode: None)
        target = TVEpisode(show=show, season=season, episode=episode, filepath=filepath)
        return _patch_object(monkeypatch, target, **kwargs)

    return create