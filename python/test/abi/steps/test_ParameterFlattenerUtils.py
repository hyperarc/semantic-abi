from typing import List

import pytest as pytest

from semanticabi.abi.InvalidAbiException import InvalidAbiException
from semanticabi.abi.item.Parameter import PrimitiveParameter, Parameter
from semanticabi.abi.item.SemanticParameter import SemanticParameter
from semanticabi.common.column.DatasetColumn import DatasetColumn
from semanticabi.steps.FlattenedParameter import FlattenedParameter
from semanticabi.steps.ParameterFlattener import ParameterFlattener


def test_build_column_name_root():
    path: List[SemanticParameter] = []
    name: str = 'foo'
    assert ParameterFlattener.build_column_name(path, name) == 'foo'


def test_build_column_name_nested():
    params: List[Parameter] = [PrimitiveParameter('foo', False, 'tuple'), PrimitiveParameter('bar', False, 'tuple')]
    path: List[SemanticParameter] = [SemanticParameter(param, None, False, None) for param in params]
    name: str = 'baz'
    assert ParameterFlattener.build_column_name(path, name) == 'foo_bar_baz'


def test_build_column_type_bool():
    field: PrimitiveParameter = PrimitiveParameter('fieldA', False, 'bool')
    assert FlattenedParameter.build_column(field, 'fieldA').type_metadata == {
        'ingestType': 'boolean',
        'expectedType': 'boolean'
    }


def test_build_column_type_address_hash():
    field: PrimitiveParameter = PrimitiveParameter('fieldA', False, 'address')
    column: DatasetColumn = FlattenedParameter.build_column(field, 'fieldA')
    assert column.type_metadata == {
        'ingestType': 'string',
        'expectedType': 'string',
        'isArray': False
    }
    assert column.extended_metadata == {
        'higherOrderType': 'addressHash'
    }


def test_build_column_type_string():
    field: PrimitiveParameter = PrimitiveParameter('fieldA', False, 'string')
    column: DatasetColumn = FlattenedParameter.build_column(field, 'fieldA')
    assert column.type_metadata == {
        'ingestType': 'string',
        'expectedType': 'string',
        'isArray': False
    }
    assert column.extended_metadata == {
        'higherOrderType': 'none'
    }


def test_build_column_type_bytes():
    field: PrimitiveParameter = PrimitiveParameter('fieldA', False, 'bytes')
    column: DatasetColumn = FlattenedParameter.build_column(field, 'fieldA')
    assert column.type_metadata == {
        'ingestType': 'string',
        'expectedType': 'string',
        'isArray': False
    }
    assert column.extended_metadata == {
        'higherOrderType': 'none'
    }


@pytest.mark.parametrize('primitive_type,expected_type', [
    ('int8', {'ingestType': 'byte', 'expectedType': 'byte'}),
    ('int16', {'ingestType': 'short', 'expectedType': 'short'}),
    ('int32', {'ingestType': 'integer', 'expectedType': 'integer'}),
    ('int64', {'ingestType': 'long', 'expectedType': 'long'}),
    ('int128', {'ingestType': 'decimal', 'expectedType': 'decimal', 'precision': 38, 'scale': 0}),
    ('int256', {'ingestType': 'string', 'expectedType': 'decimal', 'precision': 78, 'scale': 0}),
    # int is the same as int256
    ('int', {'ingestType': 'string', 'expectedType': 'decimal', 'precision': 78, 'scale': 0}),
    ('uint8', {'ingestType': 'short', 'expectedType': 'short'}),
    ('uint16', {'ingestType': 'integer', 'expectedType': 'integer'}),
    ('uint32', {'ingestType': 'long', 'expectedType': 'long'}),
    ('uint64', {'ingestType': 'decimal', 'expectedType': 'decimal', 'precision': 20, 'scale': 0}),
    # uint greater than 64 is just treated like int256 since it is coerced into a string
    ('uint128', {'ingestType': 'string', 'expectedType': 'decimal', 'precision': 78, 'scale': 0}),
    ('uint256', {'ingestType': 'string', 'expectedType': 'decimal', 'precision': 78, 'scale': 0})
])
def test_build_column_type_int(primitive_type: str, expected_type):
    field: PrimitiveParameter = PrimitiveParameter('fieldA', False, primitive_type)
    column: DatasetColumn = FlattenedParameter.build_column(field, 'fieldA')
    assert column.type_metadata == expected_type
    assert column.extended_metadata == {
        'higherOrderType': None
    }

