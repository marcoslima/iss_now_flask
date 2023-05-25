from dataclasses import dataclass
from sqlite3 import OperationalError
from typing import Optional
from unittest.mock import patch, Mock, call, MagicMock

import pytest

from iss_kml.adapters.basic_sqlite_adapter import BasicSQLiteAdapter
from iss_kml.adapters.basic_sqlite_adapter.definers import (
    DmlStatements,
    DdlStatements
)
from iss_kml.adapters.basic_sqlite_adapter.exceptions import \
    SQLiteAdapterSaveException, SQLiteAdapterDeleteException


def prefixed(text):
    prefix = "iss_kml.adapters.basic_sqlite_adapter.basic_sqlite_adapter"
    return f'{prefix}.{text}'


@dataclass
class MakeSut:
    mock_database: MagicMock
    mock_adapted_class: MagicMock
    mock_dml_statements: MagicMock
    mock_ddl_statements: MagicMock
    mock_logger: MagicMock
    mock_get_db: MagicMock
    adapter: BasicSQLiteAdapter


@pytest.fixture
def make_sut():
    @patch.object(BasicSQLiteAdapter, '_get_db')
    def _make_sut(mock_get_db,
                  mock_databasae=MagicMock(),
                  mock_adapted_class: Optional[MagicMock] = MagicMock(
                      __name__="Some Class"),
                  mock_dml_statements: Optional[MagicMock] = MagicMock(),
                  mock_ddl_statements: Optional[MagicMock] = MagicMock(),
                  mock_logger: Optional[MagicMock] = MagicMock()):
        kwargs = {'database': mock_databasae,
                  'adapted_class': mock_adapted_class}
        if mock_dml_statements:
            kwargs['dml_statements'] = mock_dml_statements
        if mock_ddl_statements:
            kwargs['ddl_statements'] = mock_ddl_statements
        if mock_logger:
            kwargs['logger'] = mock_logger

        adapter = BasicSQLiteAdapter(**kwargs)
        return MakeSut(mock_databasae,
                       mock_adapted_class,
                       mock_dml_statements,
                       mock_ddl_statements,
                       mock_logger,
                       mock_get_db,
                       adapter)

    return _make_sut


@patch(prefixed("BasicPersistAdapter.__init__"))
def test_init_basic_sqlite_adapter_without_optional_values(mock_super_init,
                                                           make_sut):
    sut_response = make_sut(mock_dml_statements=None,
                            mock_ddl_statements=None,
                            mock_logger=None)
    adapter = sut_response.adapter
    adapted_class = sut_response.mock_adapted_class
    mock_database = sut_response.mock_database
    mock_get_db = sut_response.mock_get_db

    mock_super_init.assert_called_once_with(adapted_class, None)
    mock_get_db.assert_called_once_with(mock_database)

    assert adapter._database == mock_database
    assert adapter._table_name == adapted_class.__name__
    assert adapter._db == mock_get_db.return_value
    assert adapter.DmlStatements == DmlStatements
    assert adapter.DdlStatements == DdlStatements


@patch(prefixed("BasicPersistAdapter.__init__"))
def test_init_basic_sqlite_adapter_with_optional_values(mock_super_init,
                                                        make_sut):
    sut = make_sut()

    mock_super_init.assert_called_once_with(sut.mock_adapted_class,
                                            sut.mock_logger)
    sut.mock_get_db.assert_called_once_with(sut.mock_database)

    assert sut.adapter._database == sut.mock_database
    assert sut.adapter._table_name == sut.mock_adapted_class.__name__
    assert sut.adapter._db == sut.mock_get_db.return_value
    assert sut.adapter.DmlStatements == sut.mock_dml_statements
    assert sut.adapter.DdlStatements == sut.mock_ddl_statements


@patch(prefixed("connect"))
def test_get_db(mock_connect):
    db = BasicSQLiteAdapter._get_db("some_database")

    mock_connect.assert_called_once_with("some_database")

    assert db == mock_connect.return_value


