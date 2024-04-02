from __future__ import annotations

from abc import ABC, abstractmethod
from functools import cached_property
from typing import List, Tuple, Dict, Optional, Callable

from semanticabi.abi.SemanticAbi import SemanticAbi
from semanticabi.abi.item.SemanticAbiItem import SemanticAbiItem, DecodedResult
from semanticabi.common.column.StringDatasetColumn import StringType
from semanticabi.metadata.EthBlock import EthBlock
from semanticabi.metadata.EthTransaction import EthTransaction
from semanticabi.steps.AbiSchema import AbiSchema

"""
Doing this as a NONE type rather than SYSTEM so that it can't get accidentally get dropped later. We break up the
handling of transform error into two parts, where the base Step class manages catching any errors and recording them
for later, and then only writes out the errors if the schema includes this column, which is done by including the
TransformErrorStep in the pipeline.
"""
TRANSFORM_ERROR_COLUMN = StringType.NONE('transform_error')


class TransformItem(ABC):
    """
    Normalized wrapper for the event or function that is generating the associated rows in the output.
    """
    _decoded_result_fn: Callable[[], DecodedResult]
    _transform_error: List[str]

    def __init__(self, decoded_result_fn: Callable[[], DecodedResult]):
        self._decoded_result_fn = decoded_result_fn
        self._transform_error = []

    @property
    @abstractmethod
    def contract_address(self) -> str:
        """
        The contract address that was interacted with to generate this item.
        """
        pass

    @property
    @abstractmethod
    def internal_index(self) -> str:
        """
        An index that uniquely identifies this item within the transaction.
        """
        pass

    @property
    @abstractmethod
    def item_type(self) -> str:
        """
        The type of item this is, either 'event' or 'function', to help in uniquely identifying the item within the
        transaction in combination with the internal index.
        """
        pass

    @cached_property
    def decoded_result(self) -> DecodedResult:
        """
        Lazily decode the result in case we filter out the item by contract address.
        """
        return self._decoded_result_fn()

    def add_transform_error(self, error: str) -> None:
        """
        Adds an error to the list of transform errors that will be reported at the end.
        """
        self._transform_error.append(error)

    @property
    def has_transform_error(self) -> bool:
        """
        Returns true if there are any transform errors.
        """
        return len(self._transform_error) > 0

    @property
    def transform_error(self) -> Optional[str]:
        return ",".join(self._transform_error) if self.has_transform_error else None


class Step(ABC):
    """
    Represents a step in the transaction transformation process. Each step takes the output of the previous step and
    applies the next set of transformations.
    """

    @property
    @abstractmethod
    def _abi(self) -> SemanticAbi:
        pass

    @property
    @abstractmethod
    def _abi_item(self) -> SemanticAbiItem:
        """
        The transformation process operates on a single primary abi item
        """
        pass

    @property
    @abstractmethod
    def schema(self) -> AbiSchema:
        """
        The current schema of all the steps that have run to this point
        """
        pass

    @abstractmethod
    def _inner_transform(self, block: EthBlock, transaction: EthTransaction) -> List[Tuple[TransformItem, List[Dict[str, any]]]]:
        """
        Returns a list of tuples of the current event or function being processed and the results for that item
        """
        pass

    def transform(self, block: EthBlock, transaction: EthTransaction) -> List[Dict[str, any]]:
        """
        Returns the transformed block and transaction data as a list of results
        """
        results: List[Dict[str, any]] = []
        schema: AbiSchema = self.schema
        for item, transformed_rows in self._inner_transform(block, transaction):
            for transformed_row in transformed_rows:
                final_row: Dict[str, any] = {}
                for dataset_column in schema.columns():
                    if dataset_column.name == TRANSFORM_ERROR_COLUMN.name:
                        final_row[TRANSFORM_ERROR_COLUMN.name] = item.transform_error
                        continue

                    try:
                        # Do any final column type transformation
                        final_row[dataset_column.name] = dataset_column.transform(transformed_row)
                    except Exception as e:
                        # Try to continue writing out the remaining data for the row before adding all the errors
                        item.add_transform_error(str(e))

                results.append(final_row)

        return results
