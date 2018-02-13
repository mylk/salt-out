#!/usr/bin/python2

from __future__ import print_function
import json
import sys
import pprint


class Colors:
    OK = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'


class MinionParser:
    STATUS_FAIL = '{}[ FAIL ]{}'.format(Colors.FAIL, Colors.END)
    STATUS_OK = '{}[  OK  ]{}'.format(Colors.OK, Colors.END)

    def read_stdin(self):
        for line in sys.stdin:
            if self.is_json(line):
                line_json = json.loads(line)
                result = self.parse_response(line_json)
                self.print_result(result)
            elif line.startswith('[DEBUG]') or line.startswith('Executing job with jid'):
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
                # with "requisite failed"
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
        print('- {}: {} ({} min)'.format(result['host'], status, duration_minutes))

        for error in result['errors']:
            print('{}  Reason:\n  {}\n  {}{}\n'.format(Colors.FAIL, error['command'], error['message'], Colors.END))

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
