from enum import Enum


class EvmChain(Enum):
    """
    The various supported EVM-based chains.
    """

    ARBITRUM = ('arbitrum', '0x1111111111111111111111111111111111111111')
    # AVAX address on the c-chain.
    AVALANCHE_C = ('avalanche_c', '0xb31f66aa3c1e785363f0875a1b74e27b85fd66c7')
    BASE = ('base', '0x1111111111111111111111111111111111111111')
    BNB = ('bnb', '0xb8c77482e45f1f44de1745f52c74426c631bdd52')
    # Since Ethereum is a base coin rather than a token, it does not have a contract address like erc20 tokens, so we
    # create a sentinel address.
    ETHEREUM = ('ethereum', '0x1111111111111111111111111111111111111111')
    OPTIMISM = ('optimism', '0x1111111111111111111111111111111111111111')
    # Polygon networks use matic from polygon-pos chain.
    POLYGON = ('polygon', '0x0000000000000000000000000000000000001010')
    POLYGON_ZKEVM = ('polygon_zkevm', '0x0000000000000000000000000000000000001010')
    # TRON's TRX is a base coin in its blockchain without a contract address, therefore needs it own sentinel address.
    TRON = ('tron', '0x2222222222222222222222222222222222222222')
    ZKSYNC_ERA = ('zksync_era', '0x1111111111111111111111111111111111111111')
    # The stability chains are technically feeless, so we just use a sentinel address.
    STABILITY = ('stability', '0x1111111111111111111111111111111111111111')
    STABILITY_TESTNET = ('stability_testnet', '0x1111111111111111111111111111111111111111')

    def __new__(cls, *args, **kwds):
        obj = object.__new__(cls)
        obj._value_ = args[0]
        return obj

    def __init__(self, _: str, native_token_address: str):
        self._native_token_address = native_token_address

    @property
    def native_token_address(self) -> str:
        return self._native_token_address