def test_execute_statement(make_sut):
    sut = make_sut()

    sut.adapter._execute_statement("some_statement")

    sut.mock_get_db.return_value.cursor.assert_called_once()
    sut.mock_get_db.return_value.commit.assert_called_once()

    cur = sut.mock_get_db.return_value.cursor.return_value
    cur.execute.assert_called_once_with("some_statement")


def test_query_statement(make_sut):
    sut = make_sut()

    rows = sut.adapter._query_statement("some_statement")

    sut.mock_get_db.return_value.cursor.assert_called_once()

    cur = sut.mock_get_db.return_value.cursor.return_value
    cur.execute.assert_called_once_with("some_statement")

    assert rows == cur.fetchall.return_value


def test_instantiate_object(make_sut):
    sut = make_sut()
    obj = sut.adapter._instantiate_object({"some_key": "some_value"})

    sut.mock_adapted_class.from_json.assert_called_once_with(
        {"some_key": "some_value"}
    )
    mock_entity = sut.mock_adapted_class.from_json.return_value
    mock_entity.set_adapter.assert_called_once_with(sut.adapter)

    assert obj == sut.mock_adapted_class.from_json.return_value


@patch.object(BasicSQLiteAdapter, "_query_statement")
@patch.object(BasicSQLiteAdapter, "_instantiate_object")
@patch(prefixed("json"))
def test_list_all(mock_json,
                  mock_instantiate_object,
                  mock_query_statement,
                  make_sut):
    mock_query_statement.return_value = [["", "some_obj"]]
    logger = Mock()
    dml_statements = Mock()
    sut = make_sut(mock_logger=logger, mock_dml_statements=dml_statements)

    objects = sut.adapter.list_all()

    logger.info.assert_called_once_with("Scanning Some Class...")
    dml_statements.SELECT_ALL.format.assert_called_once_with(
        "*", "Some Class"
    )

    mock_query_statement.assert_called_once_with(
        dml_statements.SELECT_ALL.format.return_value
    )

    mock_json.loads.assert_called_once_with("some_obj")
    mock_instantiate_object.assert_called_once_with(
        mock_json.loads.return_value
    )

    assert objects == [mock_instantiate_object.return_value]


@patch.object(BasicSQLiteAdapter, "_query_statement")
@patch.object(BasicSQLiteAdapter, "_instantiate_object")
@patch(prefixed("json"))
def test_get_by_id_successfully(mock_json,
                                mock_instantiate_object,
                                mock_query_statement,
                                make_sut):
    mock_query_statement.return_value = [["", "some_obj"]]
    logger = Mock()
    dml_statements = Mock()
    sut = make_sut(mock_logger=logger, mock_dml_statements=dml_statements)

    obj = sut.adapter.get_by_id("some_entity_id")

    logger.info.assert_called_once_with(
        "Searching id: some_entity_id in Some Class..."
    )

    dml_statements.SELECT.format.assert_called_once_with(
        "*", "Some Class", "entity_id='some_entity_id'"
    )

    mock_query_statement.assert_called_once_with(
        dml_statements.SELECT.format.return_value
    )

    logger.error.assert_not_called()

    mock_json.loads.assert_called_once_with("some_obj")
    mock_instantiate_object.assert_called_once_with(
        mock_json.loads.return_value
    )

    assert obj == mock_instantiate_object.return_value


@patch.object(BasicSQLiteAdapter, "_query_statement")
@patch.object(BasicSQLiteAdapter, "_instantiate_object")
@patch(prefixed("json"))
def test_get_by_id_failure(mock_json,
                           mock_instantiate_object,
                           mock_query_statement,
                           make_sut):
    mock_query_statement.return_value = []
    logger = Mock()
    dml_statements = Mock()
    sut = make_sut(mock_logger=logger, mock_dml_statements=dml_statements)
    result = sut.adapter.get_by_id("some_entity_id")

    logger.info.assert_called_once_with(
        "Searching id: some_entity_id in Some Class..."
    )

    dml_statements.SELECT.format.assert_called_once_with(
        "*", "Some Class", "entity_id='some_entity_id'"
    )

    mock_query_statement.assert_called_once_with(
        dml_statements.SELECT.format.return_value
    )

    mock_json.loads.assert_not_called()
    mock_instantiate_object.assert_not_called()

    assert result is None


