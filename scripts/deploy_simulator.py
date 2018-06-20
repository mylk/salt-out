#!/usr/bin/python2

from __future__ import print_function

import random
import time

fixtures = [
    'empty_commands',
    'empty_dict',
    'empty_response',
    'no_commands',
    'not_json',
    'with_debug',
    'with_failure',
    'with_success'
]

for fixture in fixtures:
    with open('tests/fixtures/{}'.format(fixture)) as fp:
        print(fp.read())
    time.sleep(random.randint(1, 4))
