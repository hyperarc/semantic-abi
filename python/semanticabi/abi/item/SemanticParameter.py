from __future__ import annotations
from dataclasses import dataclass
from typing import TypedDict, Optional, Dict, List, Set

from semanticabi.abi.InvalidAbiException import InvalidAbiException
from semanticabi.abi.item.DataType import DataType
from semanticabi.abi.item.Parameter import Parameter, TupleParameter
from semanticabi.common.expression.ExpressionEvaluator import ExpressionEvaluator

TYPE_NAME = 'type'

TRANSFORM_NAME = '@transform'
EXCLUDE_NAME = '@exclude'


class TypedTransform(TypedDict):
    name: Optional[str]
    expression: Optional[str]
    type: Optional[str]


_EXPECTED_PARAMETER_EXPRESSION_COLUMNS: Set[str] = {'this'}


@dataclass
class ParameterTransform:
    """
    Transforms to apply to the associated parameter
    """

    # The name to rename this parameter to in the resulting dataset
    name: Optional[str]
    # An expression to apply to the value of this parameter
    expression: Optional[str]
    # The type to cast the value of this parameter to
    type: Optional[DataType]

    def __post_init__(self):
        if self.expression is not None:
            self._expression_evaluator = ExpressionEvaluator(self.expression)
            column_names = self._expression_evaluator.column_names()
            if column_names != _EXPECTED_PARAMETER_EXPRESSION_COLUMNS:
                raise InvalidAbiException(f'Expression \'{self.expression}\' must only reference \'this\'')

    @staticmethod
    def from_json(json: TypedTransform) -> ParameterTransform:
        data_type = DataType.get(json[TYPE_NAME]) if TYPE_NAME in json else None

        return ParameterTransform(
            json.get('name', None),
            json.get('expression', None),
            data_type
        )

    def evaluate_expression(self, value: any) -> any:
        """
        Evaluate the expression for this transform
        """
        if self.expression is None:
            return value

        return self._expression_evaluator.evaluate({'this': value})


@dataclass
class SemanticParameter:
    # The underlying parameter
    parameter: Parameter
    # If this parameter should be excluded from the resulting dataset
    exclude: bool = False
    # The component parameters if this is a tuple
    components: Optional['SemanticParameters'] = None
    # Any optional transformations to apply to the parameter
    transform: Optional[ParameterTransform] = None

    @staticmethod
    def from_json(parameter: Parameter, parameter_json: Dict[str, any]) -> SemanticParameter:
        if isinstance(parameter, TupleParameter) and TRANSFORM_NAME in parameter_json:
            raise InvalidAbiException('Transforms are not supported for tuples')

        return SemanticParameter(
            parameter,
            parameter_json.get(EXCLUDE_NAME, False),
            SemanticParameters.from_parameters(parameter.components, parameter_json['components']) if isinstance(parameter, TupleParameter) else None,
            ParameterTransform.from_json(parameter_json[TRANSFORM_NAME]) if TRANSFORM_NAME in parameter_json else None
        )

    @property
    def name(self) -> str:
        """
        Get the name of this parameter
        """
        return self.parameter.name


class SemanticParameters:
    _parameters_by_name: Dict[str, SemanticParameter]

    def __init__(self, parameters_by_name: Dict[str, SemanticParameter]):
        self._parameters_by_name = parameters_by_name

    @staticmethod
    def from_parameters(parameters: List[Parameter], parameters_json: List[Dict[str, any]]) -> SemanticParameters:
        parameter_names = set()
        for parameter in parameters:
            if parameter.name in parameter_names:
                raise InvalidAbiException(f'Parameter \'{parameter.name}\' is duplicated')

            parameter_names.add(parameter.name)

        parameters_json_by_name: Dict[str, Dict[str, any]] = {f['name']: f for f in parameters_json}
        return SemanticParameters({f.name: SemanticParameter.from_json(f, parameters_json_by_name[f.name]) for f in parameters})

    def parameter(self, name: str) -> SemanticParameter:
        return self._parameters_by_name[name]

    def has_parameter(self, name: str) -> bool:
        return name in self._parameters_by_name

    def parameters(self) -> Dict[str, SemanticParameter]:
        return self._parameters_by_name
