"""copyright (c) 2020 Beeflow Ltd.

Author Rafal Przetakowski <rafal.p@beeflow.co.uk>"""

import abc


class AbstractManager(abc.ABC):
    @abc.abstractmethod
    def execute(self, data):
        pass
