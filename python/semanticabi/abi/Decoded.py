from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Dict, Optional, List

from semanticabi.abi.item.Parameter import Parameter, TupleParameter


class Decoded(ABC):
    """
    Decoded value that supports serialization back into json.

    @author zuyezheng
    """

    @abstractmethod
    def add_to_json(self, json_obj: Dict[str, any]) -> Dict[str, any]:
        pass


class DecodedPrimitive(Decoded):

    parameter: Parameter
    value: any

    def __init__(self, parameter: Parameter, value: any):
        self.parameter = parameter
        self.value = value

    def add_to_json(self, json_obj: Dict[str, any]) -> Dict[str, any]:
        value = self.value

        if self.parameter.signature.startswith('bytes'):
            if self.parameter.is_array:
                value = [v.hex() for v in value]
            else:
                value = value.hex()

        json_obj[self.parameter.name] = value
        return json_obj


class DecodedTupleArray(Decoded):

    parameter: Optional[TupleParameter]
    values: List[any]

    def __init__(self, parameter: Optional[TupleParameter], values: List[any]):
        self.parameter = parameter
        self.values = values

    def add_to_json(self, json_obj: Dict[str, any]) -> Dict[str, any]:
        tuple_json = []
        for tuple_value in self.values:
            tuple_json.append(
                DecodedTuple.from_parameters_and_values(
                    None, self.parameter.components, tuple_value
                ).to_json()
            )

        json_obj[self.parameter.name] = tuple_json

        return json_obj


class DecodedTuple(Decoded):

    parameter: Optional[TupleParameter]
    decoded: List[Decoded]

    @staticmethod
    def from_parameters_and_values(
        # root parameter if this is a nested tuple, otherwise none
        root_parameter: Optional[TupleParameter],
        parameters: List[Parameter],
        decoded_values: any | List[any]
    ) -> DecodedTuple:
        # if there is a single parameter for output, values will just be the value
        if not isinstance(decoded_values, list) and not isinstance(decoded_values, tuple):
            decoded_values = [decoded_values]

        decoded = []
        for (parameter, value) in zip(parameters, decoded_values):
            if isinstance(parameter, TupleParameter):
                if parameter.is_array:
                    decoded.append(DecodedTupleArray(parameter, value))
                else:
                    decoded.append(DecodedTuple.from_parameters_and_values(
                        parameter, parameter.components, value
                    ))
            else:
                decoded.append(DecodedPrimitive(parameter, value))

        return DecodedTuple(root_parameter, decoded)

    def __init__(self, parameter: Optional[TupleParameter], decoded: List[Decoded]):
        self.parameter = parameter
        self.decoded = decoded

    def add_to_json(self, json_obj: Dict[str, any]) -> Dict[str, any]:
        tuple_json = {}
        for cur_decoded in self.decoded:
            cur_decoded.add_to_json(tuple_json)

        if self.parameter is None:
            json_obj = tuple_json
        else:
            json_obj[self.parameter.name] = tuple_json

        return json_obj

    def to_json(self) -> Dict[str, any]:
        return self.add_to_json({})