def test_get_create_statement(make_sut):
    sut = make_sut()

    statement = sut.adapter._get_create_statement()

    sut.mock_dml_statements.INSERT.format.assert_called_once_with("Some Class")

    assert statement == sut.mock_dml_statements.INSERT.format.return_value


def test_get_update_statement(make_sut):
    sut = make_sut()
    statement = sut.adapter._get_update_statement("some_entity_id")

    sut.mock_dml_statements.UPDATE.format.assert_called_once_with(
        "Some Class", "entity_id='some_entity_id'"
    )

    assert statement == sut.mock_dml_statements.UPDATE.format.return_value


@patch.object(BasicSQLiteAdapter, "_execute_statement")
def test_create_table(mock_execute_statement, make_sut):
    sut = make_sut()

    sut.adapter._create_table()

    sut.mock_ddl_statements.CREATE_TABLE.format.assert_called_once_with(
        "Some Class")
    sut.mock_ddl_statements.CREATE_INDEX.format.assert_called_once_with(
        "ndx_Some Class",
        "Some Class",
        "entity_id"
    )

    assert mock_execute_statement.call_args_list == [
        call(sut.mock_ddl_statements.CREATE_TABLE.format.return_value),
        call(sut.mock_ddl_statements.CREATE_INDEX.format.return_value),
    ]


@patch.object(BasicSQLiteAdapter, "_get_update_statement")
@patch.object(BasicSQLiteAdapter, "_get_create_statement")
@patch.object(BasicSQLiteAdapter, "get_by_id", return_value=None)
@patch(prefixed("json"))
def test_save_to_database_with_create_statement(mock_json,
                                                mock_get_by_id,
                                                mock_get_create_statement,
                                                mock_get_update_statement,
                                                make_sut):
    sut = make_sut()
    _db = sut.mock_get_db.return_value

    sut.adapter._save_to_database("some_entity_id", "some_json_data")

    mock_json.dumps.assert_called_once_with("some_json_data")
    mock_get_by_id.assert_called_once_with("some_entity_id")
    mock_json_str = mock_json.dumps.return_value
    mock_get_create_statement.assert_called_once()
    mock_statement = mock_get_create_statement.return_value

    _db.cursor.assert_called_once()
    mock_cursor = _db.cursor.return_value
    mock_cursor.execute.assert_called_once_with(
        mock_statement,
        ("some_entity_id", mock_json_str)
    )
    _db.commit.assert_called_once()

    mock_get_update_statement.assert_not_called()


@patch.object(BasicSQLiteAdapter, "_get_create_statement")
@patch.object(BasicSQLiteAdapter, "_get_update_statement")
@patch.object(BasicSQLiteAdapter, "get_by_id")
@patch(prefixed("json"))
def test_save_to_database_with_update_statement(mock_json,
                                                mock_get_by_id,
                                                mock_get_update_statement,
                                                mock_get_create_statement,
                                                make_sut):
    sut = make_sut()
    _db = sut.mock_get_db.return_value

    sut.adapter._save_to_database("some_entity_id", "some_json_data")

    mock_json.dumps.assert_called_once_with("some_json_data")
    mock_get_by_id.assert_called_once_with("some_entity_id")
    mock_json_str = mock_json.dumps.return_value
    mock_get_update_statement.assert_called_once()
    mock_statement = mock_get_update_statement.return_value

    _db.cursor.assert_called_once()
    mock_cursor = _db.cursor.return_value
    mock_cursor.execute.assert_called_once_with(
        mock_statement,
        (mock_json_str,)
    )
    _db.commit.assert_called_once()

    mock_get_create_statement.assert_not_called()


