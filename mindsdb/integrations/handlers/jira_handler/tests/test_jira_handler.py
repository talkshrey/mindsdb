import unittest
from mindsdb.integrations.handlers.jira_handler.jira_handler import JiraHandler
from mindsdb.api.mysql.mysql_proxy.libs.constants.response_type import RESPONSE_TYPE


class JiraHandlerTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.kwargs = {
            "table_name": "project",
            "jira_url": "https://jira.linuxfoundation.org/",
            "user_id": "balaceg",
            "api_key": "4Rhq&Ehd#KV4an!",
            "jira_query": "project = RELENG and status = 'In Progress'"
        }
        cls.handler = JiraHandler('test_jira_handler', cls.kwargs)

    def test_0_check_connection(self):
        assert self.handler.check_connection()

    def test_1_native_query_select(self):
        query = "SELECT * FROM project LIMIT 10"
        result = self.handler.native_query(query)
        assert result.type is RESPONSE_TYPE.TABLE

    def test_2_get_tables(self):
        tables = self.handler.get_tables()
        assert tables.type is not RESPONSE_TYPE.ERROR

    def test_3_get_columns(self):
        columns = self.handler.get_columns()
        assert columns.type is not RESPONSE_TYPE.ERROR


if __name__ == '__main__':
    unittest.main()
