"""copyright (c) 2020 Beeflow Ltd.

Author Rafal Przetakowski <rafal.p@beeflow.co.uk>"""
import base64
import wave
from typing import Dict
import pickle
from pylab import *

from rabbit_queues.management.commands.db_queue_managers.abstract_manager import AbstractManager
from rest_api.models import WaveFile
from utils.file_uploader.uploader import Uploader
from vl_server import settings


class WaveParser(AbstractManager):
    def execute(self, data: Dict):
        file_id: str = data.get('id')

        try:
            wave_data = WaveFile.objects.get(id=file_id)
        except WaveFile.DoesNotExist:
            return

        print(f'{wave_data.id}')

        spf = wave.open(f'{settings.UPLOAD_DIR}/waves/{wave_data.id}.wav', 'r')
        sound_info = fromstring(spf.readframes(-1), 'Int16')
        framerate = spf.getframerate()

        np_bytes = pickle.dumps(sound_info)
        np_base64 = base64.b64encode(np_bytes)

        wave_data.channels = spf.getnchannels()
        wave_data.sampwidth = spf.getsampwidth()
        wave_data.framerate = framerate
        wave_data.nframes = spf.getnframes()
        wave_data.audiogram = np_base64
        wave_data.status = WaveFile.Status.DONE

        wave_data.save()

        Uploader().delete(f'/waves/{wave_data.id}.wav')
