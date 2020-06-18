import logging

from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException

logger = logging.getLogger( __name__ )


def run_client_command( rpc_configuration, command, value_to_return, *command_arguments ):
    logger.info(
        f"Running command: {command}, with arguments: {command_arguments} "
        f"and getting value from result: {value_to_return}." )

    try:
        rpc = AuthServiceProxy(
            "http://" + rpc_configuration[ "username" ] + ":" + rpc_configuration[ "password" ] + "@"
            + rpc_configuration[ "host" ] + ":" + rpc_configuration[ "port" ] )

        rpc_function_to_call = getattr( rpc, command )

        result = rpc_function_to_call( *command_arguments )

        if value_to_return is None:
            return result
        else:
            return result[ value_to_return ]

    except JSONRPCException as e:
        raise Exception( f"Failed to get a successful result for command: {command}. {e.message}", e )
