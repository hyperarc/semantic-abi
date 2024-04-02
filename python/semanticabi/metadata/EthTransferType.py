from enum import Enum


class EthTransferType(Enum):

    # primary transactions
    PRIMARY = 'Primary'
    # internal transactions
    INTERNAL = 'Internal'
    # block rewards
    REWARD = 'Reward'
    # erc20, erc721, erc115 transfers
    ERC = 'Erc'
