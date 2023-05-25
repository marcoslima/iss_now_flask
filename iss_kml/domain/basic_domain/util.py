def generic_serialize_roundtrip_test(cls, obj):
    json_data = obj.to_json()
    loaded = cls.from_json(json_data)
    assert obj == loaded  # noqa
