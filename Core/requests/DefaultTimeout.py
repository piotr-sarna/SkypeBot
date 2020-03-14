import requests
from requests.adapters import TimeoutSauce


class DefaultTimeout(TimeoutSauce):
    connect = None
    read = None

    def __init__(self, *args, **kwargs):
        if kwargs['connect'] is None:
            kwargs['connect'] = DefaultTimeout.connect
        if kwargs['read'] is None:
            kwargs['read'] = DefaultTimeout.read

        super(DefaultTimeout, self).__init__(*args, **kwargs)

    @staticmethod
    def set_as_default():
        requests.adapters.TimeoutSauce = DefaultTimeout
