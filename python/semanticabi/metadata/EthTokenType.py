from enum import Enum


class EthTokenType(Enum):

    ETH = ('Eth', False)
    ERC20 = ('Erc20', False)
    ERC721 = ('Erc721', True)
    ERC1155 = ('Erc1155', True)
    CRYPTO_PUNKS = ('CryptoPunks', True)

    code: str
    is_nft: bool

    def __init__(self, code: str, is_nft: bool):
        self.code = code
        self.is_nft = is_nft