@patch.object(BasicSQLiteAdapter, "_save_to_database")
@patch.object(BasicSQLiteAdapter, "_create_table")
@patch(prefixed("uuid4"))
def test_try_save_without_entity_id_successfully(mock_uuid4,
                                                 mock_create_table,
                                                 mock_save_to_database,
                                                 make_sut):
    mock_uuid4.return_value = "some_uuid4"
    sut = make_sut()

    entity_id = sut.adapter._try_save({})

    mock_uuid4.assert_called_once()
    sut.mock_logger.debug.assert_called_once_with(
        "Data received to save: {'entity_id': 'some_uuid4'}"
    )

    mock_save_to_database.assert_called_once_with("some_uuid4",
                                                  {"entity_id": "some_uuid4"})
    mock_create_table.assert_not_called()

    assert entity_id == "some_uuid4"


@patch.object(BasicSQLiteAdapter, "_save_to_database",
              side_effect=OperationalError("no such table: Any Table"))
@patch.object(BasicSQLiteAdapter, "_create_table")
@patch(prefixed("uuid4"))
def test_try_save_failure_no_such_table(mock_uuid4,
                                        mock_create_table,
                                        mock_save_to_database,
                                        make_sut):
    sut = make_sut()
    entity_id = sut.adapter._try_save({"entity_id": "some_entity_id"})

    mock_uuid4.assert_not_called()
    sut.mock_logger.debug.assert_called_once_with(
        "Data received to save: {'entity_id': 'some_entity_id'}"
    )

    mock_save_to_database.assert_called_once_with(
        "some_entity_id",
        {"entity_id": "some_entity_id"}
    )
    mock_create_table.assert_called_once()

    assert entity_id is None


@patch.object(BasicSQLiteAdapter, "_save_to_database",
              side_effect=OperationalError("Some Error"))
@patch.object(BasicSQLiteAdapter, "_create_table")
@patch(prefixed("uuid4"))
def test_try_save_failure_without_no_such_table(mock_uuid4,
                                                mock_create_table,
                                                mock_save_to_database,
                                                make_sut):
    sut = make_sut()
    with pytest.raises(SQLiteAdapterSaveException) as error:
        sut.adapter._try_save({"entity_id": "some_entity_id"})

    mock_uuid4.assert_not_called()
    sut.mock_logger.debug.assert_called_once_with(
        "Data received to save: {'entity_id': 'some_entity_id'}"
    )
    sut.mock_logger.error.assert_called_once_with(
        "Error on save entity_id: OperationalError(Some Error)"
    )

    mock_save_to_database.assert_called_once_with(
        "some_entity_id",
        {"entity_id": "some_entity_id"}
    )
    mock_create_table.assert_not_called()

    assert str(error.value) == (
        "Error on save entity_id: OperationalError(Some Error)"
    )


@patch.object(BasicSQLiteAdapter, "_save_to_database",
              side_effect=ValueError("Some Generic Error"))
@patch.object(BasicSQLiteAdapter, "_create_table")
@patch(prefixed("uuid4"))
def test_try_save_failure_with_generic_error(mock_uuid4,
                                             mock_create_table,
                                             mock_save_to_database,
                                             make_sut):
    sut = make_sut()
    with pytest.raises(SQLiteAdapterSaveException) as error:
        sut.adapter._try_save({"entity_id": "some_entity_id"})

    mock_uuid4.assert_not_called()
    sut.mock_logger.debug.assert_called_once_with(
        "Data received to save: {'entity_id': 'some_entity_id'}"
    )
    sut.mock_logger.error.assert_called_once_with(
        "Error on save entity_id: ValueError(Some Generic Error)"
    )

    mock_save_to_database.assert_called_once_with(
        "some_entity_id",
        {"entity_id": "some_entity_id"}
    )
    mock_create_table.assert_not_called()

    assert str(error.value) == (
        "Error on save entity_id: ValueError(Some Generic Error)"
    )


@patch.object(BasicSQLiteAdapter, "_try_save")
def test_save_successfully(mock_try_save, make_sut):
    sut = make_sut()

    result = sut.adapter.save("some_json_data")

    mock_try_save.assert_called_once_with("some_json_data")

    sut.mock_logger.error.assert_not_called()

    assert result == mock_try_save.return_value


