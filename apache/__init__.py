
def get_provider_info():
    return {
        "package-name":            "airflow-providers-clickhouse",
        "name":                    "Clickhouse",
        "description":             "Clickhouse provider for Airflow",
        "versions":                [
            "0.0.1"
        ],
        "additional-dependencies": [
            "apache-airflow>=2.2.0", "clickhouse_driver>=0.2.1", "pandas>=1.3.2"
        ],
        "integrations":            [
            {
                "integration-name": "Clickhouse",
                "external-doc-url": "https://osample.link.com",
                "tags":             [
                    "service", "clickhouse","database","airflow"
                ]
            }
        ],
        "operators":               [
            {
                "integration-name": "Clickhouse",
                "python-modules":   [
                    "apache.airflow.providers.clickhouse.operators.ClickhouseOperator"
                ]
            }
        ],
        "hooks":                   [
            {
                "integration-name": "Clickhouse",
                "python-modules":   [
                    "apache.airflow.providers.clickhouse.hooks.ClickhouseHook"
                ]
            }
        ],
        "connection-types":        [
            {
                "hook-class-name": "apache.airflow.providers.clickhouse.hooks.ClickhouseHook.ClickhouseHook",
                "connection-type": "clickhouse"
            }
        ]
    }
