"""copyright (c) 2020 Beeflow Ltd.

Author Rafal Przetakowski <rafal.p@beeflow.co.uk>"""

from django.utils.translation import ugettext_lazy as _


def translate(msg) -> str:
    return str(_(msg))
