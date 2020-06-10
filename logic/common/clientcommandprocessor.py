import logging

from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException

from logic.helpers.configuration import Configuration

logger = logging.getLogger( __name__ )
RPC_CONFIGURATION = Configuration.RPC_CONFIGURATION


def run_client_command( command, value_to_return, *command_arguments ):
    logger.info(
        f"Running command: {command}, with arguments: {command_arguments} "
        f"and getting value from result: {value_to_return}." )

    try:
        rpc = AuthServiceProxy(
            "http://" + RPC_CONFIGURATION[ "username" ] + ":" + RPC_CONFIGURATION[ "password" ] + "@"
            + RPC_CONFIGURATION[ "host" ] + ":" + RPC_CONFIGURATION[ "port" ] )

        rpc_function_to_call = getattr( rpc, command )

        result = rpc_function_to_call( *command_arguments )

        if value_to_return is None:
            return result
        else:
            return result[ value_to_return ]

    except JSONRPCException as e:
        logger.error( f"Failed to get a successful result for command: {command}. {e.message}" )
