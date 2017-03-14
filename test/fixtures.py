import os
import pytest
import json
from retrying import retry
from .constants import version, image, container_name
from subprocess import run, PIPE


@pytest.fixture()
def logstash(Process, Command, LocalCommand):
    class Logstash:
        def __init__(self):
            self.name = container_name
            self.process = Process.get(comm='java')

        def start(self, args=None):
            if args:
                arg_array = args.split(' ')
            else:
                arg_array = []
            run(['docker', 'run', '-d', '--name', self.name] + arg_array + [image])

        def stop(self):
            run(['docker', 'kill', self.name])
            run(['docker', 'rm', self.name])

        def restart(self, args=None):
            self.stop()
            self.start(args)

        @retry(wait_fixed=1000, stop_max_attempt_number=60)
        def get_node_info(self):
            """Return the contents of Logstash's node info API.

            It retries for a while, since Logstash may still be coming up.
            Refer: https://www.elastic.co/guide/en/logstash/master/node-info-api.html
            """
            return json.loads(Command.check_output('curl -s http://localhost:9600/_node'))

    return Logstash()
