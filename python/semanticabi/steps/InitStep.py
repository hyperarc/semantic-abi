from functools import partial
from typing import List, Tuple, Dict, Callable

from semanticabi.abi.SemanticAbi import SemanticAbi
from semanticabi.abi.item.SemanticAbiItem import SemanticAbiItem, SemanticAbiEvent, DecodedResult
from semanticabi.common.ValueConverter import ValueConverter
from semanticabi.metadata.EthBlock import EthBlock
from semanticabi.metadata.EthLog import EthLog
from semanticabi.metadata.EthTraces import EthTrace
from semanticabi.metadata.EthTransaction import EthTransaction
from semanticabi.steps.AbiSchema import AbiSchema
from semanticabi.steps.Step import Step, TransformItem


class EventTransformItem(TransformItem):
    """
    A TransformItem that wraps an EthLog event
    """
    event: EthLog

    def __init__(self, event: EthLog, decoded_result_fn: Callable[[], DecodedResult]):
        super().__init__(decoded_result_fn)
        self.event = event

    @property
    def contract_address(self) -> str:
        return self.event['address']

    @property
    def internal_index(self) -> str:
        return str(ValueConverter.hex_to_int(self.event['logIndex']))

    @property
    def item_type(self) -> str:
        return 'event'


class FunctionTransformItem(TransformItem):
    """
    A TransformItem that wraps an EthTrace function call
    """
    function: EthTrace

    def __init__(self, function: EthTrace, decoded_result_fn: Callable[[], DecodedResult]):
        super().__init__(decoded_result_fn)
        self.function = function

    @property
    def contract_address(self) -> str:
        return self.function.to_address

    @property
    def internal_index(self) -> str:
        return self.function.trace_hash

    @property
    def item_type(self) -> str:
        return 'function'


class InitStep(Step):
    """
    A no-op step that gets initialized with the particular ABI item that it'll handle, and filters the logs
    or traces by the signature of that item, optionally also filtering those by any contract addresses specified in the
    ABI, adding an empty row for each matching log or trace
    """

    _semantic_abi: SemanticAbi
    _semantic_abi_item: SemanticAbiItem
    _schema: AbiSchema

    def __init__(self, abi: SemanticAbi, abi_item: SemanticAbiItem):
        self._semantic_abi = abi
        self._semantic_abi_item = abi_item
        self._schema = AbiSchema()

    @property
    def _abi(self) -> SemanticAbi:
        return self._semantic_abi

    @property
    def _abi_item(self) -> SemanticAbiItem:
        return self._semantic_abi_item

    @property
    def schema(self) -> AbiSchema:
        return self._schema

    def _inner_transform(self, block: EthBlock, transaction: EthTransaction) -> List[Tuple[TransformItem, List[Dict[str, any]]]]:
        results = []
        if isinstance(self._abi_item, SemanticAbiEvent):
            logs: List[EthLog] = transaction.logs_by_topic.get(self._abi_item.raw_item.hash, [])
            for log in logs:
                transform_item: EventTransformItem = EventTransformItem(log, partial(self._abi_item.decode, log))
                if self._abi.should_consider(transform_item.contract_address):
                    results.append((transform_item, [{}]))
        else:
            traces: List[EthTrace] = transaction.traces_by_topic.get(self._abi_item.raw_item.hash, [])
            for trace in traces:
                transform_item: FunctionTransformItem = FunctionTransformItem(trace, partial(self._abi_item.decode, trace))
                if self._abi.should_consider(transform_item.contract_address):
                    results.append((transform_item, [{}]))

        return results
