from setuptools import setup

setup(
    name='airflow-providers-clickhouse',
    version='0.0.1',
    url='https://just.temp.string',
    license='GNU',
    author='klimenko.iv',
    author_email='klimenko.iv@gmail.com',
    description='Apache Airflow providers for Yandex Clickhouse Database',
    entry_points={
        "apache_airflow_provider": [
            "provider_info=apache.__init__:get_provider_info"
        ]
    },
    packages=['apache',
              'apache.airflow',
              'apache.airflow.providers',
              'apache.airflow.providers.clickhouse',
              'apache.airflow.providers.clickhouse.hooks',
              'apache.airflow.providers.clickhouse.operators'
              ],
    install_requires=['apache-airflow>=2.0', 'clickhouse_driver>=0.2.1', 'pandas>=1.3.2'],
    keywords=['clickhouse', 'airflow', 'providers', 'database', 'ClickhouseHook', 'ClickhouseOperator'],
    include_package_data=True

)
