import json
from sqlite3 import connect, OperationalError
from typing import List
from uuid import uuid4

from ..basic_persist_adapter import BasicPersistAdapter

from .definers import DmlStatements, DdlStatements, get_ops
from .exceptions import (SQLiteAdapterSaveException,
                         SQLiteAdapterDeleteException)
from ...domain.basic_domain import BasicEntity


class BasicSQLiteAdapter(BasicPersistAdapter):
    def save_many(self, entity_list: List[BasicEntity]):
        raise NotImplementedError

    def delete_many(self, entity_ids: List[str]):
        raise NotImplementedError

    def lock_row(self, entity_id):
        raise NotImplementedError

    def release_row(self, entity_id):
        raise NotImplementedError

    def __init__(
        self,
        database,
        adapted_class,
        dml_statements=DmlStatements,
        ddl_statements=DdlStatements,
        logger=None
    ):
        super().__init__(adapted_class, logger)

        self._database = database
        self._table_name = adapted_class.__name__
        self._db = self._get_db(database)
        self.DmlStatements = dml_statements
        self.DdlStatements = ddl_statements

    @staticmethod
    def _get_db(database):
        return connect(database)

    def _execute_statement(self, statement):
        cur = self._db.cursor()
        cur.execute(statement)
        self._db.commit()

    def _query_statement(self, statement):
        cur = self._db.cursor()
        cur.execute(statement)

        return cur.fetchall()

    def _instantiate_object(self, item: dict):
        obj = self._class.from_json(item)
        obj.set_adapter(self)
        return obj

    def list_all(self):
        self.logger.info(f'Scanning {self._table_name}...')

        statement = self.DmlStatements.SELECT_ALL.format('*', self._table_name)

        rows = self._query_statement(statement)

        objects = [self._instantiate_object(json.loads(row[1]))
                   for row in rows]
        return objects

    def get_by_id(self, item_id):
        self.logger.info(f'Searching id: {item_id} in {self._table_name}...')

        conditions = f"entity_id='{item_id}'"
        statement = self.DmlStatements.SELECT.format(
            '*', self._table_name, conditions)
        try:
            rows = self._query_statement(statement)
        except OperationalError:
            return None

        if rows:
            return self._instantiate_object(json.loads(rows[0][1]))
        else:
            return None

    def _get_create_statement(self):
        statement = self.DmlStatements.INSERT.format(
            self._table_name)

        return statement

    def _get_update_statement(self, entity_id):
        statement = self.DmlStatements.UPDATE.format(
            self._table_name, f"entity_id='{entity_id}'")

        return statement

    def _create_table(self):
        statement = self.DdlStatements.CREATE_TABLE.format(self._table_name)
        self._execute_statement(statement)

        statement = self.DdlStatements.CREATE_INDEX.format(
            f"ndx_{self._table_name}",
            self._table_name,
            'entity_id')
        self._execute_statement(statement)

    def _save_to_database(self, entity_id, json_data):
        json_str = json.dumps(json_data)
        entity = self.get_by_id(entity_id)

        cur = self._db.cursor()

        if entity is None:
            statement = self._get_create_statement()
            cur.execute(statement, (entity_id, json_str))
        else:
            statement = self._get_update_statement(entity_id)
            cur.execute(statement, (json_str,))

        self._db.commit()

    def _try_save(self, json_data):
        entity_id = self._resolve_entity_id(json_data)

        self.logger.debug(f'Data received to save: {json_data}')

        try:
            self._save_to_database(entity_id, json_data)
            return json_data['entity_id']

        except OperationalError as e:
            return self._check_operational_error(e)

        except Exception as e:
            self._report_and_raise_error(e,
                                         'Error on save entity_id',
                                         SQLiteAdapterSaveException)

    def _check_operational_error(self, e):
        if "no such table" in str(e):
            self._create_table()
            return None
        else:
            self._report_and_raise_error(e,
                                         'Error on save entity_id',
                                         SQLiteAdapterSaveException)

    def _report_and_raise_error(self,
                                exc: Exception,
                                message: str,
                                exc_to_raise):
        msg = f'{message}: {exc.__class__.__name__}({exc})'
        self._logger.error(msg)
        raise exc_to_raise(msg)

    @staticmethod
    def _resolve_entity_id(json_data):
        if 'entity_id' not in json_data or not json_data['entity_id']:
            entity_id = str(uuid4())
            json_data.update(dict(entity_id=entity_id))
        entity_id = json_data['entity_id']
        return entity_id

    def save(self, json_data):
        for _ in range(3):
            result = self._try_save(json_data)
            if result:
                return result

        msg = f'Error creating table: {self._table_name}'
        self._logger.error(msg)

        raise SQLiteAdapterSaveException(msg)

    def delete(self, entity_id):
        self._logger.info(f'Deleting id: {entity_id} in {self._table_name}...')
        conditions = f"entity_id='{entity_id}'"
        statement = self.DmlStatements.DELETE.format(
            self._table_name, conditions)

        try:
            self._execute_statement(statement)
        except Exception as e:
            self._report_and_raise_error(
                e,
                'Error deleting entity_id',
                SQLiteAdapterDeleteException)
        return entity_id

    @staticmethod
    def _get_ops():
        return get_ops()

    @staticmethod
    def _args_from_value(value, arg_count):
        args = []
        if arg_count == 1:
            args.append(value)
        elif arg_count > 1:
            args.extend(value)

        return args

    @staticmethod
    def _get_argcount(op, ops):
        try:
            return ops[op][0]
        except KeyError:
            raise ValueError(f'invalid comparator: {op}')

    @staticmethod
    def _get_op_mask_normalized(arg, op_mask: str):
        is_not_string = type(arg) != str
        return op_mask.replace('\'', '') if is_not_string else op_mask

    @staticmethod
    def _get_attr(field, op, ops, args):
        op_mask = str(ops[op][1])
        op_mask_normalized = BasicSQLiteAdapter._get_op_mask_normalized(
            args[0], op_mask
        )
        attr = op_mask_normalized.format(
            field,
            *args
        )
        return attr

    @staticmethod
    def _parse_conditions(args, kwargs):
        ops = BasicSQLiteAdapter._get_ops()

        attr_list = list(args)
        for k, v in kwargs.items():
            field, op = k.split('__')
            arg_count = BasicSQLiteAdapter._get_argcount(op, ops)

            args = BasicSQLiteAdapter._args_from_value(v, arg_count)
            field = field.replace('_dot_', '.')

            attr_list.append(
                BasicSQLiteAdapter._get_attr(field, op, ops, args))

        if not attr_list:
            raise ValueError('No conditions in the filter.')

        return attr_list

    @staticmethod
    def filter_and(*args, **kwargs):
        pargs = list(args)
        conditions = BasicSQLiteAdapter._parse_conditions(pargs, kwargs)
        return f'({conditions[0]} AND {conditions[1]})'

    @staticmethod
    def filter_or(*args, **kwargs):
        pargs = list(args)
        conditions = BasicSQLiteAdapter._parse_conditions(pargs, kwargs)
        return f'({conditions[0]} OR {conditions[1]})'

    @staticmethod
    def _get_conditions(args, kwargs):
        conditions = BasicSQLiteAdapter._parse_conditions(args, kwargs)
        return str(conditions.pop())

    def filter(self, *args, **kwargs):
        conditions = self._get_conditions(args, kwargs)
        statement = self.DmlStatements.SELECT.format(
            'data', self._table_name, conditions)

        rows = self._query_statement(statement)

        objects = [self._instantiate_object(json.loads(row[0]))
                   for row in rows]
        return objects