@patch.object(BasicSQLiteAdapter, "_try_save", return_value=None)
def test_save_failure(mock_try_save, make_sut):
    sut = make_sut()

    with pytest.raises(SQLiteAdapterSaveException) as error:
        sut.adapter.save("some_json_data")

    assert mock_try_save.call_args_list == [
        call("some_json_data"),
        call("some_json_data"),
        call("some_json_data"),
    ]

    sut.mock_logger.error.assert_called_once_with(
        "Error creating table: Some Class")

    assert str(error.value) == "Error creating table: Some Class"


@patch.object(BasicSQLiteAdapter, "_execute_statement")
def test_delete_successfully(mock_execute_statement, make_sut):
    sut = make_sut()
    entity_id = sut.adapter.delete("some_entity_id")

    sut.mock_logger.info.assert_called_once_with(
        "Deleting id: some_entity_id in Some Class..."
    )

    sut.mock_dml_statements.DELETE.format.assert_called_once_with(
        "Some Class", "entity_id='some_entity_id'"
    )

    mock_execute_statement.assert_called_once_with(
        sut.mock_dml_statements.DELETE.format.return_value
    )

    assert entity_id == "some_entity_id"


@patch.object(BasicSQLiteAdapter, "_execute_statement",
              side_effect=Exception("Some Error"))
def test_delete_failure(mock_execute_statement, make_sut):
    sut = make_sut()
    with pytest.raises(SQLiteAdapterDeleteException) as error:
        sut.adapter.delete("some_entity_id")

    sut.mock_logger.info.assert_called_once_with(
        "Deleting id: some_entity_id in Some Class..."
    )

    sut.mock_dml_statements.DELETE.format.assert_called_once_with(
        "Some Class", "entity_id='some_entity_id'"
    )

    mock_execute_statement.assert_called_once_with(
        sut.mock_dml_statements.DELETE.format.return_value
    )

    sut.mock_logger.error.assert_called_once_with(
        "Error deleting entity_id: Exception(Some Error)"
    )

    assert str(error.value) == (
        "Error deleting entity_id: Exception(Some Error)"
    )


@patch(prefixed("get_ops"))
def test_get_ops(mock_get_ops):
    ops = BasicSQLiteAdapter._get_ops()

    mock_get_ops.assert_called_once()

    assert ops == mock_get_ops.return_value


@pytest.mark.parametrize(
    "value,arg_count,expected",
    [(1, 1, [1]), ([1, 2], 2, [1, 2])]
)
def test_args_from_value(value, arg_count, expected):
    args = BasicSQLiteAdapter._args_from_value(value, arg_count)

    assert args == expected


def test_get_argcount_successfully():
    args = BasicSQLiteAdapter._get_argcount("foo", {"foo": ["some_args"]})

    assert args == "some_args"


def test_get_argcount_failure():
    with pytest.raises(ValueError) as error:
        BasicSQLiteAdapter._get_argcount("foo", {"some_key": ["some_args"]})

    assert str(error.value) == "invalid comparator: foo"


def test_get_op_mask_normalized_with_arg_not_string():
    result = BasicSQLiteAdapter._get_op_mask_normalized({},
                                                        "s\'om\'e_op\'_mask")

    assert result == "some_op_mask"


def test_get_op_mask_normalized_with_arg_string():
    result = BasicSQLiteAdapter._get_op_mask_normalized(
        "some_arg", "some_op_mask"
    )

    assert result == "some_op_mask"


@patch.object(BasicSQLiteAdapter, "_get_op_mask_normalized")
def test_get_attr(mock_get_op_mask_normalized):
    result = BasicSQLiteAdapter._get_attr("some_field",
                                          "foo",
                                          {"foo": ["", "some_ops"]},
                                          ["some_args"])

    mock_get_op_mask_normalized.assert_called_once_with(
        "some_args", "some_ops"
    )
    mock_mask = mock_get_op_mask_normalized.return_value

    mock_mask.format.assert_called_once_with("some_field", "some_args")

    assert result == mock_mask.format.return_value


