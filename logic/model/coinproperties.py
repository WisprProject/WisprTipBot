from typing import Optional

from logic.model.blockchainexplorerconfiguration import BlockchainExplorerConfiguration
from logic.model.rpcconfiguration import RpcConfiguration


class CoinProperties:
    def __init__( self, coin_properties ):
        self.name: str = coin_properties[ 'NAME' ]
        self.ticker: str = coin_properties[ 'TICKER' ]
        self.minimum_withdraw: float = coin_properties[ 'MINIMUM_WITHDRAW' ]
        self.withdrawal_fee: float = coin_properties[ 'WITHDRAWAL_FEE' ]
        self.rpc_configuration: RpcConfiguration = RpcConfiguration( coin_properties[ 'RPC_CONFIGURATION' ] )
        self.blockchain_explorer: Optional[ None, BlockchainExplorerConfiguration ] = coin_properties[ 'BLOCKCHAIN_EXPLORER' ]
