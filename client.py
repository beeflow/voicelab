#!/usr/bin/env python
"""copyright (c) 2020 Beeflow Ltd.

Author Rafal Przetakowski <rafal.p@beeflow.co.uk>"""
import argparse
import json
from typing import Dict

import requests

BASE_URL = 'http://127.0.0.1:8000'


def upload_file(filename: str) -> Dict:
    file_data: Dict = {'file': open(filename, 'rb')}
    response = requests.post(url=f'{BASE_URL}/api/v1/upload', files=file_data)

    if response.status_code == 400:
        return {'error': 'Bad request'}

    return json.loads(response.content)


def get_task(task_id: str) -> Dict:
    response = requests.get(f'{BASE_URL}/api/v1/tasks/{task_id}')

    if response.status_code == 200:
        return json.loads(response.content)

    return {'error': 'Task not found'}


def get_tasks(page: int) -> Dict:
    response = requests.get(f'{BASE_URL}/api/v1/tasks/{page}')

    if response.status_code == 200:
        return json.loads(response.content)

    return {'error': 'Page not found'}


def save_file(task_id: str) -> Dict:
    response = requests.get(f'{BASE_URL}/api/v1/waveform/{task_id}')

    if response.status_code == 404:
        return {'error': 'Task not found'}

    response_data = json.loads(response.content)
    remote_filename: str = response_data.get('@file')

    if not remote_filename:
        response = requests.get(f'{BASE_URL}{response_data.get("task").get("href")}')
        job_status: str = json.loads(response.content).get("job").get("job-status")
        return {'error': f'File does not exists. Task status: {job_status}'}

    local_filename: str = remote_filename.split('/')[-1]

    with open(local_filename, 'wb') as local_file:
        local_file.write(requests.get(f'{BASE_URL}/{remote_filename}').content)

    return {'success': f'Waveform saved as {local_filename}'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='VL Waveform client.')

    parser.add_argument('task', metavar='TASK_ID', nargs='?', type=str,
                        help='task id - needed only task info and saving waveform file')

    # tricky only for help - page number is taken as task ;)
    parser.add_argument('page', metavar='PAGE', nargs='?', type=int, help='page number - needed only tasks list')

    # tricky only for help - filename is taken as task ;)
    parser.add_argument('filename', metavar='FILENAME', nargs='?', type=int, help='filename to upload')

    parser.add_argument('--get-task', dest='accumulate', action='store_const', required=False,
                        const=get_task, help='Takes task information. Task id is required')
    parser.add_argument('--get-tasks-list', dest='accumulate', action='store_const', required=False,
                        const=get_tasks, help='Takes tasks list. Page number is required')
    parser.add_argument('--get-waveform', dest='accumulate', action='store_const', required=False,
                        const=save_file, help='Takes waveform file and saves locally. ask id is required')
    parser.add_argument('--upload', dest='accumulate', action='store_const', required=False,
                        const=upload_file, help='Uploads wave file. Filename is required')

    args = parser.parse_args()

    if not args.task:
        parser.print_help()
        exit(0)

    print(args.accumulate(args.task))
