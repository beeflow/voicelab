import base64
import json
import pickle
import os

from typing import Dict

from django.core.exceptions import ValidationError
from django.core.paginator import Paginator
from django.http import HttpRequest
from django.shortcuts import resolve_url
from pylab import *
from requests import Response
from rest_framework import views, status
from rest_framework.response import Response

from rest_api.models import WaveFile
from utils.file_uploader.uploader import Uploader
from utils.rabbit_mq.queue import UseRabbitQueue
from vl_server import settings


class FileUploadView(views.APIView):
    @staticmethod
    def post(request):
        wave_file = request.FILES['file']
        db_file = WaveFile.objects.create(filename=wave_file.name)
        Uploader().upload_in_memory_uploaded_file(wave_file, 'waves', f'{db_file.id}.wav')

        with UseRabbitQueue(settings.RABBITMQ_DATABASE_QUEUE) as queue:
            queue.basic_publish(
                routing_key=settings.RABBITMQ_DATABASE_QUEUE,
                body=json.dumps({'queue_engine': 'wave_parser', 'data': {'id': str(db_file.id)}})
            )

        return Response({'id': str(db_file.id)}, status=status.HTTP_201_CREATED)


class TasksView(views.APIView):
    _filename = '/{upload_dir}/{filename}.png'

    _statuses = {
        WaveFile.Status.IN_QUEUE: 'UNDETERMINED',
        WaveFile.Status.IN_PROGRESS: 'INPROGRESS',
        WaveFile.Status.DONE: 'SUCCESS'
    }

    def get(self, request, page: int = 1):
        items_per_page: int = 10
        files = WaveFile.objects.all()
        paginator = Paginator(files, items_per_page)
        max_pages: int = paginator.num_pages

        if max_pages < page:
            return Response(
                status=status.HTTP_404_NOT_FOUND,
                headers={'Content-Type': 'application/api-problem+json'}
            )

        result: Dict = {'data': [], 'links': {}}
        requested_page = paginator.get_page(page)

        for element in requested_page.object_list:
            job: Dict = {
                'job': {
                    '@uri': resolve_url('get_task', task_id=str(element.id)),
                    'id': str(element.id),
                    'name': element.filename,
                    'job-status': self._statuses.get(element.status),
                }
            }

            filename = self._filename.format(upload_dir=settings.UPLOAD_DIR, filename=str(element.id))

            if os.path.exists(filename):
                job['job']['@file'] = self._filename

            result['data'].append(job)

        if requested_page.has_previous():
            result['links'].update({'previous': resolve_url('get_tasks', page=requested_page.previous_page_number())})

        result['links'].update({'self': resolve_url('get_tasks', page=page)})

        if requested_page.has_next():
            result['links'].update({'next': resolve_url('get_tasks', page=requested_page.next_page_number())})

        result['links'].update({'meta': {'count': paginator.num_pages}})

        return Response(result)


class TaskView(views.APIView):
    _filename = '/{upload_dir}/{filename}.png'

    _statuses = {
        WaveFile.Status.IN_QUEUE: 'UNDETERMINED',
        WaveFile.Status.IN_PROGRESS: 'INPROGRESS',
        WaveFile.Status.DONE: 'SUCCESS'
    }

    def get(self, request: HttpRequest, task_id: str):
        try:
            wave_data = WaveFile.objects.get(id=task_id)
            self._filename = self._filename.format(upload_dir=settings.UPLOAD_DIR, filename=task_id)
        except (WaveFile.DoesNotExist, ValidationError):
            return Response(
                status=status.HTTP_404_NOT_FOUND,
                headers={'Content-Type': 'application/api-problem+json'}
            )

        result: Dict = {
            'job': {
                '@uri': resolve_url('get_task', task_id=task_id),
                'id': task_id,
                'name': wave_data.filename,
                'job-status': self._statuses.get(wave_data.status),
            }
        }

        if os.path.exists(self._filename):
            result['job']['@file'] = self._filename

        return Response(result)


class WaveformView(views.APIView):
    _filename = '{upload_dir}/{filename}.png'

    def get(self, request: HttpRequest, id: str):
        try:
            wave_data = WaveFile.objects.get(id=id)
            self._filename = self._filename.format(upload_dir=settings.UPLOAD_DIR, filename=str(wave_data.id))
        except (WaveFile.DoesNotExist, ValidationError):
            return Response(
                status=status.HTTP_404_NOT_FOUND,
                headers={'Content-Type': 'application/api-problem+json'}
            )

        if os.path.exists(self._filename):
            return Response({'@file': self._filename})

        if wave_data.audiogram:
            self._save_audiogram_file(wave_data)
            return Response({'@file': self._filename})

        return Response(
            {'task': {'href': resolve_url('get_task', task_id=str(wave_data.id)), 'id': str(wave_data.id)}},
            status=status.HTTP_202_ACCEPTED,
        )

    def _save_audiogram_file(self, wave_data: WaveFile) -> None:
        np_bytes = base64.b64decode(wave_data.audiogram)
        sound_info = pickle.loads(np_bytes)

        subplot(211)
        plot(sound_info)
        title('Wave from and spectrogram of %s' % wave_data.filename)

        subplot(212)
        specgram(sound_info, Fs=wave_data.framerate, scale_by_freq=True, sides='default')

        savefig(self._filename)
