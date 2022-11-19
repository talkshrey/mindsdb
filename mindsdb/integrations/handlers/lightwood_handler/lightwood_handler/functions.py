import os
import traceback
import tempfile
from pathlib import Path
import json
import requests
from datetime import datetime
import dataclasses

import pandas as pd
from pandas.core.frame import DataFrame
import lightwood
from lightwood.api.types import ProblemDefinition, JsonAI

import mindsdb.interfaces.storage.db as db
from mindsdb.interfaces.storage import db
from mindsdb.utilities.functions import mark_process
from mindsdb.utilities import log
from mindsdb.integrations.libs.const import PREDICTOR_STATUS
from mindsdb.integrations.utilities.utils import format_exception_error
from mindsdb.interfaces.model.functions import (
    get_model_record,
    get_model_records
)
from mindsdb.interfaces.storage.fs import FileStorage, RESOURCE_GROUP
from mindsdb.interfaces.storage.json import get_json_storage

from .utils import rep_recur, brack_to_mod, unpack_jsonai_old_args


def create_learn_mark():
    if os.name == 'posix':
        p = Path(tempfile.gettempdir()).joinpath('mindsdb/learn_processes/')
        p.mkdir(parents=True, exist_ok=True)
        p.joinpath(f'{os.getpid()}').touch()


def delete_learn_mark():
    if os.name == 'posix':
        p = Path(tempfile.gettempdir()).joinpath('mindsdb/learn_processes/').joinpath(f'{os.getpid()}')
        if p.exists():
            p.unlink()


@mark_process(name='learn')
def run_generate(df: DataFrame, predictor_id: int, args: dict = None):
    json_ai_override = args.pop('using', {})

    if 'timeseries_settings' in args:
        for tss_key in [f.name for f in dataclasses.fields(lightwood.api.TimeseriesSettings)]:
            k = f'timeseries_settings.{tss_key}'
            if k in json_ai_override:
                args['timeseries_settings'][tss_key] = json_ai_override.pop(k)

    problem_definition = lightwood.ProblemDefinition.from_dict(args)
    json_ai = lightwood.json_ai_from_problem(df, problem_definition)
    json_ai = json_ai.to_dict()
    unpack_jsonai_old_args(json_ai_override)
    json_ai_override = brack_to_mod(json_ai_override)
    rep_recur(json_ai, json_ai_override)
    json_ai = JsonAI.from_dict(json_ai)

    code = lightwood.code_from_json_ai(json_ai)

    predictor_record = db.Predictor.query.with_for_update().get(predictor_id)
    predictor_record.code = code
    db.session.commit()

    json_storage = get_json_storage(
        resource_id=predictor_id,
        company_id=predictor_record.company_id
    )
    json_storage.set('json_ai', json_ai.to_dict())


@mark_process(name='learn')
def run_fit(predictor_id: int, df: pd.DataFrame, company_id: int) -> None:
    try:
        predictor_record = db.Predictor.query.with_for_update().get(predictor_id)
        assert predictor_record is not None

        predictor_record.data = {'training_log': 'training'}
        predictor_record.status = PREDICTOR_STATUS.TRAINING
        db.session.commit()
        predictor: lightwood.PredictorInterface = lightwood.predictor_from_code(predictor_record.code)
        predictor.learn(df)

        db.session.refresh(predictor_record)

        fs = FileStorage(
            resource_group=RESOURCE_GROUP.PREDICTOR,
            resource_id=predictor_id,
            company_id=company_id,
            sync=True
        )
        predictor.save(fs.folder_path / fs.folder_name)
        fs.push()

        predictor_record.data = predictor.model_analysis.to_dict()

        # getting training time for each tried model. it is possible to do
        # after training only
        fit_mixers = list(predictor.runtime_log[x] for x in predictor.runtime_log
                          if isinstance(x, tuple) and x[0] == "fit_mixer")
        submodel_data = predictor_record.data.get("submodel_data", [])
        # add training time to other mixers info
        if submodel_data and fit_mixers and len(submodel_data) == len(fit_mixers):
            for i, tr_time in enumerate(fit_mixers):
                submodel_data[i]["training_time"] = tr_time
        predictor_record.data["submodel_data"] = submodel_data

        predictor_record.dtype_dict = predictor.dtype_dict
        db.session.commit()
    except Exception as e:
        db.session.refresh(predictor_record)
        predictor_record.data = {'error': f'{traceback.format_exc()}\nMain error: {e}'}
        db.session.commit()
        raise e


