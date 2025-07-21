from typing import Any, Optional, Union
from collections.abc import Iterable, Mapping

from airflow.models import BaseOperator
from pandas import DataFrame

from apache.airflow.providers.clickhouse.hooks.ClickhouseHook import ClickhouseHook


class ClickhouseOperator(BaseOperator):
    """ClicHouseOperator provide Airflow operator
    execute query on Clickhouse instance
    @author = klimenko.iv@gmail.com."""

    template_fields = ("sql",)
    template_ext = (".sql",)

    parameters = {
        "use_numpy": False,
        "client_name": "airflow-providers-clickhouse-fork",
        "strings_encoding": "utf-8",
        "strings_as_bytes": True,
    }

    def __init__(
        self,
        *,
        sql: Union[str, list[str]],
        click_conn_id: str = "click_default",
        parameters: Optional[Union[Mapping, Iterable]] = None,
        **kwargs: dict[str, Any],
    ) -> None:
        """Initialize method."""

        super().__init__(**kwargs)
        if parameters:
            self.parameters.update(parameters)
        self.sql = sql
        self.click_conn_id: str = click_conn_id
        self.hook = None

    def execute(self, context) -> None:
        """Execute method."""

        self.log.info("Executing: %s", self.sql)
        client = ClickhouseHook(click_conn_id=self.click_conn_id)
        self.log.info("Load client: %s", client)
        rows, col_definitions = client.run(sql=self.sql, parameters=self.parameters, with_column_types=True)
        columns = [column_name for column_name, _ in col_definitions]
        data = DataFrame(rows, columns=columns).to_json(orient="records")
        if self.do_xcom_push:
            self.xcom_push(context, "query_result", data)
