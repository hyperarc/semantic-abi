import logging
from abc import abstractmethod
from typing import List, Dict, Tuple

from semanticabi.abi.SemanticAbi import SemanticAbi
from semanticabi.abi.item.SemanticAbiItem import SemanticAbiItem
from semanticabi.common.TransformException import TransformException
from semanticabi.metadata.EthBlock import EthBlock
from semanticabi.metadata.EthTransaction import EthTransaction
from semanticabi.steps.Step import Step, TransformItem


class SubsequentStep(Step):
    """
    Steps that have a prior step
    """
    _previous_step: Step

    def __init__(self, previous_step: Step):
        self._previous_step = previous_step

    @property
    def _abi(self) -> SemanticAbi:
        return self._previous_step._abi

    @property
    def _abi_item(self) -> SemanticAbiItem:
        """
        The transformation process operates on a single primary abi item
        """
        return self._previous_step._abi_item

    def _should_transform(self) -> bool:
        """
        Returns true if this step should be run
        """
        return True

    @abstractmethod
    def _inner_transform_item(
        self,
        block: EthBlock,
        transaction: EthTransaction,
        item: TransformItem,
        previous_data: List[Dict[str, any]]
    ) -> List[Dict[str, any]]:
        """
        Apply a transform to an individual event or function, given any previous data that has already been transformed.
        The vast majority of steps should only need to implement this method, and use the default implementation of
        _inner_transform.
        """
        pass

    def _inner_transform(self, block: EthBlock, transaction: EthTransaction) -> List[Tuple[TransformItem, List[Dict[str, any]]]]:
        """
        Returns a list of tuples of the current event or function being processed and the results for that item
        """
        previous_results: List[Tuple[TransformItem, List[Dict[str, any]]]] = self._previous_step._inner_transform(block, transaction)
        if not self._should_transform():
            return previous_results

        results: List[Tuple[TransformItem, List[Dict[str, any]]]] = []
        for result_item, previous_data in previous_results:
            try:
                if not result_item.has_transform_error:
                    transformed_rows: List[Dict[str, any]] = self._inner_transform_item(block, transaction, result_item, previous_data)
                    results.append((result_item, transformed_rows))
                else:
                    results.append((result_item, previous_data))
            except Exception as e:
                # If there is an exception during transformation, add the error message to the row and continue
                result_item.add_transform_error(str(e))
                results.append((result_item, previous_data))
                if not isinstance(e, TransformException):
                    # For any unexpected exceptions, also log an error for later
                    logging.error(f'Error transforming transaction {transaction.hash}, chain {block.chain.name}, item with topic {self._abi_item.raw_item.hash}: {e}')

        return results
