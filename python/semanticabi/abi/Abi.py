from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Dict, List, Optional

from web3 import Web3
from web3.contract import Contract

from semanticabi.metadata.EthTraces import EthTrace
from semanticabi.abi.Decoded import DecodedTuple
from semanticabi.abi.item.AbiItem import AbiEvent, AbiFunction


class Abi:
    """
    Load an ABI for parsing.

    @author zuyezheng
    """

    @staticmethod
    def from_enriched(location: str) -> Abi:
        """
        Parse an enriched JSON file with a separate metadata section.
        """
        with open(location, 'r') as json_file:
            enriched = json.load(json_file)

        return Abi(enriched['metadata']['name'], enriched['abi'])


    @staticmethod
    def from_json(name: str, location: str) -> Abi:
        """
        Parse an ABI json file to use for decoding.
        """
        with open(location, 'r') as json_file:
            abi_json = json.load(json_file)

        return Abi(name, abi_json)

    name: str
    abi: List[Dict[str, any]]

    # events and functions by their hashes
    events: Dict[str, List[AbiEvent]]
    functions: Dict[str, AbiFunction]

    def __init__(
        self,
        # name of the ABI if we need to identify it later
        name: str,
        abi: List[Dict[str, any]]
    ):
        self.name = name
        self.abi = abi

        self.events = {}
        self.functions = {}
        for item in self.abi:
            # skip if there are no inputs
            if 'inputs' not in item:
                continue

            if item['type'] == 'event':
                event = AbiEvent.from_json(item)

                # handle event hashes that collide
                if event.hash not in self.events:
                    self.events[event.hash] = []
                self.events[event.hash].append(event)
            elif item['type'] == 'function':
                function = AbiFunction.from_json(item)

                self.functions[function.hash] = function

    def with_client(self, address: str, client: Web3) -> AbiWithClient:
        return AbiWithClient(self, address, client)

    def function_by_name(self, name: str) -> Optional[AbiFunction]:
        """ Find a function by name. """
        for function in self.functions.values():
            if function.name == name:
                return function

        return None

    def decode_log(self, log: Dict[str, any]) -> Optional[DecodedLog]:
        if len(log['topics']) == 0:
            return None

        # first topic is always the signature hash
        event_signature_hash = log['topics'][0][2:]

        # if more than 1 event, find the right one
        events = self.events.get(event_signature_hash)
        event = None
        if events is not None:
            if len(events) == 1:
                event = events[0]
            elif len(events) > 1:
                for possible in events:
                    if possible.is_of(log):
                        event = possible
                        break

        if event is None:
            return None

        return DecodedLog(
            event,
            event.decode(log)
        )

    def decode_trace(self, trace: EthTrace) -> Optional[DecodedTrace]:
        # get the function by its signature excluding the 0x
        function = self.functions.get(trace.signature[2:])

        if function is None:
            return None

        output = trace.output
        output_decoded = None
        # output is only valid and non-empty if more than 2 characters since the first 2 are 0x
        if output is not None and len(output) > 2:
            output_decoded = function.decode_output(output)

        return DecodedTrace(
            function,
            function.decode(trace.input),
            output_decoded
        )

    def print(self):
        """ Print a pretty version of the ABI. """
        lines = []

        lines.append('Events')
        for event_hash in self.events:
            for event in self.events[event_hash]:
                lines.append(f'0x{event_hash} {event.signature}')

        lines.append('')
        lines.append('Functions')
        for function_hash in self.functions:
            function = self.functions[function_hash]
            lines.append(f'0x{function_hash} {function.signature}')

        print('\n'.join(lines))

    def decode_and_print(self, transaction: Dict[str, any]):
        """ Decode logs and traces from a transaction response and pretty print them. """
        lines = []

        lines.append('Events')
        for log in transaction['logs']:
            if decoded_result := self.decode_log(log):
                lines.append(f'{decoded_result.event.name} {decoded_result.event.extra}')
                lines.append(json.dumps(decoded_result.data.to_json(), indent=4))

        lines.append('')
        lines.append('Functions')
        # we might not have traces
        if 'traces' in transaction:
            for trace in transaction['traces']:
                if decoded_result := self.decode_trace(trace):
                    function, decoded = decoded_result
                    lines.append(function.name)
                    lines.append(json.dumps(decoded.to_json(), indent=4))

        print('\n'.join(lines))


class AbiWithClient:

    abi: Abi
    contract: Contract

    def __init__(self, abi: Abi, address: str, client: Web3):
        self.abi = abi
        self.contract = client.eth.contract(
            address=Web3.to_checksum_address(address),
            abi=abi.abi
        )

    def call(self, function: str, *args, block_identifier: int | str = 'latest') -> DecodedTuple:
        return DecodedTuple.from_parameters_and_values(
            None,
            self.abi.function_by_name(function).outputs.parameters(),
            self.contract.get_function_by_name(function)(*args).call(block_identifier=block_identifier)
        )

    async def async_call(self, function: str, *args, block_identifier: int | str = 'latest') -> DecodedTuple:
        return DecodedTuple.from_parameters_and_values(
            None,
            self.abi.function_by_name(function).outputs.parameters(),
            await self.contract.get_function_by_name(function)(*args).call(block_identifier=block_identifier)
        )


@dataclass
class DecodedLog:
    event: AbiEvent
    data: DecodedTuple


@dataclass
class DecodedTrace:
    function: AbiFunction
    input: DecodedTuple
    output: Optional[DecodedTuple]