@patch.object(BasicSQLiteAdapter, "_args_from_value")
@patch.object(BasicSQLiteAdapter, "_get_argcount")
@patch.object(BasicSQLiteAdapter, "_get_attr")
@patch.object(BasicSQLiteAdapter, "_get_ops")
def test_parse_conditions_successfully(mock_get_ops,
                                       mock_get_attr,
                                       mock_get_argcount,
                                       mock_args_from_value):
    result = BasicSQLiteAdapter._parse_conditions(
        ["some_arg", "some_arg"],
        {"some__key": "some_value"}
    )

    mock_get_ops.assert_called_once()

    mock_get_argcount.assert_called_once_with(
        "key", mock_get_ops.return_value
    )

    mock_args_from_value.assert_called_once_with(
        "some_value", mock_get_argcount.return_value
    )

    mock_get_attr.assert_called_once_with(
        "some",
        "key",
        mock_get_ops.return_value,
        mock_args_from_value.return_value
    )

    assert result == ["some_arg", "some_arg", mock_get_attr.return_value]


@patch.object(BasicSQLiteAdapter, "_args_from_value")
@patch.object(BasicSQLiteAdapter, "_get_argcount")
@patch.object(BasicSQLiteAdapter, "_get_attr")
@patch.object(BasicSQLiteAdapter, "_get_ops")
def test_parse_conditions_failure(mock_get_ops,
                                  mock_get_attr,
                                  mock_get_argcount,
                                  mock_args_from_value):
    with pytest.raises(ValueError) as error:
        BasicSQLiteAdapter._parse_conditions(
            [],
            {}
        )

    mock_get_ops.assert_called_once()
    mock_get_argcount.assert_not_called()
    mock_args_from_value.assert_not_called()
    mock_get_attr.assert_not_called()

    assert str(error.value) == "No conditions in the filter."


@pytest.mark.parametrize(
    "method,operator",
    [
        ("filter_and", "AND"),
        ("filter_or", "OR")
    ]
)
@patch.object(BasicSQLiteAdapter, "_parse_conditions")
def test_filter_operators(mock_parse_conditions, method, operator):
    mock_parse_conditions.return_value = ["value1", "value2"]
    result = getattr(BasicSQLiteAdapter, method)("some_arg", some="kwarg")

    mock_parse_conditions.assert_called_once_with(
        ["some_arg"], {"some": "kwarg"}
    )

    assert result == f"(value1 {operator} value2)"


@patch.object(BasicSQLiteAdapter, "_parse_conditions")
def test_get_conditions(mock_parse_conditions):
    mock_parse_conditions.return_value = ["value1", "value2"]
    result = BasicSQLiteAdapter._get_conditions("some_arg", "some_kwarg")

    mock_parse_conditions.assert_called_once_with(
        "some_arg", "some_kwarg"
    )

    assert result == "value2"


@patch.object(BasicSQLiteAdapter, "_get_conditions")
@patch.object(BasicSQLiteAdapter, "_query_statement")
@patch.object(BasicSQLiteAdapter, "_instantiate_object")
@patch(prefixed("json"))
def test_filter(mock_json,
                mock_instantiate_object,
                mock_query_statement,
                mock_get_conditions,
                make_sut):
    mock_query_statement.return_value = [["some_value"]]
    sut = make_sut()
    objects = sut.adapter.filter("some_arg", some="kwargs")

    mock_get_conditions.assert_called_once_with(
        ("some_arg",), {"some": "kwargs"}
    )

    sut.mock_dml_statements.SELECT.format.assert_called_once_with(
        "data", "Some Class", mock_get_conditions.return_value
    )

    mock_query_statement.assert_called_once_with(
        sut.mock_dml_statements.SELECT.format.return_value
    )

    mock_json.loads.assert_called_once_with(
        "some_value"
    )

    mock_instantiate_object.assert_called_once_with(
        mock_json.loads.return_value
    )

    assert objects == [mock_instantiate_object.return_value]
