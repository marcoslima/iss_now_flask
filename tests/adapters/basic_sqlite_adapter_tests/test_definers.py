from iss_kml.adapters.basic_sqlite_adapter.definers import (
    DmlStatements,
    DdlStatements,
    get_ops
)


def test_dml_statements():
    assert DmlStatements.SELECT_ALL == 'SELECT {} FROM {}'
    assert DmlStatements.SELECT == 'SELECT {} FROM {} WHERE {}'
    assert DmlStatements.INSERT == (
        'INSERT INTO {} (entity_id, data) values (?,?)'
    )
    assert DmlStatements.UPDATE == 'UPDATE {} SET data=? WHERE {}'
    assert DmlStatements.DELETE == 'DELETE FROM {} WHERE {}'


def test_ddl_statements():
    assert DdlStatements.CREATE_TABLE == (
        'CREATE TABLE {} (entity_id str, data str)'
    )
    assert DdlStatements.CREATE_INDEX == 'CREATE INDEX {} ON {} ({})'


def test_get_ops():
    ops = get_ops()

    keys = [
        "begins_with",
        "between",
        "contains",
        "eq",
        "gt",
        "gte",
        "lt",
        "lte",
        "ne"]

    for key in keys:
        assert key in ops
