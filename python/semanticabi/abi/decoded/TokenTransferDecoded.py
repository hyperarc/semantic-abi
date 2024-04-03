from __future__ import annotations

import math
from dataclasses import dataclass
from functools import cached_property
from typing import Literal, Optional, List, Dict

from eth_abi.exceptions import DecodingError

from semanticabi.abi.Abi import DecodedLog, Abi
from semanticabi.metadata.EthLog import EthLog
from semanticabi.metadata.EthTransferable import EthTransferable
from semanticabi.metadata.EthTokenType import EthTokenType
from semanticabi.metadata.EthTransferType import EthTransferType


@dataclass
class TokenTransferDecoded(EthTransferable):
    """
    Handles the edge cases of decoding transfers for Erc20, Erc721, and Erc1155.

    @author zuyezheng
    """

    # signatures that match token transfers
    SIGNATURES = {
        # Transfer(address,address,uint256)
        '0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef',
        # TransferSingle(address,address,address,uint256,uint256)
        '0xc3d58168c5ae7397731d063d5bbf3d657854427343f4c083240f7aacaa2d0f62',
        # TransferBatch(address,address,address,uint256[],uint256[])
        '0x4a39dc06d4c0dbc64b70af90fd698a233a518aa5d07e595d983b8c0526c8f7fb',

        # Depending on if it's a transfer or purchase, only one of these will be emitted (most of the times)
        # PunkTransfer(address,address,uint256)
        '0x05af636b70da6819000c49f85b21fa82081c632069bb626f30932034099107d8',
        # PunkBought(uint256,uint256,address,address) 
        '0x58e5d5a525e3b40bc15abaa38b5882678db1ee68befd2f60bafe3a7fd06db9e3'
    }

    @staticmethod
    def is_a(log: EthLog) -> bool:
        """ If the log is of one of the transfer topics. """
        return len(log['topics']) > 0 and log['topics'][0] in TokenTransferDecoded.SIGNATURES

    @staticmethod
    def try_decode(
        abi: Abi,
        log: EthLog,
        # The unique sequence number of this log entry within a collection of log entries being processed.
        log_i: int
    ) -> List[TokenTransferDecoded]:
        if not TokenTransferDecoded.is_a(log):
            return []

        try:
            if decoded_transfer := abi.decode_log(log):
                return TokenTransferDecoded.of(log, log_i, decoded_transfer)
        except DecodingError:
            # if we can't decode the transfer event
            pass

        # always return an empty list to avoid null handling
        return []

    @staticmethod
    def of(log: EthLog, log_i: int, decoded_log: DecodedLog) -> List[TokenTransferDecoded]:
        decoded = decoded_log.data.to_json()
        event_name = decoded_log.event.name

        def make(value: int, token_id: Optional[int], token_type: EthTokenType, internal_index: int | float):
            return TokenTransferDecoded(
                log,
                decoded,
                decoded['from'].lower(),
                decoded['to'].lower(),
                value,
                token_id,
                event_name,
                token_type,
                float(internal_index)
            )

        if event_name == 'Transfer':
            if decoded_log.event.extra['standard'] == 'Erc721':
                return [make(1, decoded['tokenId'], EthTokenType.ERC721, log_i)]
            else:
                return [make(decoded['value'], None, EthTokenType.ERC20, log_i)]
        elif event_name == 'TransferSingle':
            return [make(decoded['value'], decoded['id'], EthTokenType.ERC1155, log_i)]
        elif event_name == 'TransferBatch':
            # see HYPERARC-1385
            num_transfers = len(decoded['ids'])

            # Calculate the maximum padding we will need. So, for example, if there are 99 transfers,
            # we will get a padding value of 2. Since we start the subindex count at 1, this leaves room
            # for 0.01 ... 0.99
            padding = int(math.log10(num_transfers)) + 1

            def make_internal_index(i: int):
                sub_index = str(i + 1).rjust(padding, '0')
                return float(f'{log_i}.{sub_index}')

            return [
                make(
                    decoded['values'][id_i], id, EthTokenType.ERC1155, make_internal_index(id_i)
                ) for id_i, id in enumerate(decoded['ids'])
            ]
        elif event_name == 'PunkTransfer':
            return [make(1, decoded['punkIndex'], EthTokenType.CRYPTO_PUNKS, log_i)]
        elif event_name == 'PunkBought':
            return [TokenTransferDecoded(
                log,
                decoded,
                decoded['fromAddress'].lower(),
                decoded['toAddress'].lower(),
                1,
                decoded['punkIndex'],
                event_name,
                EthTokenType.CRYPTO_PUNKS,
                float(log_i)
            )]

    log: EthLog
    decoded: Dict[str, any]
    _from_address: str
    _to_address: str
    _value: int
    token_id: Optional[int]
    event_name: Literal['Transfer', 'TransferSingle', 'TransferBatch', 'PunkTransfer', 'PunkBought']
    token_type: EthTokenType
    internal_index: float

    @cached_property
    def contract_address(self) -> str:
        return self.log['address'].lower()

    @property
    def from_address(self) -> str:
        return self._from_address

    @property
    def to_address(self) -> str:
        return self._to_address

    @property
    def value(self) -> int:
        return self._value

    @property
    def transfer_type(self) -> EthTransferType:
        return EthTransferType.ERC

    @property
    def operator(self) -> str:
        """ Operator field specific to 1155. """
        return self.decoded['operator'].lower()

    def __contains__(self, key):
        return hasattr(self, key)

    def __getitem__(self, item):
        return getattr(self, item)
