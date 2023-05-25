from unittest.mock import MagicMock, patch

from marshmallow import fields, post_load
from pytest import fixture

from iss_kml.domain.basic_domain import BasicEntity
from iss_kml.domain.basic_domain.basic_entity import missing_id
from iss_kml.domain.basic_domain.util import generic_serialize_roundtrip_test


@fixture
def dummy_entity():
    class DummyEntity(BasicEntity):
        pass

    return DummyEntity


@fixture
def dummy_complex_entity():
    class DummyEntity(BasicEntity):
        def __init__(self, entity_id, texto, numero):
            super(DummyEntity, self).__init__(entity_id)
            self.texto = texto
            self.numero = numero

        class Schema(BasicEntity.Schema):
            texto = fields.Str()
            numero = fields.Number()

            @post_load
            def on_load(self, data, many, partial):
                return DummyEntity(**data)

    return DummyEntity


@fixture
def dummy_entity_adapted():
    class DummyEntity(BasicEntity):
        pass

    adapter = MagicMock()

    entity = DummyEntity()
    entity.set_adapter(adapter)

    return entity, adapter


def test_basic_entity(dummy_entity):
    entity = dummy_entity()

    assert isinstance(entity, BasicEntity)


def test_basic_entity_save(dummy_entity_adapted):
    entity, adapter = dummy_entity_adapted

    entity.save()
    adapter.save.assert_called_once()


def test_basic_entity_update(dummy_entity_adapted):
    entity, adapter = dummy_entity_adapted

    entity.update()

    adapter.save.assert_called_with({'entity_id': entity.entity_id})


def test_basic_entity_delete(dummy_entity_adapted):
    entity, adapter = dummy_entity_adapted

    entity.delete()

    adapter.delete.assert_called_once()


def test_basic_entity_eq(dummy_complex_entity):
    entity1 = dummy_complex_entity(None, 'texto', 42)
    entity2 = dummy_complex_entity(entity1.entity_id, 'texto', 42)
    entity3 = dummy_complex_entity(None, 'outro texto', 42)

    assert entity1 == entity2
    assert entity1 != entity3
    assert entity2 != entity3


def test_basic_entity_serialize(dummy_complex_entity):
    entity = dummy_complex_entity('the_id', 'texto', 42)

    generic_serialize_roundtrip_test(dummy_complex_entity, entity)


def test_basic_entity_hashable(dummy_complex_entity):
    e1 = dummy_complex_entity(None, 'resposta', 42)
    e2 = dummy_complex_entity(None, 'outro', 17)
    e3 = dummy_complex_entity(e1.entity_id, 'novo estado', 42)
    s = {e1, e2, e3}

    assert e1 != e2
    assert e1.entity_id != e2.entity_id
    assert len(s) == 2


@patch('iss_kml.domain.basic_domain.basic_entity.uuid4')
def test_missing_id(uuid4_mock):
    new_id = missing_id()
    uuid4_mock.assert_called_once()
    assert new_id == str(uuid4_mock())
