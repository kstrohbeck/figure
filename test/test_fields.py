from __future__ import absolute_import, unicode_literals

import pytest

from figure import Field, String, Int, Bool, Nested


@pytest.fixture(params=[Field, String, Int, Bool])
def prim_field(request):
    return request.param


@pytest.mark.parametrize('prefix', [[], ['bar'], ['bar', 'baz']])
def test_prim_field_asks_for_correct_path(prim_field, prefix, mocker):
    source = mocker.Mock()
    foo = prim_field()
    foo.attr_name = 'foo'
    _ = foo.get_from_source(source, prefix)
    source.path_for.assert_called_with(prefix + ['foo'])


@pytest.mark.parametrize('value', ['bar', 1, True, None])
def test_prim_field_gets_correct_value(prim_field, value, mocker):
    source = mocker.Mock()
    source.path_for.return_value.value = value
    foo = prim_field()
    foo.attr_name = 'foo'
    path_value = foo.get_from_source(source, [])
    assert path_value == value


def test_instance_initializes_as_none(prim_field, mocker):
    cfg = mocker.Mock()
    foo = prim_field()
    foo.attr_name = 'foo'
    instance = foo.instance_for(cfg)
    instance.initialize()
    assert cfg.foo is None

@pytest.mark.parametrize('default', ['bar', 1, True, None])
def test_prim_field_initializes_to_default(prim_field, default, mocker):
    cfg = mocker.Mock()
    foo = prim_field(default=default)
    foo.attr_name = 'foo'
    instance = foo.instance_for(cfg)
    instance.initialize()
    if default is None:
        assert cfg.foo is None
    else:
        assert cfg.foo == default


@pytest.mark.parametrize('value', ['bar', 1, True, None])
def test_prim_field_doesnt_change_value_on_none(prim_field, mocker, value):
    cfg = mocker.Mock()
    cfg.foo = value
    source = mocker.Mock()
    source.path_for.return_value.value = None
    foo = prim_field()
    foo.attr_name = 'foo'
    instance = foo.instance_for(cfg)
    instance.load_from_source(source, [])
    if value is None:
        assert cfg.foo is None
    else:
        assert cfg.foo == value


@pytest.mark.parametrize('value', ['bar', 1, True, None])
def test_prim_field_doesnt_change_nested_value_on_none(prim_field, mocker, value):
    cfg = mocker.Mock()
    cfg.bar.foo = value
    source = mocker.Mock()
    source.path_for.return_value.value = None
    foo = prim_field()
    foo.attr_name = 'foo'
    instance = foo.instance_for(cfg)
    instance.load_from_source(source, ['bar'])
    if value is None:
        assert cfg.bar.foo is None
    else:
        assert cfg.bar.foo == value


# TODO: Test Nested.
