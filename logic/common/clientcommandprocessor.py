import json
import subprocess

from logic.helpers.configuration import Configuration

CLI_LOCATION = Configuration.CLI_LOCATION


def run_client_command( command_attributes, value_to_return=None ):
    try:
        call = subprocess.Popen( [ CLI_LOCATION ] + command_attributes, stdout=subprocess.PIPE )
        result, _ = call.communicate()
        if value_to_return is None:
            return str( result.decode( "utf-8" ) ).strip()
        else:
            data = json.loads( result )
            return data[ value_to_return ]

    except ValueError:
        raise ValueError
