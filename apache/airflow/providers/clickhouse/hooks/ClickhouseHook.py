from typing import Any, Iterable, Union
from urllib.parse import quote, urlencode, unquote, parse_qs, urlparse, urlunparse

from airflow.exceptions import AirflowException
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

    def _get_field(self, extra_dict, field_name):
        backcompat_prefix = "extra__clickhouse__"
        backcompat_key = f"{backcompat_prefix}{field_name}"
        if field_name.startswith("extra__"):
            raise ValueError(
                f"Got prefixed name {field_name}; please remove the '{backcompat_prefix}' prefix "
                f"when using this method."
            )
        if field_name in extra_dict:
            import warnings

            if backcompat_key in extra_dict:
                warnings.warn(
                    f"Conflicting params `{field_name}` and `{backcompat_key}` found in extras. "
                    f"Using value for `{field_name}`.  Please ensure this is the correct "
                    f"value and remove the backcompat key `{backcompat_key}`.",
                    UserWarning,
                    stacklevel=2,
                )
            return extra_dict[field_name] or None
        return extra_dict.get(backcompat_key) or None

    @property
    def http_port(self) -> int:
        conn = self.get_connection(self.click_conn_id)  # type: ignore[attr-defined]
        extra_dict = conn.extra_dejson
        field_value = self._get_field(extra_dict, "http_port")
        try:
            return int(field_value)
        except ValueError:
            raise AirflowException(
                f"The http_port field should be a integer. "
                f'Current value: "{field_value}" (type: {type(field_value)}). '
                f"Please check the connection configuration."
            )

    @classmethod
    def get_connection_form_widgets(cls) -> dict[str, Any]:
        """Return connection widgets to add to connection form."""
        from flask_appbuilder.fieldwidgets import BS3TextFieldWidget
        from flask_babel import lazy_gettext
        from wtforms import IntegerField

        return {
            "http_port": IntegerField(
                lazy_gettext("HTTP default port"),
                widget=BS3TextFieldWidget(),
                default=8123,
            ),
        }

    @classmethod
    def get_ui_field_behaviour(cls) ->  dict[str, Any]:
        """Returns custom field behaviour"""
        return {
            "hidden_fields": ['extra'],
            "relabeling": {'schema': 'Database', 'port': "Native Protocal port"},
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
        # if "http_port" in click_kwargs:
        click_kwargs.pop("http_port", None)
        # if "extra__clickhouse__http_port" in click_kwargs:
        click_kwargs.pop("extra__clickhouse__http_port", None)
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


    def get_uri(self) -> str:
        conn_id = getattr(self, self.conn_name_attr)
        airflow_conn = self.get_connection(conn_id)
        if airflow_conn.conn_type is None:
            airflow_conn.conn_type = self.conn_type
        airflow_uri = unquote(airflow_conn.get_uri())
        airflow_uri = airflow_uri.replace("/?", "?")
        url_parts = urlparse(airflow_uri)
        query_params = parse_qs(url_parts.query)
        query_params.pop('__extra__', None)
        url_parts = url_parts._replace(query=urlencode(query_params, doseq=True))
        sqlalchemy_uri = urlunparse(url_parts)
        return sqlalchemy_uri


    def get_jdbc_uri(self) -> str:
        """Return connection in URI format."""

        # conn = self.get_connection(getattr(self, self.conn_name_attr))
        # conn.schema = self.database or conn.schema
        # http_port = conn.extra_dejson.get("http_port", 8123)
        # conn.extra
        # uri = conn.get_uri().replace(f":{conn.port}", f":{http_port}")
        # return uri

        conn = self.get_connection(getattr(self, self.conn_name_attr))
        uri = f"{self.conn_type.lower().replace('_', '-')}://"


        if conn.host and "://" in conn.host:
            protocol, host = conn.host.split("://", 1)
        else:
            protocol, host = None, conn.host

        if protocol:
            uri += f"{protocol}://"

        authority_block = ""
        if conn.login is not None:
            authority_block += quote(conn.login, safe="")

        if conn.password is not None:
            authority_block += ":" + quote(conn.password, safe="")

        if authority_block > "":
            authority_block += "@"
            uri += authority_block

        host_block = ""
        if host:
            host_block += quote(host, safe="")

        if self.http_port:
            if host_block == "" and authority_block == "":
                host_block += f"@:{self.http_port}"
            else:
                host_block += f":{self.http_port}"

        if conn.schema:
            host_block += f"/{quote(conn.schema, safe='')}"

        uri += host_block

        return uri

    def run(self, sql: Union[str, Iterable[str]], parameters: dict = None,
            with_column_types: bool = True, **kwargs) -> Any:

        queries: Iterable[str] = ...
        if isinstance(sql, str):
            queries = (sql,)
        else:
            queries = sql
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
