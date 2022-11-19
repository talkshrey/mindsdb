import sys
from mindsdb_sql.parser.ast import Identifier, Constant, Star, Select, Join, BinaryOperation
from mindsdb.api.mysql.mysql_proxy.controllers.session_controller import SessionController
from mindsdb.interfaces.database.integrations import IntegrationController
from mindsdb.interfaces.model.model_controller import ModelController
from mindsdb.interfaces.database.projects import ProjectController
from mindsdb.interfaces.database.database import DatabaseController


def make_sql_session(company_id):
    server_obj = type('', (), {})()
    server_obj.original_integration_controller = IntegrationController()
    server_obj.original_model_controller = ModelController()
    server_obj.original_project_controller = ProjectController()
    server_obj.original_database_controller = DatabaseController()

    sql_session = SessionController(
        server=server_obj,
        company_id=company_id
    )
    sql_session.database = 'mindsdb'
    return sql_session


def get_where_data(where):
    result = {}
    if type(where) != BinaryOperation:
        raise Exception("Wrong 'where' statement")
    if where.op == '=':
        if type(where.args[0]) != Identifier or type(where.args[1]) != Constant:
            raise Exception("Wrong 'where' statement")
        result[where.args[0].parts[-1]] = where.args[1].value
    elif where.op == 'and':
        result.update(get_where_data(where.args[0]))
        result.update(get_where_data(where.args[1]))
    else:
        raise Exception("Wrong 'where' statement")
    return result


def format_exception_error(exception):
    try:
        exception_type, _exception_object, exception_traceback = sys.exc_info()
        filename = exception_traceback.tb_frame.f_code.co_filename
        line_number = exception_traceback.tb_lineno
        error_message = f'{exception_type.__name__}: {exception}, raised at: {filename}#{line_number}'
    except Exception:
        error_message = str(exception)
    return error_message