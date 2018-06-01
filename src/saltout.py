#!/usr/bin/python2

from __future__ import print_function

import argparse
import json
import sys
import time


class Colors:
    OK = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'


class MinionParser:
    NO_COLORS = False
    RAW_DIR = None
    RAW_FILE = None

    STATUS_OK = 'OK'
    STATUS_WARNING = 'WARNING'
    STATUS_FAIL = 'FAIL'

    def __init__(self):
        arg_parser = argparse.ArgumentParser()
        arg_parser.add_argument('--no-colors', action='store_true')
        arg_parser.add_argument('-r', '--raw-dir', action='store', default=None)
        args = arg_parser.parse_args()
        self.NO_COLORS = args.no_colors
        self.RAW_DIR = args.raw_dir

        if self.RAW_DIR:
            self.RAW_FILE = '{}/saltout_{}.out'.format(self.RAW_DIR, time.strftime('%Y%m%d%H%M%S'))

    def read_stdin(self):
        has_errors = False
        for line in sys.stdin:
            self.save_raw(line, self.RAW_FILE)

            if self.is_json(line):
                line_json = json.loads(line)
                result = self.parse_response(line_json)
                self.print_result(result)

                if len(result['errors']) > 0:
                    has_errors = True
            elif line.startswith('[DEBUG') or line.startswith('[WARNING') or line.startswith('Executing job with jid'):
                print(line, end='')

        if has_errors:
            exit(1)

    @staticmethod
    def parse_response(response):
        empty_response = False
        success = True
        duration = 0
        errors = []

        # elements in response are not ordered.
        # so, loop to detect the commands element
        elements = response.items()
        for key, value in elements:
            if isinstance(value, dict):
                host = key
                commands = value
                empty_response = (len(value) == 0)
                break

        if empty_response:
            success = False
            errors.append({
                'command': "NO RESPONSE FROM {}".format(host),
                'message': ''
            })

        else:
            for command, details in commands.items():
                if not isinstance(details, dict):
                    continue

                if not details['result']:
                    success = False

                    name = details['name'] if 'name' in details else command
                    message = details['changes']['stderr'] if 'stderr' in details['changes'] else details['comment']

                    errors.append({
                        'command': name,
                        'message': message
                    })
                    # following commands will always fail,
                    # with "prerequisite failed"
                    break
                duration += details['duration'] if details['duration'] else 0

        return {
            'host': host,
            'success': success,
            'duration': duration,
            'errors': errors
        }

    @staticmethod
    def save_raw(data, path):
        if path is None:
            return

        raw_file = open(path, 'a+')
        raw_file.write(data)
        raw_file.close()

    def print_result(self, result):
        status = self.STATUS_FAIL
        if result['success']:
            status = self.STATUS_OK

        duration_minutes = round((result['duration'] / (1000 * 60)), 1)
        output = '{} ({} min)'.format(result['host'], duration_minutes)

        for error in result['errors']:
            output += '\nReason:\n{}\n{}\n'.format(error['command'], error['message'])

        self.log(output, status)

    def log(self, message, message_type):
        color_start = getattr(Colors, message_type)
        color_end = Colors.END
        if self.NO_COLORS:
            color_start = ''
            color_end = ''

        if message_type == self.STATUS_OK:
            message_prefix = '{}[  OK  ]{}'
        elif message_type == self.STATUS_WARNING:
            message_prefix = '{}[ FAIL ]{}'
        elif message_type == self.STATUS_FAIL:
            message_prefix = '{}[ FAIL ]{}'

        message_prefix = message_prefix.format(color_start, color_end)
        print('{} {}'.format(message_prefix, message))

    @staticmethod
    def is_json(data):
        try:
            data_json = json.loads(data)
        except ValueError as e:
            return False
        return True


if __name__ == '__main__':
    parser = MinionParser()
    if parser.RAW_FILE:
        print('Saving raw input to {}\n'.format(parser.RAW_FILE))

    parser.read_stdin()
