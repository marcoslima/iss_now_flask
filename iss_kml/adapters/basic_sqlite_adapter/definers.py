class DmlStatements:
    SELECT_ALL: str = 'SELECT {} FROM {}'
    SELECT: str = 'SELECT {} FROM {} WHERE {}'
    INSERT: str = 'INSERT INTO {} (entity_id, data) values (?,?)'
    UPDATE: str = 'UPDATE {} SET data=? WHERE {}'
    DELETE: str = 'DELETE FROM {} WHERE {}'


class DdlStatements:
    CREATE_TABLE: str = 'CREATE TABLE {} (entity_id str, data str)'
    CREATE_INDEX: str = 'CREATE INDEX {} ON {} ({})'


def get_ops():
    return {
        "begins_with": (1, "{0} LIKE '{1}%'"),
        "between": (2, "({0} BETWEEN '{1}' AND '{2}')"),
        "contains": (1, "{0} LIKE '%{1}%'"),
        "eq": (1, "{0}='{1}'"),
        "gt": (1, "{0}>'{1}'"),
        "gte": (1, "{0}>='{1}'"),
        "lt": (1, "{0}<'{1}'"),
        "lte": (1, "{0}<='{1}'"),
        "ne": (1, "{0}<>'{1}'")
    }
