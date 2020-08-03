class RpcConfiguration:
    def __init__( self, rpc_configuration ):
        self.username: str = rpc_configuration[ 'username' ]
        self.password: str = rpc_configuration[ 'password' ]
        self.host: str = rpc_configuration[ 'host' ]
        self.port: int = rpc_configuration[ 'port' ]
