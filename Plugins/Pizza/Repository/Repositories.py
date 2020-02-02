from collections import namedtuple

Repositories = namedtuple('Repositories', [
    'organizer',
    'order',
    'optional_order',
    'forced_order'
])
