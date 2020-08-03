class BlockchainExplorerConfiguration:
    def __init__( self, explorerConfiguration: dict ):
        self.url: str = explorerConfiguration[ 'url' ]
        self.tx_prefix: str = explorerConfiguration[ 'tx_prefix' ]
        self.address_prefix: str = explorerConfiguration[ 'address_prefix' ]
