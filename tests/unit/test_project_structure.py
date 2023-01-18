from unittest.mock import patch
import datetime as dt
import time
import pytest

import pandas as pd

from mindsdb_sql import parse_sql

from .executor_test_base import BaseExecutorDummyML


class TestProjectStructure(BaseExecutorDummyML):

    def wait_predictor(self, project, name, filter=None):
        # wait
        done = False
        for attempt in range(200):
            sql = f"select * from {project}.models_versions where name='{name}'"
            if filter is not None:
                for k, v in filter.items():
                    sql += f" and {k}='{v}'"
            ret = self.run_sql(sql)
            if not ret.empty:
                if ret['STATUS'][0] == 'complete':
                    done = True
                    break
                elif ret['STATUS'][0] == 'error':
                    break
            time.sleep(0.5)
        if not done:
            raise RuntimeError("predictor didn't created")

    def run_sql(self, sql, throw_error=True, database='mindsdb'):
        self.command_executor.session.database = database
        ret = self.command_executor.execute_command(
            parse_sql(sql, dialect='mindsdb')
        )
        if throw_error:
            assert ret.error_code is None
        if ret.data is not None:
            columns = [
                col.alias if col.alias is not None else col.name
                for col in ret.columns
            ]
            return pd.DataFrame(ret.data, columns=columns)

    def get_models(self):
        models = {}
        for p in self.db.Predictor.query.all():
            models[p.id] = p
        return models

    @patch('mindsdb.integrations.handlers.postgres_handler.Handler')
    def test_version_managing(self, data_handler):
        # set up

        df = pd.DataFrame([
            {'a': 1, 'b': dt.datetime(2020, 1, 1)},
            {'a': 2, 'b': dt.datetime(2020, 1, 2)},
            {'a': 1, 'b': dt.datetime(2020, 1, 3)},
        ])
        self.set_handler(data_handler, name='pg', tables={'tasks': df})

        # ================= retrain cycles =====================

        # create folder
        self.run_sql('create database proj')

        # -- create model --
        self.run_sql(
            '''
                CREATE PREDICTOR proj.task_model
                from pg (select * from tasks)
                PREDICT a
                using engine='dummy_ml',
                tag = 'first',
                join_learn_process=true
            '''
        )
        self.wait_predictor('proj', 'task_model')

        # check input to data handler
        assert data_handler().native_query.call_args[0][0] == 'select * from tasks'

        # tag works in create model
        ret = self.run_sql('select * from proj.models')
        assert ret['TAG'][0] == 'first'

        # use model
        ret = self.run_sql('''
             SELECT m.*
               FROM pg.tasks as t
               JOIN proj.task_model as m
        ''')

        assert len(ret) == 3
        assert ret.predicted[0] == 42

        # -- retrain predictor with tag --
        data_handler.reset_mock()
        self.run_sql(
            '''
                retrain proj.task_model
                from pg (select * from tasks where a=2)
                PREDICT b
                using tag = 'second',
                join_learn_process=true
            '''
        )
        self.wait_predictor('proj', 'task_model', {'tag': 'second'})

        # get current model
        ret = self.run_sql('select * from proj.models')

        # check target
        assert ret['PREDICT'][0] == 'b'

        # check label
        assert ret['TAG'][0] == 'second'

        # check integration sql
        assert data_handler().native_query.call_args[0][0] == 'select * from tasks where a=2'

        # use model
        ret = self.run_sql('''
             SELECT m.*
               FROM pg.tasks as t
               JOIN proj.task_model as m
        ''')
        assert ret.predicted[0] == 42

        # used model has tag 'second'
        models = self.get_models()
        model_id = ret.predictor_id[0]
        assert models[model_id].label == 'second'

        # -- retrain again with active=0 --
        data_handler.reset_mock()
        self.run_sql(
            '''
                retrain proj.task_model
                from pg (select * from tasks where a=2)
                PREDICT a
                using tag='third', active=0
            '''
        )
        self.wait_predictor('proj', 'task_model', {'tag': 'third'})

        ret = self.run_sql('select * from proj.models')

        # check target is from previous retrain
        assert ret['PREDICT'][0] == 'b'

        # use model
        ret = self.run_sql('''
             SELECT m.*
               FROM pg.tasks as t
               JOIN proj.task_model as m
        ''')

        # used model has tag 'second' (previous)
        models = self.get_models()
        model_id = ret.predictor_id[0]
        assert models[model_id].label == 'second'

        # ================ working with inactive versions =================

        # run 3rd version model and check used model version
        ret = self.run_sql('''
             SELECT m.*
               FROM pg.tasks as t
               JOIN proj.task_model.3 as m
        ''')

        # 3rd version was used
        models = self.get_models()
        model_id = ret.predictor_id[0]
        assert models[model_id].label == 'third'

        # one-line query model by version
        ret = self.run_sql('SELECT * from proj.task_model.3 where a=1 and b=2')
        model_id = ret.predictor_id[0]
        assert models[model_id].label == 'third'

        # check exception: not existing version
        with pytest.raises(Exception) as exc_info:
            self.run_sql(
                'SELECT * from proj.task_model.4 where a=1 and b=2',
            )
        assert 'does not exists' in str(exc_info.value)

        # ===================== one-line with 'use database'=======================

        # active
        ret = self.run_sql('SELECT * from task_model where a=1 and b=2', database='proj')
        model_id = ret.predictor_id[0]
        assert models[model_id].label == 'second'


        # inactive
        ret = self.run_sql('SELECT * from task_model.3 where a=1 and b=2', database='proj')
        model_id = ret.predictor_id[0]
        assert models[model_id].label == 'third'

        # ================== managing versions =========================

        # check 'show models' command in different combination
        # Show models <from | in> <project> where <expr>
        ret = self.run_sql('Show models')
        assert len(ret) == 1 and ret['NAME'][0] == 'task_model'

        ret = self.run_sql('Show models from proj')
        assert len(ret) == 1 and ret['NAME'][0] == 'task_model'

        ret = self.run_sql('Show models in proj')
        assert len(ret) == 1 and ret['NAME'][0] == 'task_model'

        ret = self.run_sql("Show models where name='task_model'")
        assert len(ret) == 1 and ret['NAME'][0] == 'task_model'

        # model is not exists
        ret = self.run_sql("Show models from proj where name='xxx'")
        assert len(ret) == 0

        # ----------------

        # See all versions
        ret = self.run_sql('select * from proj.models_versions')
        # we have all tags in versions
        assert set(ret['TAG']) == {'first', 'second', 'third'}

        # Set active selected version
        self.run_sql('''
           update proj.models_versions 
           set active=1
           where version=1 and name='task_model' 
        ''')

        # get active version
        ret = self.run_sql('select * from proj.models_versions where active = 1')
        assert ret['TAG'][0] == 'first'

        # use active version ?

        # Delete specific version
        self.run_sql('''
           delete from proj.models_versions 
           where version=2 
           and name='task_model'
        ''')

        # deleted version not in list
        ret = self.run_sql('select * from proj.models_versions')
        assert len(ret) == 2
        assert 'second' not in ret['TAG']

        # try to use deleted version
        with pytest.raises(Exception) as exc_info:
            self.run_sql(
                'SELECT * from proj.task_model.2 where a=1',
            )
        assert 'does not exists' in str(exc_info.value)

        # exception with deleting active version
        with pytest.raises(Exception) as exc_info:
            self.run_sql('''
               delete from proj.models_versions 
               where version=1 
               and name='task_model'
            ''')
        assert "Can't remove active version" in str(exc_info.value)

        # exception with deleting non-existing version
        with pytest.raises(Exception) as exc_info:
            self.run_sql('''
               delete from proj.models_versions 
               where version=11 
               and name='task_model'
            ''')
        assert "is not found" in str(exc_info.value)

        # ----------------------------------------------------

        # retrain without all params
        self.run_sql(
            '''
                retrain proj.task_model
            '''
        )
        self.wait_predictor('proj', 'task_model', {'version': '4'})

        # ----------------------------------------------------

        # drop predictor and check model is deleted and no versions
        self.run_sql('drop predictor proj.task_model')
        ret = self.run_sql('select * from proj.models')
        assert len(ret) == 0

        # versions are also deleted
        ret = self.run_sql('select * from proj.models_versions')
        assert len(ret) == 0

    @patch('mindsdb.integrations.handlers.postgres_handler.Handler')
    def test_view(self, data_handler):
        df = pd.DataFrame([
            {'a': 1, 'b': dt.datetime(2020, 1, 1)},
            {'a': 2, 'b': dt.datetime(2020, 1, 2)},
            {'a': 1, 'b': dt.datetime(2020, 1, 3)},
        ])
        self.set_handler(data_handler, name='pg', tables={'tasks': df})

        self.run_sql('''
            create view mindsdb.vtasks (
                select * from pg.tasks where a=1
            )
        ''')

        # -- create model --
        self.run_sql(
            '''
                CREATE PREDICTOR mindsdb.task_model
                from mindsdb (select * from vtasks)
                PREDICT a
                using engine='dummy_ml'
            '''
        )
        self.wait_predictor('mindsdb', 'task_model')

        # check input to data handler
        assert data_handler().query.call_args[0][0].to_string() == 'SELECT * FROM tasks WHERE tasks.a = 1'

        # use model
        ret = self.run_sql('''
             SELECT m.*
               FROM mindsdb.vtasks as t
               JOIN mindsdb.task_model as m
        ''')

        assert len(ret) == 2
        assert ret.predicted[0] == 42


    def test_empty_df(self):
        # -- create model --
        self.run_sql(
            '''
                CREATE PREDICTOR mindsdb.task_model
                PREDICT a
                using engine='dummy_ml',
                join_learn_process=true
            '''
        )
        self.wait_predictor('mindsdb', 'task_model')

    @patch('mindsdb.integrations.handlers.postgres_handler.Handler')
    def test_complex_joins(self, data_handler):
        df1 = pd.DataFrame([
            {'a': 1, 'c': 1, 'b': dt.datetime(2020, 1, 1)},
            {'a': 2, 'c': 1, 'b': dt.datetime(2020, 1, 2)},
            {'a': 1, 'c': 3, 'b': dt.datetime(2020, 1, 3)},
            {'a': 3, 'c': 2, 'b': dt.datetime(2020, 1, 2)},
        ])
        df2 = pd.DataFrame([
            {'a': 6, 'c': 1},
            {'a': 4, 'c': 2},
            {'a': 2, 'c': 3},
        ])
        self.set_handler(data_handler, name='pg', tables={'tbl1': df1, 'tbl2': df2})

        self.run_sql(
            '''
                CREATE PREDICTOR mindsdb.pred
                PREDICT p
                using engine='dummy_ml',
                join_learn_process=true
            '''
        )

        self.run_sql('''
            create view mindsdb.view2 (
                select * from pg.tbl2 where a!=4
            )
        ''')

        # --- test join table-table-table ---
        ret = self.run_sql('''
            SELECT t1.a as t1a,  t3.a t3a
              FROM pg.tbl1 as t1
              JOIN pg.tbl2 as t2 on t1.c=t2.c
              LEFT JOIN pg.tbl1 as t3 on t2.a=t3.a
              where t1.a=1
        ''')

        # must be 2 rows
        assert len(ret) == 2

        # all t1.a values are 1
        assert list(ret.t1a) == [1, 1]

        # t3.a has 2 and None
        assert len(ret[ret.t3a == 2]) == 1
        assert len(ret[ret.t3a.isna()]) == 1

        # --- test join table-predictor-view ---

        ret = self.run_sql('''
            SELECT t1.a t1a, t3.a t3a, m.*
              FROM pg.tbl1 as t1
              JOIN mindsdb.pred m
              LEFT JOIN mindsdb.view2 as t3 on t1.c=t3.c
              where t1.a>1
        ''')

        # must be 2 rows
        assert len(ret) == 2

        # t1.a > 1
        assert ret[ret.t1a <= 1].empty

        # view: a!=4
        assert ret[ret.t3a == 4].empty

        # t3.a has 6 and None
        assert len(ret[ret.t3a == 6]) == 1
        assert len(ret[ret.t3a.isna()]) == 1

        # contents predicted values
        assert list(ret.predicted.unique()) == [42]

        # --- tests table-subselect-view ---

        ret = self.run_sql('''
            SELECT t1.a t1a,
                   t2.t1a t2t1a, t2.t3a t2t3a,
                   t3.c t3c, t3.a t3a
              FROM pg.tbl1 as t1
              JOIN ( 
                  SELECT t1.a as t1a,  t3.a t3a
                  FROM pg.tbl1 as t1
                  JOIN pg.tbl2 as t2 on t1.c=t2.c
                  LEFT JOIN pg.tbl1 as t3 on t2.a=t3.a
                  where t1.a=1
              ) t2 on t2.t3a = t1.a
              LEFT JOIN mindsdb.view2 as t3 on t1.c=t3.c
              where t1.a>1
        ''')

        # 1 row
        assert len(ret) == 1

        # check row values
        row = ret.iloc[0].to_dict()
        assert row['t1a'] == 2
        assert row['t2t3a'] == 2

        assert row['t2t1a'] == 1
        assert row['t3c'] == 1

        assert row['t3a'] == 6





