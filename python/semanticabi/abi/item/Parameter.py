from __future__ import annotations
from abc import ABC, abstractmethod
from functools import cached_property
from typing import List, Optional, Dict

from semanticabi.abi.InvalidAbiException import InvalidAbiException


class Parameter(ABC):
    """
    A parameter in an event or function, or a component of a tuple parameter.

    @author zuyezheng
    """

    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @property
    @abstractmethod
    def is_indexed(self) -> str:
        pass

    @property
    @abstractmethod
    def is_array(self) -> bool:
        pass

    @property
    @abstractmethod
    def is_array_of_arrays(self) -> bool:
        pass

    @property
    @abstractmethod
    def signature(self) -> str:
        pass


class PrimitiveParameter(Parameter):
    """
    Parameter for primitive values like address, uint256, and strings.
    """

    _name: str
    _primitive_type: str
    _is_indexed: bool

    def __init__(self, name: str, is_indexed: bool, primitive_type: str):
        self._name = name
        self._is_indexed = is_indexed
        self._primitive_type = primitive_type

    @property
    def name(self) -> str:
        return self._name

    @property
    def is_indexed(self) -> bool:
        return self._is_indexed

    @property
    def is_array(self) -> bool:
        return self._primitive_type.endswith('[]')

    @property
    def is_array_of_arrays(self) -> bool:
        return self._primitive_type.endswith('[][]')

    @property
    def signature(self) -> str:
        return self._primitive_type


class TupleParameter(Parameter):
    """
    "Tuple" or a struct parameter.
    """

    _name: str
    _is_indexed: bool
    _is_array: bool
    _is_array_of_arrays: bool

    components: List[Parameter]

    def __init__(self, name: str, is_indexed: bool, is_array: bool, is_array_of_arrays: bool, components: List[Parameter]):
        self._name = name
        self._is_indexed = is_indexed
        self._is_array = is_array
        self._is_array_of_arrays = is_array_of_arrays
        self.components = components

    @property
    def name(self) -> str:
        return self._name

    @property
    def is_indexed(self) -> bool:
        return self._is_indexed

    @property
    def is_array(self) -> bool:
        return self._is_array

    @property
    def is_array_of_arrays(self) -> bool:
        return self._is_array_of_arrays

    @cached_property
    def signature(self) -> str:
        signature = '(' + ','.join(map(lambda c: c.signature, self.components)) + ')'
        if self.is_array:
            signature += '[]'
        if self.is_array_of_arrays:
            signature += '[]'
        return signature


class Parameters:
    """
    List of input or output parameters in an event or function, or components of a tuple parameter
    """

    _parameters: List[Parameter]

    @staticmethod
    def parameters_from_json(parameter_jsons: List[Dict[str, any]]) -> List[Parameter]:
        parameters = []
        for parameter_json in parameter_jsons:
            parameter_name = parameter_json['name']
            if parameter_name == '':
                raise InvalidAbiException('Parameter name cannot be empty')
            parameter_type = parameter_json['type']

            if parameter_type in ['tuple', 'tuple[]', 'tuple[][]']:
                parameters.append(TupleParameter(
                    parameter_name,
                    # test of existence and explicit equality to true
                    parameter_json.get('indexed') is True,
                    parameter_type.endswith('[]'),
                    parameter_type.endswith('[][]'),
                    Parameters.parameters_from_json(parameter_json['components'])
                ))
            else:
                parameters.append(PrimitiveParameter(
                    parameter_name,
                    # test of existence and explicit equality to true
                    parameter_json.get('indexed') is True,
                    parameter_type
                ))

        return parameters

    @staticmethod
    def from_json(json_elements: List[Dict[str, any]]) -> Parameters:
        return Parameters(Parameters.parameters_from_json(json_elements))

    def __init__(self, parameters: List[Parameter]):
        self._parameters = parameters

    def parameters(self, indexed: Optional[bool] = None) -> List[Parameter]:
        if indexed is None:
            return self._parameters

        return list(filter(
            lambda e: e.is_indexed == indexed,
            self._parameters
        ))

    def signatures(self, indexed: Optional[bool] = None) -> List[str]:
        """
        Generate the signatures for all elements, optionally filter for indexed/unindexed elements.
        """
        return list(map(lambda e: e.signature, self.parameters(indexed)))
