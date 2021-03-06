import os
import csv
import boto3
import json
from typing import Sequence

_FILE_NAME = os.getenv('FILE_NAME', 'Alexa笑点 - お題.csv')
_PROJECT_NAME = os.getenv('PROJECT_NAME', 'therefore-project')
_FILE_KEY = os.path.join(_PROJECT_NAME, _FILE_NAME)
_BUCKET_NAME = os.getenv('BUCKET_NAME', '')
_SKILL_JSON_PATH = os.getenv('SKILL_JSON', 'skill.json')
_SKILL_NAME = os.getenv('SKILL_NAME', 'SKILL_NAME')


def get_skill_name(locale: str = 'ja-JP') -> str:
    """
    取得の優先順位
    - skill.json "manifest.publishingInformation.locales.ja-JP.name"
    - environment valuable from "lambda"
    - from python
    Args:
        locale: when get from skill.json
    """
    if os.path.exists(_SKILL_JSON_PATH):
        with open(_SKILL_JSON_PATH, 'r') as skill_json:
            json_loaded = json.load(skill_json)
            return json_loaded['manifest']['publishingInformation']['locales'][
                locale]['name']
    return _SKILL_NAME


def read_file_from_s3(bucket_name, file_path):
    s3 = boto3.resource('s3')
    obj = s3.Object(bucket_name, file_path)
    body = obj.get()['Body'].read()
    decoded: str = body.decode('utf-8')
    new_lines = decoded.split('\r\n')
    return [row.split(',') for row in new_lines]


def read_file_from_lambda(file_name: str,
                          full_path: str = '') -> Sequence[Sequence[str]]:
    open_file_path = full_path if full_path \
        else os.path.join(os.getcwd(), file_name)
    with open(open_file_path) as csv_file:
        spam_reader = csv.reader(csv_file, delimiter=',', quotechar='|')
        return [row for row in spam_reader]


def read_file(target: str = '') -> Sequence[Sequence[str]]:
    if target == 's3':
        return read_file_from_s3(_BUCKET_NAME, _FILE_KEY)
    return read_file_from_lambda(_FILE_NAME)


def get_speech_text(_, text_keys):
    if isinstance(text_keys, str):
        text_keys = [text_keys]
    # text keys list to response text
    speech_texts = [_.get(text_key, text_key)
                    for text_key in text_keys]
    separated_value = _.get('SEPARATED_VALUE', '.')
    return f'{separated_value}'.join(speech_texts)


class Singleton:
    _unique_instance = None

    def __new__(cls):
        raise NotImplementedError('Cannot initialize via Constructor')

    @classmethod
    def __internal_new__(cls):
        return super().__new__(cls)

    @classmethod
    def get_instance(cls):
        if not cls._unique_instance:
            cls._unique_instance = cls.__internal_new__()
        return cls._unique_instance
