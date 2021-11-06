from typing import Iterable, List, Mapping, Optional, Union

from airflow.models import BaseOperator
from pandas import pandas

from apache.airflow.providers.clickhouse.hooks.ClickhouseHook import ClickhouseHook


class ClickhouseOperator(BaseOperator):
    template_fields = ('sql',)
    template_ext = ('.sql',)

    parameters = {
        "use_numpy": False,
        "client_name":"airflow-providers-clickhouse",
        "strings_encoding":"utf-8",
        "strings_as_bytes":True
    }

    def __init__(
            self,
            *,
            sql: Union[str, List[str]],
            click_conn_id: str = 'click_default',
            parameters: Optional[Union[Mapping, Iterable]] = None,
            **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        if parameters:
           self.parameters.update(parameters)
        self.sql = sql
        self.click_conn_id : str = click_conn_id
        self.hook = None

    def execute(self, context) -> None:
        self.log.info('Executing: %s', self.sql)
        client = ClickhouseHook(click_conn_id = self.click_conn_id)
        self.log.info('Load client: %s', client)
        rows, col_definitions = client.run(sql=self.sql, parameters=self.parameters, with_column_types=True)
        columns = [column_name for column_name, _ in col_definitions]
        data = pandas.DataFrame(rows, columns=columns).to_json(orient='records')
        if self.do_xcom_push:
            self.xcom_push(context,"query_result", data)
        return

