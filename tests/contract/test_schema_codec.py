"""Tests for dataclass -> JSON Schema Draft 2020-12 converter."""

from tests.contract._paths import MAIN_REPO_ROOT, HARNESS_ROOT

import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import pytest

sys.path.insert(0, str(MAIN_REPO_ROOT / "skills" / "kicad" / "scripts"))

from schema_codec import dataclass_to_json_schema  # noqa: E402

from jsonschema import Draft202012Validator  # noqa: E402


def _schema_is_valid(schema: dict) -> None:
    """Raises if schema is not valid JSON Schema Draft 2020-12."""
    Draft202012Validator.check_schema(schema)


def test_empty_dataclass_produces_object_schema():
    @dataclass
    class Empty:
        pass

    schema = dataclass_to_json_schema(Empty)
    _schema_is_valid(schema)
    assert schema["$schema"] == "https://json-schema.org/draft/2020-12/schema"
    assert schema["type"] == "object"
    assert schema["properties"] == {}
    assert schema["required"] == []


def test_primitive_fields():
    @dataclass
    class Prim:
        count: int = field(metadata={"description": "A count"})
        ratio: float = field(metadata={"description": "A ratio"})
        name: str = field(metadata={"description": "A name"})
        flag: bool = field(metadata={"description": "A flag"})

    schema = dataclass_to_json_schema(Prim)
    _schema_is_valid(schema)
    assert schema["properties"]["count"] == {"type": "integer", "description": "A count"}
    assert schema["properties"]["ratio"] == {"type": "number", "description": "A ratio"}
    assert schema["properties"]["name"] == {"type": "string", "description": "A name"}
    assert schema["properties"]["flag"] == {"type": "boolean", "description": "A flag"}
    assert set(schema["required"]) == {"count", "ratio", "name", "flag"}


def test_optional_is_not_required_and_uses_anyof_null():
    @dataclass
    class Opt:
        required_field: str = field(metadata={"description": "r"})
        optional_field: Optional[int] = field(default=None, metadata={"description": "o"})

    schema = dataclass_to_json_schema(Opt)
    _schema_is_valid(schema)
    assert schema["required"] == ["required_field"]
    assert schema["properties"]["optional_field"] == {
        "anyOf": [{"type": "integer"}, {"type": "null"}],
        "description": "o",
    }


def test_list_of_primitives():
    @dataclass
    class L:
        tags: list[str] = field(metadata={"description": "tags"})

    schema = dataclass_to_json_schema(L)
    _schema_is_valid(schema)
    assert schema["properties"]["tags"] == {
        "type": "array",
        "items": {"type": "string"},
        "description": "tags",
    }


def test_dict_str_to_primitive():
    @dataclass
    class D:
        counts: dict[str, int] = field(metadata={"description": "counts by key"})

    schema = dataclass_to_json_schema(D)
    _schema_is_valid(schema)
    assert schema["properties"]["counts"] == {
        "type": "object",
        "additionalProperties": {"type": "integer"},
        "description": "counts by key",
    }


def test_nested_dataclass_inlined():
    @dataclass
    class Inner:
        value: int = field(metadata={"description": "v"})

    @dataclass
    class Outer:
        inner: Inner = field(metadata={"description": "i"})

    schema = dataclass_to_json_schema(Outer)
    _schema_is_valid(schema)
    inner_schema = schema["properties"]["inner"]
    assert inner_schema["type"] == "object"
    assert inner_schema["description"] == "i"
    assert inner_schema["properties"]["value"]["type"] == "integer"


def test_list_of_dataclass():
    @dataclass
    class Row:
        key: str = field(metadata={"description": "k"})

    @dataclass
    class Table:
        rows: list[Row] = field(metadata={"description": "rs"})

    schema = dataclass_to_json_schema(Table)
    _schema_is_valid(schema)
    assert schema["properties"]["rows"]["type"] == "array"
    assert schema["properties"]["rows"]["items"]["type"] == "object"
    assert schema["properties"]["rows"]["items"]["properties"]["key"]["type"] == "string"


def test_plain_dict_type_means_arbitrary_object():
    @dataclass
    class Arbitrary:
        blob: dict = field(metadata={"description": "free-form"})

    schema = dataclass_to_json_schema(Arbitrary)
    _schema_is_valid(schema)
    assert schema["properties"]["blob"] == {"type": "object", "description": "free-form"}


def test_missing_description_raises():
    @dataclass
    class Bad:
        x: int = 0

    with pytest.raises(ValueError, match="missing description metadata"):
        dataclass_to_json_schema(Bad)


def test_non_dataclass_raises_typeerror():
    class NotADataclass:
        x: int = 0

    with pytest.raises(TypeError, match="not a dataclass"):
        dataclass_to_json_schema(NotADataclass)


def test_unsupported_type_raises_with_class_field_context():
    @dataclass
    class HasTuple:
        pair: tuple[int, int] = field(metadata={"description": "a pair"})

    with pytest.raises(TypeError, match=r"HasTuple\.pair"):
        dataclass_to_json_schema(HasTuple)


def test_multi_arg_union():
    @dataclass
    class Multi:
        value: "int | str | None" = field(metadata={"description": "multi"})

    schema = dataclass_to_json_schema(Multi)
    _schema_is_valid(schema)
    # 3-arg union -> general-union branch returns {"anyOf": [...]}
    # Description is attached at the _object_schema_for level.
    assert "anyOf" in schema["properties"]["value"]
    variants = schema["properties"]["value"]["anyOf"]
    types_seen = {tuple(sorted(v.items())) for v in variants}
    assert len(variants) == 3
    assert {"type": "integer"} in variants
    assert {"type": "string"} in variants
    assert {"type": "null"} in variants


def test_default_factory_field_is_optional():
    @dataclass
    class HasFactory:
        items: list[int] = field(default_factory=list, metadata={"description": "items"})

    schema = dataclass_to_json_schema(HasFactory)
    _schema_is_valid(schema)
    assert schema["required"] == []
    assert schema["properties"]["items"]["type"] == "array"


def test_const_metadata_emits_const_constraint():
    @dataclass
    class Discriminated:
        kind: str = field(metadata={"description": "k", "const": "widget"})

    schema = dataclass_to_json_schema(Discriminated)
    _schema_is_valid(schema)
    assert schema["properties"]["kind"]["const"] == "widget"
    assert schema["properties"]["kind"]["type"] == "string"
    assert schema["properties"]["kind"]["description"] == "k"


def test_json_name_metadata_renames_property():
    @dataclass
    class R:
        underscore_field: str = field(metadata={
            "description": "d",
            "json_name": "_underscore_field",
        })

    schema = dataclass_to_json_schema(R)
    _schema_is_valid(schema)
    assert "_underscore_field" in schema["properties"]
    assert "_underscore_field" in schema["required"]
    assert "underscore_field" not in schema["properties"]
