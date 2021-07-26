from airflow.hooks.postgres_hook import PostgresHook
from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults

class DataQualityOperator(BaseOperator):
    """Operator for checking if the results generated by the parsed queries 
    are present, correct and meaningful. 
    In order to pass the quality check, the produced results should NOT match 
    the failure results provided by the user.

    Args:
        redshift_conn_id (str): Postgres connection name created by the user on Airflow;
        target_database (str): Database where the table is located;
        table (str): name of the table that will be tested;
        queries (list): list of queries  that should be performed against the table;
        failure_results (list): list of results that will determine if the check has passed or failed;
    """

    @apply_defaults
    def __init__(self,
                 redshift_conn_id = 'redshift_conn_id',
                 target_database = 'public',
                 table = '',
                 check_quality_queries = [],
                 failure_results = [],
                 *args, **kwargs):

        super(DataQualityOperator, self).__init__(*args, **kwargs)
        self.redshift_conn_id = redshift_conn_id
        self.target_database = target_database
        self.table = table
        self.check_quality_queries = check_quality_queries
        self.failure_results = failure_results

    def execute(self, context):
        self.log.info('DataQualityOperator starting')

        self.log.info('Creating a connection to Redshift')
        redshift_hook = PostgresHook(postgres_conn_id = self.redshift_conn_id)

        result_list = []

        self.log.info(f'Starting the quality checks for the table {self.target_database}.{self.table}')
        for i in range(0, len(self.check_quality_queries)):
            formatted_query = self.check_quality_queries[i].format(self.database + '.' + self.table)

            result = redshift_hook.get_first(formatted_query)[0]
            result_list.append(result)

            if result == self.failure_result[i]:
                raise ValueError(f'Test failed for the {formatted_query} - failure_result: {self.failure_results[i]}')

        self.log.info(f'Quality check passed with success with the results {result_list}')


