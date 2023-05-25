from .basic_value import BasicValue
from marshmallow import Schema, fields
from uuid import uuid4


def missing_id():
    return str(uuid4())


class BasicEntity(BasicValue):
    def __init__(self, entity_id=None):
        self.entity_id = entity_id or str(uuid4())
        self.adapter = None

    def set_adapter(self, adapter):
        self.adapter = adapter

    def save(self):
        my_id = self.adapter.save(self.to_json())
        return my_id

    def update(self):
        my_id = self.adapter.save(self.to_json())
        return my_id

    def delete(self):
        self.adapter.delete(self.entity_id)

    def __eq__(self, other):
        return self.entity_id == other.entity_id

    def __hash__(self):
        return hash(self.entity_id)

    class Schema(Schema):
        entity_id = fields.String(required=False,
                                  allow_none=True,
                                  missing=missing_id)
