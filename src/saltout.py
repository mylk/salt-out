#!/usr/bin/python2

from __future__ import print_function
import json
import sys
import pprint
import argparse


class Colors:
    OK = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'


class MinionParser:
    NO_COLORS = False
    STATUS_OK = 'OK'
    STATUS_WARNING = 'WARNING'
    STATUS_FAIL = 'FAIL'

    def __init__(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('--no-colors', action='store_true')
        args = parser.parse_args()
        self.NO_COLORS = args.no_colors

    def read_stdin(self):
        for line in sys.stdin:
            if self.is_json(line):
                line_json = json.loads(line)
                result = self.parse_response(line_json)
                self.print_result(result)
            elif line.startswith('[DEBUG') or line.startswith('[WARNING') or line.startswith('Executing job with jid'):
                print(line, end='')

    @staticmethod
    def parse_response(response):
        success = True
        duration = 0
        errors = []

        # elements in resonse are not ordered.
        # so, loop to detect the commands element
        elements = response.items()
        for key, value in elements:
            if isinstance(value, dict):
                host = key
                commands = value
                break

        for name, details in commands.items():
            if not isinstance(details, dict):
                continue
            duration += details['duration']
            if not details['result']:
                success = False
                errors.append({
                    'command': details['name'],
                    'message': details['changes']['stderr']
                })
                # following commands will always fail,
                # with "prerequisite failed"
                break

        return {
            'host': host,
            'success': success,
            'duration': duration,
            'errors': errors
        }

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
        color_start = getattr(Colors,message_type)
        color_end = Colors.END
        if self.NO_COLORS == True:
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
    parser.read_stdin()

