from typing import Dict, Any, Iterable, Union

from airflow.hooks.dbapi import DbApiHook
from airflow.models.connection import Connection
from clickhouse_driver import Client


class ClickhouseHook(DbApiHook):
    """
    @author = klimenko.iv@gmail.com

    """

    def bulk_dump(self, table, tmp_file):
        pass

    def bulk_load(self, table, tmp_file):
        pass

    conn_name_attr = 'click_conn_id'
    default_conn_name = 'click_default'
    conn_type = 'clickhouse'
    hook_name = 'ClickHouse'
    database = ''

    @staticmethod
    def get_ui_field_behaviour() -> Dict:
        """Returns custom field behaviour"""
        return {
            "hidden_fields": ['extra'],
            "relabeling":    {'schema': 'Database'},
        }

    def get_conn(self, conn_name_attr: str = None) -> Client:

        if conn_name_attr:
            self.conn_name_attr = conn_name_attr
        conn: Connection = self.get_connection(getattr(self, self.conn_name_attr))
        host: str = conn.host
        port: int = int(conn.port) if conn.port else 9000
        user: str = conn.login
        password: str = conn.password
        database: str = conn.schema
        click_kwargs = conn.extra_dejson.copy()
        if password is None:
            password = ''
        click_kwargs.update(port=port)
        click_kwargs.update(user=user)
        click_kwargs.update(password=password)
        if database:
            click_kwargs.update(database=database)

        result = Client(host or 'localhost', **click_kwargs)
        result.connection.connect()
        return result

    def run(self, sql: Union[str, Iterable[str]], parameters: dict = None,
            with_column_types: bool = True, **kwargs) -> Any:

        if isinstance(sql, str):
            queries = (sql,)
        client = self.get_conn()
        result = None
        index = 0
        for query in queries:
            index += 1
            self.log.info("Query_%s  to database : %s", index, query)
            result = client.execute(
                query=query,
                #  params=parameters,
                with_column_types=with_column_types,
            )
            self.log.info("Query_%s completed", index)
        return result
