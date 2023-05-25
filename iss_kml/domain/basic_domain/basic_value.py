from marshmallow import Schema


class BasicValue:
    @classmethod
    def from_json(cls, dict_data):
        return cls.Schema().load(dict_data)

    def to_json(self):
        return self.Schema().dump(self)

    def __eq__(self, other):
        return all([getattr(self, attr) == getattr(other, attr)
                    for attr in self.Schema().fields.keys()])

    def __repr__(self):
        class_name = self.__class__.__name__
        fields = self.Schema().fields
        values_dict = {field: str(getattr(self, field))
                       for field in fields.keys()}
        values = [f'{field}={value}' for field, value in values_dict.items()]
        values_str = ', '.join(sorted(values))
        return f'{class_name}({values_str})'

    class Schema(Schema):
        pass
