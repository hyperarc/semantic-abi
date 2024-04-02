from __future__ import annotations
from dataclasses import dataclass
from functools import cached_property
from typing import List, TypedDict, Optional, Dict

from semanticabi.abi.InvalidAbiException import InvalidAbiException
from semanticabi.abi.item.SemanticParameter import SemanticParameters, SemanticParameter


class TypedExplode(TypedDict):
    paths: List[str]


@dataclass
class Explode:
    """
    Defines the paths in a jsonpath-like dot-separated format to explode into separate rows.
    """

    @staticmethod
    def from_json(json: TypedExplode) -> Explode:
        return Explode(json['paths'])

    paths: List[str]

    @cached_property
    def path_parts(self) -> Dict[str, List[str]]:
        """
        The path parts for each path
        """
        return {path: path.split('.') for path in self.paths}

    def validate(self, all_parameters: List[SemanticParameters]):
        for path, path_parts in self.path_parts.items():
            parameter: Optional[SemanticParameter] = None

            # Find the root parameter in the input or output traces
            for parameters_set in all_parameters:
                parameter = parameters_set.parameter(path_parts[0]) if parameters_set.has_parameter(path_parts[0]) else None
                if parameter is not None:
                    break

            for part in path_parts[1:]:
                if parameter is None:
                    break

                if parameter.exclude:
                    raise InvalidAbiException(f'Explode path \'{path}\' cannot reference an excluded parameter: {part}')

                if parameter.parameter.is_array:
                    raise InvalidAbiException(f'Explode path \'{path}\' does not support nested arrays: {part}')

                parameter = parameter.components.parameter(part) if parameter.components is not None and parameter.components.has_parameter(part) else None

            if parameter is None:
                raise InvalidAbiException(f'Explode path \'{path}\' not found in item parameters')

            if not parameter.parameter.is_array:
                raise InvalidAbiException(f'Explode path \'{path}\' is not an array')

            if parameter.parameter.is_array_of_arrays:
                raise InvalidAbiException(f'Explode path \'{path}\' does not support array of arrays')
