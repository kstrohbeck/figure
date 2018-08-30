from __future__ import absolute_import, unicode_literals

import os
import sys

import pytest

try:
    import ConfigParser as configparser
except ImportError:
    import configparser

from figure import ConfigParser, Dict, Environment, FlatModule, Object


@pytest.fixture
def fake_obj():
    class Bar(object):
        baz = 'quux'
    class Fake(object):
        foo = 1
        bar = Bar()
    return Fake()


@pytest.fixture
def cfg_parser():
    parser = configparser.ConfigParser()
    parser.add_section('general')
    parser.set('general', 'bar', '1')
    parser.add_section('foo')
    parser.set('foo', 'baz', 'true')
    parser.add_section('foo.bar')
    parser.set('foo.bar', 'baz', 'hello')
    return parser


def test_env_single_segment_has_correct_str():
    source = Environment()
    path = source.path_for(['foo'])
    assert str(path) == 'FOO'


def test_env_multiple_segments_have_correct_str():
    source = Environment()
    path = source.path_for(['foo', 'bar'])
    assert str(path) == 'FOO_BAR'


def test_env_path_starts_with_prefix():
    source = Environment('test_prefix')
    path = source.path_for(['foo'])
    assert str(path).startswith('TEST_PREFIX')


def test_env_value_is_correct():
    os.environ['FOO'] = 'hello'
    source = Environment()
    path = source.path_for(['foo'])
    assert path.value == 'hello'


def test_prefixed_env_value_is_correct():
    os.environ['TEST_PREFIX_FOO'] = 'hello'
    source = Environment('test_prefix')
    path = source.path_for(['foo'])
    assert path.value == 'hello'


def test_nonexistent_env_value_returns_none():
    del os.environ['FOO']
    source = Environment()
    path = source.path_for(['foo'])
    assert path.value is None


def test_flat_module_path_is_correct():
    source = FlatModule(None)
    path = source.path_for(['foo', 'bar'])
    assert str(path) == 'FOO_BAR'


def test_flat_module_loads_module_from_string(mocker):
    module = mocker.Mock()
    sys.modules['settings_module'] = module
    source = FlatModule('settings_module')
    path = source.path_for(['foo', 'bar'])
    assert path.value == module.FOO_BAR
    del sys.modules['settings_module']


def test_flat_module_returns_none_for_nonexistent_module():
    assert 'settings_module' not in sys.modules
    source = FlatModule('settings_module')
    path = source.path_for(['foo', 'bar'])
    assert path.value is None


def test_dict_path_is_correct():
    source = Dict({})
    path = source.path_for(['foo', 'bar'])
    assert str(path) == 'foo.bar'


def test_dict_returns_correct_value():
    source = Dict({'foo': 'bar'})
    path = source.path_for(['foo'])
    assert path.value == 'bar'


def test_dict_returns_correct_nested_value():
    source = Dict({'foo': {'bar': 'baz'}})
    path = source.path_for(['foo', 'bar'])
    assert path.value == 'baz'


def test_dict_returns_none_if_value_doesnt_exist():
    source = Dict({'foo': {'baz': 'quux'}})
    path = source.path_for(['foo', 'bar'])
    assert path.value is None


def test_dict_returns_none_if_parent_doesnt_exist():
    source = Dict({'bar': {'baz': 'quux'}})
    path = source.path_for(['foo', 'bar'])
    assert path.value is None


def test_dict_returns_none_if_parent_wasnt_dict():
    source = Dict({'foo': 'bar'})
    path = source.path_for(['foo', 'bar'])
    assert path.value is None


def test_object_path_is_correct():
    source = Object(None)
    path = source.path_for(['foo', 'bar'])
    assert str(path) == 'foo.bar'


def test_object_returns_correct_value(fake_obj):
    source = Object(fake_obj)
    path = source.path_for(['foo'])
    assert path.value == 1


def test_object_returns_correct_nested_value(fake_obj):
    source = Object(fake_obj)
    path = source.path_for(['bar', 'baz'])
    assert path.value == 'quux'


def test_object_returns_none_if_value_doesnt_exist(fake_obj):
    source = Object(fake_obj)
    path = source.path_for(['bar', 'foo'])
    assert path.value is None


def test_object_returns_none_if_parent_doesnt_exist(fake_obj):
    source = Object(fake_obj)
    path = source.path_for(['quux', 'bar'])
    assert path.value is None


def test_object_returns_none_if_parent_wasnt_object(fake_obj):
    source = Object(fake_obj)
    path = source.path_for(['foo', 'bar'])
    assert path.value is None


def test_cfg_parser_single_prefix_has_correct_section():
    source = ConfigParser(None)
    path = source.path_for(['foo', 'bar'])
    assert str(path).startswith('[foo]')


def test_cfg_parser_multi_prefix_has_correct_section():
    source = ConfigParser(None)
    path = source.path_for(['foo', 'bar', 'baz'])
    assert str(path).startswith('[foo.bar]')


def test_cfg_parser_uses_custom_separator_in_section():
    source = ConfigParser(None, sep='/')
    path = source.path_for(['foo', 'bar', 'baz'])
    assert str(path).startswith('[foo/bar]')


def test_cfg_parser_non_prefixed_has_general_section():
    source = ConfigParser(None)
    path = source.path_for(['foo'])
    assert str(path).startswith('[general]')


def test_cfg_parser_uses_custom_general_section():
    source = ConfigParser(None, general='defaults')
    path = source.path_for(['foo'])
    assert str(path).startswith('[defaults]')

def test_cfg_parser_returns_correct_general_value(cfg_parser):
    source = ConfigParser(cfg_parser)
    path = source.path_for(['bar'])
    assert path.value == '1'


def test_cfg_parser_returns_correct_single_nested_value(cfg_parser):
    source = ConfigParser(cfg_parser)
    path = source.path_for(['foo', 'baz'])
    assert path.value == 'true'


def test_cfg_parser_returns_correct_multi_nested_value(cfg_parser):
    source = ConfigParser(cfg_parser)
    path = source.path_for(['foo', 'bar', 'baz'])
    assert path.value == 'hello'


def test_cfg_parser_returns_none_for_missing_value(cfg_parser):
    source = ConfigParser(cfg_parser)
    path = source.path_for(['baz'])
    assert path.value is None


def test_cfg_parser_returns_none_for_missing_nested_value(cfg_parser):
    source = ConfigParser(cfg_parser)
    path = source.path_for(['foo', 'quux'])
    assert path.value is None


def test_cfg_parser_returns_none_for_missing_parent(cfg_parser):
    source = ConfigParser(cfg_parser)
    path = source.path_for(['quux', 'bar'])
    assert path.value is None