@mark_process(name='learn')
def run_learn_remote(df: DataFrame, predictor_id: int) -> None:
    try:
        serialized_df = json.dumps(df.to_dict())
        predictor_record = db.Predictor.query.with_for_update().get(predictor_id)
        resp = requests.post(predictor_record.data['train_url'],
                             json={'df': serialized_df, 'target': predictor_record.to_predict[0]})

        assert resp.status_code == 200
        predictor_record.data['status'] = 'complete'
    except Exception:
        predictor_record.data['status'] = 'error'
        predictor_record.data['error'] = str(resp.text)

    db.session.commit()


@mark_process(name='learn')
def run_learn(df: DataFrame, args: dict, model_storage) -> None:
    # FIXME
    predictor_id = model_storage.predictor_id
    company_id = model_storage.company_id

    predictor_record = db.Predictor.query.with_for_update().get(predictor_id)
    predictor_record.training_start_at = datetime.now()
    db.session.commit()

    run_generate(df, predictor_id, args)
    run_fit(predictor_id, df, company_id)

    predictor_record.status = PREDICTOR_STATUS.COMPLETE
    predictor_record.training_stop_at = datetime.now()
    db.session.commit()


def run_adjust(name, db_name, from_data, datasource_id, company_id):
    # @TODO: Actually implement this
    return 0


@mark_process(name='learn')
def run_update(predictor_id: int, df: DataFrame, company_id: int):
    try:
        predictor_record = db.Predictor.query.filter_by(id=predictor_id).first()

        problem_definition = predictor_record.learn_args
        problem_definition['target'] = predictor_record.to_predict[0]

        if 'join_learn_process' in problem_definition:
            del problem_definition['join_learn_process']

        if 'stop_training_in_x_seconds' in problem_definition:
            problem_definition['time_aim'] = problem_definition['stop_training_in_x_seconds']

        json_ai = lightwood.json_ai_from_problem(df, problem_definition)

        # TODO move it to ModelStorage (don't work with database directly)
        predictor_record.code = lightwood.code_from_json_ai(json_ai)
        predictor_record.data = {'training_log': 'training'}
        predictor_record.training_start_at = datetime.now()
        predictor_record.status = PREDICTOR_STATUS.TRAINING
        db.session.commit()

        json_storage = get_json_storage(
            resource_id=predictor_id,
            company_id=predictor_record.company_id
        )
        json_storage.set('json_ai', json_ai.to_dict())

        predictor: lightwood.PredictorInterface = lightwood.predictor_from_code(predictor_record.code)
        predictor.learn(df)

        fs = FileStorage(
            resource_group=RESOURCE_GROUP.PREDICTOR,
            resource_id=predictor_id,
            company_id=company_id,
            sync=True
        )
        predictor.save(fs.folder_path / fs.folder_name)
        fs.push()

        predictor_record.data = predictor.model_analysis.to_dict()
        predictor_record.update_status = 'up_to_date'
        predictor_record.dtype_dict = predictor.dtype_dict

        predictor_record.status = PREDICTOR_STATUS.COMPLETE
        predictor_record.training_stop_at = datetime.now()
        db.session.commit()

        predictor_records = get_model_records(
            active=None,
            name=predictor_record.name,
            company_id=company_id
        )
        predictor_records = [
            x for x in predictor_records
            if x.training_stop_at is not None
        ]
        predictor_records.sort(key=lambda x: x.training_stop_at)
        for record in predictor_records:
            record.active = False
        predictor_records[-1].active = True
        db.session.commit()
    except Exception as e:
        log.logger.error(e)
        predictor_record = db.Predictor.query.with_for_update().get(predictor_id)
        print(traceback.format_exc())

        error_message = format_exception_error(e)

        predictor_record.data = {"error": error_message}

        # old_predictor_record.update_status = 'update_failed'   # TODO
        db.session.commit()

    if predictor_record.training_stop_at is None:
        predictor_record.training_stop_at = datetime.now()
        db.session.commit()
