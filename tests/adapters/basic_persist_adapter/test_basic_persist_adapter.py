from typing import List
from unittest.mock import MagicMock

from pytest import fixture

from uuid import uuid4

from iss_kml.adapters.basic_persist_adapter import BasicPersistAdapter
from iss_kml.domain.basic_domain import BasicEntity


@fixture
def dummy_adapter_class():
    class DummyPersistAdapter(BasicPersistAdapter):
        def __init__(self, adapted_class, fake_db, logger):
            super(DummyPersistAdapter, self).__init__(adapted_class, logger)
            self.fake_db: dict = fake_db

        def list_all(self):
            return [self._class.load(x) for x in self.fake_db.values()]

        def get_by_id(self, item_id):
            return self._class.load(self.fake_db[item_id])

        def save(self, serialized_data):
            entity_id = serialized_data['entity_id'] or str(uuid4())
            serialized_data['entity_id'] = entity_id
            self.fake_db[entity_id] = serialized_data
            return entity_id

        def delete(self, entity_id):
            if entity_id in self.fake_db:
                del self.fake_db[entity_id]

        def save_many(self, entity_list: List[BasicEntity]):
            for obj in entity_list:
                data = obj.to_json()
                self.save(data)

        def delete_many(self, entity_ids: List[str]):
            for entity_id in entity_ids:
                self.delete(entity_id)

        def filter(self, **kwargs):
            raise NotImplementedError

        def lock_row(self, entity_id):
            raise NotImplementedError

        def release_row(self, entity_id):
            raise NotImplementedError

    return DummyPersistAdapter


@fixture
def dummy_serializable():
    class DummySerializable:
        def __init__(self, entity_id, nome, idade):
            self.entity_id = entity_id
            self.nome = nome
            self.idade = idade

        def dump(self):
            return dict(entity_id=self.entity_id,
                        nome=self.nome,
                        idade=self.idade)

        def to_json(self):
            return self.dump()

        @classmethod
        def load(cls, data):
            return cls(**data)

        def save(self, adapter):
            self.entity_id = adapter.save(self.dump())
            return self.entity_id

        def __eq__(self, other):
            return self.entity_id == other.entity_id

    return DummySerializable


def test_basic_persist_adapter(dummy_adapter_class, dummy_serializable):
    fake_db = {}
    logger = MagicMock
    adapter = dummy_adapter_class(adapted_class=dummy_serializable,
                                  fake_db=fake_db,
                                  logger=logger)

    assert adapter.logger == logger

    obj1 = dummy_serializable(None, 'fulano', idade=42)
    obj2 = dummy_serializable(None, nome='beltrano', idade=15)

    id1 = obj1.save(adapter)
    id2 = obj2.save(adapter)

    assert id1 in fake_db
    assert id2 in fake_db

    loaded1 = adapter.get_by_id(id1)
    loaded2 = adapter.get_by_id(id2)

    assert loaded1 == obj1
    assert loaded2 == obj2

    lista = adapter.list_all()
    assert isinstance(lista, list)
    assert all([isinstance(x, dummy_serializable) for x in lista])
    assert lista[0].entity_id in [id1, id2]
    assert lista[1].entity_id in [id1, id2]

    adapter.delete(id1)
    assert id1 not in fake_db
    assert id2 in fake_db

    adapter.delete(id2)
    assert id2 not in fake_db

    # noinspection PyTypeChecker
    adapter.save_many([obj1, obj2])
    assert id1 in fake_db
    assert id2 in fake_db

    adapter.delete_many([id1, id2])
    assert id1 not in fake_db
    assert id2 not in fake_db


def test_adapted_class_properties(dummy_adapter_class, dummy_serializable):
    fake_db = {}
    logger = MagicMock
    adapter = dummy_adapter_class(adapted_class=dummy_serializable,
                                  fake_db=fake_db,
                                  logger=logger)

    assert adapter.adapted_class_name == 'DummySerializable'
    assert adapter.adapted_class == dummy_serializable
