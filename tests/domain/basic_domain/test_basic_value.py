from datetime import datetime

from marshmallow import fields, post_load

from iss_kml.domain.basic_domain import BasicValue
from iss_kml.domain.basic_domain.util import generic_serialize_roundtrip_test


def make_dummy_class():
    class DummyClass(BasicValue):
        def __init__(self,
                     nome: str,
                     idade: int,
                     data: datetime
                     ):
            self.nome = nome
            self.idade = idade
            self.data = data

        class Schema(BasicValue.Schema):
            nome = fields.Str()
            idade = fields.Int()
            data = fields.AwareDateTime()

    class DummyClassContainer(BasicValue):
        def __init__(self,
                     matricula: str,
                     pessoa: DummyClass):
            self.matricula = matricula
            self.pessoa = pessoa

        class Schema(BasicValue.Schema):
            matricula = fields.Str()
            pessoa = fields.Nested(DummyClass.Schema)

    return DummyClass, DummyClassContainer


def test_basic_value_serialize():
    class DummyValue(BasicValue):
        def __init__(self, texto, numero):
            self.texto = texto
            self.numero = numero

        class Schema(BasicValue.Schema):
            texto = fields.Str()
            numero = fields.Number()

            @post_load
            def on_load(self, data, many, partial):
                return DummyValue(**data)

    value = DummyValue('texto', 42)
    generic_serialize_roundtrip_test(DummyValue, value)


def test_baisc_value_repr():
    # noinspection PyPep8Naming
    DummyClass, _ = make_dummy_class()

    dummy_obj = DummyClass('João', 42, datetime(2003, 8, 13, 4, 0))
    representation = str(dummy_obj)

    assert representation == 'DummyClass(data=2003-08-13 04:00:00, ' \
                             'idade=42, nome=João)'


def test_baisc_value_repr_long_values():
    # noinspection PyPep8Naming
    DummyClass, DummyClassContainer = make_dummy_class()
    dummy_obj = DummyClass('João', 42, datetime(2003, 8, 13, 4, 0))
    dummy_cnt = DummyClassContainer(matricula="a1", pessoa=dummy_obj)
    representation = str(dummy_cnt)

    assert representation == 'DummyClassContainer(matricula=a1, ' \
                             'pessoa=DummyClass(data=2003-08-13 04:00:00, ' \
                             'idade=42, nome=João))'
