from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.empty import EmptyOperator

from apache.airflow.providers.clickhouse.operators.ClickhouseOperator import ClickhouseOperator

with DAG(
    dag_id="example_clickhouse_operator",
    start_date=datetime(2021, 1, 1),
    dagrun_timeout=timedelta(minutes=60),
    tags=["example", "clickhouse"],
    catchup=False,
    template_searchpath="$AIRFLOW_HOME/include",
) as dag:
    run_this_last = EmptyOperator(task_id="run_this_last")

    select_data = ClickhouseOperator(
        task_id="select_quit",
        sql="query.sql",
        click_conn_id="my_click",
        do_xcom_push=False,
    )
    select_push = ClickhouseOperator(
        task_id="select_xcom",
        sql="select * from TestTable;",
        click_conn_id="my_click",
    )

    select_data >> select_push >> run_this_last
