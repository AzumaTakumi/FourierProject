#!/usr/bin/env python3
"""
Generate Python skeleton code directly from astah XMI/XML class model.

Typical usage:
  python generate_python_from_astah_xmi.py FourierSignalModel.xml generated --write

Without --write, this runs in dry-run mode and only reports planned files.
"""

from __future__ import annotations

import argparse
import difflib
import keyword
import re
import urllib.parse
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path

TYPE_MAP = {
    "void": "None",
    "boolean": "bool",
    "Boolean": "bool",
    "String": "str",
    "str": "str",
    "integer": "int",
    "Integer": "int",
    "int": "int",
    "float": "float",
    "double": "float",
    "list": "list",
    "List": "list",
    "ndarray": "np.ndarray",
    "np.ndarray": "np.ndarray",
    "PIL.Image": "Image.Image",
    "PIL.Image.Image": "Image.Image",
    "Callable": "Callable",
    "Function": "Callable",
    "None": "None",
    "none": "None",
}

NONE_LITERALS = {"none", "null", "none", "NULL", "None"}
BUILTIN_TYPE_NAMES = {
    "Any",
    "None",
    "bool",
    "int",
    "float",
    "str",
    "list",
    "dict",
    "set",
    "tuple",
    "object",
    "Enum",
    "auto",
    "Callable",
    "np",
    "ndarray",
    "Image",
}
EXTERNAL_MODEL_TYPE_NAMES = {
    "any",
    "str",
    "list",
    "dict",
    "set",
    "tuple",
    "int",
    "float",
    "bool",
    "object",
    "none",
    "ndarray",
    "np.ndarray",
    "pil.image",
    "pil.image.image",
    "callable",
    "function",
}
EXTERNAL_GENERIC_PREFIXES = (
    "list[",
    "list<",
    "dict[",
    "dict<",
    "set[",
    "set<",
    "tuple[",
    "tuple<",
)

SAFE_AREA_PATTERN = re.compile(
    r"(?P<start>^[ \t]*# SAFE CODE AREA ˅\n)"
    r"(?P<body>.*?)"
    r"(?P<end>^[ \t]*# SAFE CODE AREA ˄\n?)",
    re.M | re.S,
)
SAFE_AREA_DEFAULT_PLACEHOLDER = "# add module-level custom code"
GENERATED_CODE_AREA_PATTERN = re.compile(
    r"(?P<start>^(?P<indent>[ \t]*)# (?P<state>GENERATED|FIXED) CODE AREA: (?P<label>[^\n]+?) ˅\n)"
    r"(?P<body>.*?)"
    r"(?P<end>^(?P=indent)# (?P=state) CODE AREA: (?P=label) ˄\n?)",
    re.M | re.S,
)


@dataclass(frozen=True)
class ParameterSpec:
    name: str
    type_name: str
    default: str | None


@dataclass(frozen=True)
class AttributeSpec:
    name: str
    type_name: str
    default: str | None
    definition: str | None
    is_enum_literal: bool


@dataclass(frozen=True)
class MethodSpec:
    name: str
    parameters: tuple[ParameterSpec, ...]
    return_type: str
    definition: str | None


@dataclass(frozen=True)
class ClassSpec:
    class_id: str
    original_name: str
    name: str
    package_name: str
    definition: str | None
    base_class_name: str | None
    is_enumeration: bool
    is_dataclass: bool
    attributes: tuple[AttributeSpec, ...]
    methods: tuple[MethodSpec, ...]


@dataclass(frozen=True)
class XmiModel:
    package_to_classes: dict[str, tuple[ClassSpec, ...]]


@dataclass(frozen=True)
class GeneratedCodeArea:
    label: str
    state: str
    start: str
    body: str
    end: str


def local_name(tag: str) -> str:
    if "}" in tag:
        return tag.rsplit("}", 1)[1]
    if ":" in tag:
        return tag.rsplit(":", 1)[1]
    return tag


def xmi_attr(elem: ET.Element, name: str) -> str | None:
    return elem.attrib.get(f"xmi.{name}") or elem.attrib.get(name)


def direct_children_by_local(elem: ET.Element, local: str) -> list[ET.Element]:
    return [c for c in list(elem) if local_name(c.tag) == local]


def child_classifier_idref(elem: ET.Element) -> str | None:
    for child in elem.iter():
        if local_name(child.tag) == "Classifier":
            return xmi_attr(child, "idref")
    return None


def decode_astah_text(value: str | None) -> str | None:
    if value is None:
        return None
    text = urllib.parse.unquote_plus(value).strip()
    return text or None


def decode_astah_name(value: str | None) -> str | None:
    return decode_astah_text(value)


def read_definition(elem: ET.Element) -> str | None:
    for def_node in direct_children_by_local(elem, "ModelElement.definition"):
        text = decode_astah_text(def_node.attrib.get("xmi.value") or def_node.attrib.get("value"))
        if text:
            return text
    return None


def parse_param_name(raw_name: str | None) -> tuple[str, str | None]:
    decoded = decode_astah_name(raw_name) or ""
    if "=" in decoded:
        name, default = decoded.split("=", 1)
        return name.strip(), default.strip()
    return decoded, None


def to_safe_identifier(name: str, fallback: str = "value") -> str:
    raw = name.strip()
    leading = len(raw) - len(raw.lstrip("_"))
    trailing = len(raw) - len(raw.rstrip("_"))
    core = raw.strip("_")

    core = re.sub(r"[^0-9A-Za-z_]", "_", core)
    core = re.sub(r"_+", "_", core).strip("_")
    if not core:
        core = fallback

    if core[0].isdigit():
        core = f"_{core}"
    if keyword.iskeyword(core) and leading == 0 and trailing == 0:
        core = f"{core}_"

    return f"{'_' * leading}{core}{'_' * trailing}"


def normalize_type(
    type_name: str | None,
    class_name_map: dict[str, str],
    default: str | None = None,
) -> str:
    decoded_type = decode_astah_name(type_name)
    if not decoded_type:
        py_type = "Any"
    else:
        py_type = TYPE_MAP.get(decoded_type)
        if py_type is None:
            py_type = normalize_collection_type_name(decoded_type)
        if py_type is None:
            py_type = class_name_map.get(decoded_type, to_safe_identifier(decoded_type, fallback="Any"))
    if default is not None and default.strip() in NONE_LITERALS and py_type != "None":
        return f"{py_type} | None"
    return py_type


def is_external_model_type(class_name: str) -> bool:
    normalized = decode_astah_name(class_name) or ""
    lower = normalized.strip().lower()
    if lower in EXTERNAL_MODEL_TYPE_NAMES:
        return True
    compact = re.sub(r"\s+", "", lower)
    return any(compact.startswith(prefix) for prefix in EXTERNAL_GENERIC_PREFIXES)


def normalize_collection_type_name(type_name: str) -> str | None:
    compact = re.sub(r"\s+", "", type_name).lower()
    if compact.startswith(("list[", "list<")):
        return "list"
    if compact.startswith(("dict[", "dict<")):
        return "dict"
    if compact.startswith(("set[", "set<")):
        return "set"
    if compact.startswith(("tuple[", "tuple<")):
        return "tuple"
    return None


def normalize_default_expr(value: str | None) -> str | None:
    if value is None:
        return None
    v = value.strip()
    if not v:
        return None
    lower = v.lower()
    if lower == "none" or lower == "null":
        return "None"
    if lower == "true":
        return "True"
    if lower == "false":
        return "False"
    return v


def fallback_default_expr(type_name: str) -> str:
    if type_name == "None":
        return "None"
    if "| None" in type_name:
        return "None"
    if type_name == "bool":
        return "False"
    if type_name == "int":
        return "0"
    if type_name == "float":
        return "0.0"
    if type_name == "str":
        return "''"
    if type_name == "list":
        return "[]"
    if type_name == "dict":
        return "{}"
    if type_name == "set":
        return "set()"
    if type_name == "tuple":
        return "()"
    return "None"


def parse_initial_value(attr: ET.Element) -> str | None:
    for init_node in direct_children_by_local(attr, "Attribute.initialValue"):
        for expr_node in init_node.iter():
            if local_name(expr_node.tag) == "Expression.body":
                return normalize_default_expr(expr_node.text)
    return None


def collect_classifier_names(root: ET.Element) -> dict[str, str]:
    id_to_name: dict[str, str] = {}
    for elem in root.iter():
        if local_name(elem.tag) in {"Class", "Interface", "DataType", "Primitive", "Enumeration"}:
            xid = xmi_attr(elem, "id")
            name = decode_astah_name(elem.attrib.get("name"))
            if xid and name:
                id_to_name[xid] = name
    return id_to_name


def collect_package_names(root: ET.Element) -> dict[str, str]:
    id_to_name: dict[str, str] = {}
    for elem in root.iter():
        if local_name(elem.tag) == "Package":
            xid = xmi_attr(elem, "id")
            name = decode_astah_name(elem.attrib.get("name"))
            if xid and name:
                id_to_name[xid] = name
    return id_to_name


def collect_generalization_map(root: ET.Element) -> dict[str, str]:
    child_to_parent: dict[str, str] = {}
    for gen in root.iter():
        if local_name(gen.tag) != "Generalization":
            continue
        gen_id = xmi_attr(gen, "id")
        if not gen_id:
            continue
        child_id = None
        parent_id = None
        for child_section in direct_children_by_local(gen, "Generalization.child"):
            for ge in child_section.iter():
                if local_name(ge.tag) == "GeneralizableElement":
                    child_id = xmi_attr(ge, "idref")
        for parent_section in direct_children_by_local(gen, "Generalization.parent"):
            for ge in parent_section.iter():
                if local_name(ge.tag) == "GeneralizableElement":
                    parent_id = xmi_attr(ge, "idref")
        if child_id and parent_id:
            child_to_parent[child_id] = parent_id
    return child_to_parent


def collect_stereotype_names(root: ET.Element) -> dict[str, str]:
    id_to_name: dict[str, str] = {}
    for elem in root.iter():
        if local_name(elem.tag) != "Stereotype":
            continue
        sid = xmi_attr(elem, "id")
        name = decode_astah_name(elem.attrib.get("name"))
        if sid and name:
            id_to_name[sid] = name
    return id_to_name


def collect_dependency_endpoint_id(elem: ET.Element, endpoint_local: str) -> str | None:
    for section in direct_children_by_local(elem, endpoint_local):
        for child in section.iter():
            cid = xmi_attr(child, "idref")
            if cid:
                return cid
    return None


def is_realize_usage(usage: ET.Element, stereotype_names: dict[str, str]) -> bool:
    for st_container in direct_children_by_local(usage, "ModelElement.stereotype"):
        for st_elem in st_container.iter():
            if local_name(st_elem.tag) != "Stereotype":
                continue
            sid = xmi_attr(st_elem, "idref")
            if not sid:
                continue
            if stereotype_names.get(sid, "").lower() == "realize":
                return True
    return False


def class_has_stereotype(elem: ET.Element, stereotype_name: str, stereotype_names: dict[str, str]) -> bool:
    expected = stereotype_name.lower()
    for st_container in direct_children_by_local(elem, "ModelElement.stereotype"):
        for st_elem in st_container.iter():
            if local_name(st_elem.tag) != "Stereotype":
                continue
            sid = xmi_attr(st_elem, "idref")
            if not sid:
                continue
            if stereotype_names.get(sid, "").lower() == expected:
                return True
    return False


def collect_realization_map(root: ET.Element) -> dict[str, str]:
    stereotype_names = collect_stereotype_names(root)
    client_to_supplier: dict[str, str] = {}
    for usage in root.iter():
        if local_name(usage.tag) != "Usage":
            continue
        usage_id = xmi_attr(usage, "id")
        if not usage_id:
            # Skip xmi.idref references under diagram presentation trees.
            continue
        if not is_realize_usage(usage, stereotype_names):
            continue
        client_id = collect_dependency_endpoint_id(usage, "Dependency.client")
        supplier_id = collect_dependency_endpoint_id(usage, "Dependency.supplier")
        if client_id and supplier_id:
            client_to_supplier[client_id] = supplier_id
    return client_to_supplier


def get_visibility(elem: ET.Element) -> str | None:
    visibility = elem.attrib.get("visibility")
    if visibility:
        return visibility
    for vis_node in direct_children_by_local(elem, "ModelElement.visibility"):
        value = vis_node.attrib.get("xmi.value") or vis_node.attrib.get("value")
        if value:
            return value
    return None


def has_tagged_value(elem: ET.Element, tag: str, value: str | None = None) -> bool:
    for tv_container in direct_children_by_local(elem, "ModelElement.taggedValue"):
        for tagged in direct_children_by_local(tv_container, "TaggedValue"):
            if tagged.attrib.get("tag") != tag:
                continue
            if value is None or tagged.attrib.get("value") == value:
                return True
    return False


def collect_namespace_id(elem: ET.Element) -> str | None:
    for ns_container in direct_children_by_local(elem, "ModelElement.namespace"):
        for ns in ns_container.iter():
            if local_name(ns.tag) == "Namespace":
                return xmi_attr(ns, "idref")
    return None


def parse_xmi(xml_path: Path) -> XmiModel:
    root = ET.parse(xml_path).getroot()
    id_to_name = collect_classifier_names(root)
    classifier_py_names = {name: to_safe_identifier(name, fallback="TypeName") for name in set(id_to_name.values())}
    package_id_to_name = collect_package_names(root)
    child_to_parent_id = collect_generalization_map(root)
    child_to_interface_id = collect_realization_map(root)
    stereotype_names = collect_stereotype_names(root)

    package_to_classes: dict[str, list[ClassSpec]] = {}

    for cls in root.iter():
        if local_name(cls.tag) not in {"Class", "Interface"}:
            continue
        class_id = xmi_attr(cls, "id")
        class_name_raw = decode_astah_name(cls.attrib.get("name"))
        class_name = to_safe_identifier(class_name_raw or "", fallback="GeneratedClass")
        if not class_id or not class_name_raw:
            continue
        if is_external_model_type(class_name_raw):
            continue

        package_id = collect_namespace_id(cls)
        package_name = package_id_to_name.get(package_id or "", "generated")
        class_definition = read_definition(cls)
        is_enumeration = has_tagged_value(cls, "jude.enumeration", "true")
        is_dataclass = class_has_stereotype(cls, "dataclass", stereotype_names)

        attributes: list[AttributeSpec] = []
        methods: list[MethodSpec] = []

        for feature in direct_children_by_local(cls, "Classifier.feature"):
            for attr in direct_children_by_local(feature, "Attribute"):
                attr_name = decode_astah_name(attr.attrib.get("name"))
                if not attr_name:
                    continue
                attr_name = to_safe_identifier(attr_name)

                type_ref = None
                for type_node in direct_children_by_local(attr, "StructuralFeature.type"):
                    type_ref = child_classifier_idref(type_node)
                uml_type = id_to_name.get(type_ref or "")

                default_value = parse_initial_value(attr)
                attr_type = normalize_type(uml_type, classifier_py_names, default_value)
                attr_definition = read_definition(attr)
                is_enum_literal = has_tagged_value(attr, "jude.enumeration_literal", "true")

                attributes.append(
                    AttributeSpec(
                        name=attr_name,
                        type_name=attr_type,
                        default=default_value,
                        definition=attr_definition,
                        is_enum_literal=is_enum_literal,
                    )
                )

            for op in direct_children_by_local(feature, "Operation"):
                method_name = decode_astah_name(op.attrib.get("name"))
                if not method_name:
                    continue
                if get_visibility(op) == "protected" and not method_name.startswith("_"):
                    method_name = f"_{method_name}"
                method_name = to_safe_identifier(method_name, fallback="method")

                params: list[ParameterSpec] = []
                return_type = "None"

                for bf_param in direct_children_by_local(op, "BehavioralFeature.parameter"):
                    for param in direct_children_by_local(bf_param, "Parameter"):
                        kind = param.attrib.get("kind")
                        type_ref = None
                        for type_node in direct_children_by_local(param, "Parameter.type"):
                            type_ref = child_classifier_idref(type_node)
                        uml_type = id_to_name.get(type_ref or "")

                        if kind == "return":
                            return_type = normalize_type(uml_type, classifier_py_names)
                            continue
                        if kind not in {"in", "inout", "out"}:
                            continue

                        name, default = parse_param_name(param.attrib.get("name"))
                        if not name:
                            continue
                        params.append(
                            ParameterSpec(
                                name=to_safe_identifier(name),
                                type_name=normalize_type(uml_type, classifier_py_names, default),
                                default=default,
                            )
                        )

                methods.append(
                    MethodSpec(
                        name=method_name,
                        parameters=tuple(params),
                        return_type=return_type,
                        definition=read_definition(op),
                    )
                )

        base_class_name = None
        parent_id = child_to_parent_id.get(class_id)
        if not parent_id:
            parent_id = child_to_interface_id.get(class_id)
        if parent_id:
            base_raw = id_to_name.get(parent_id)
            if base_raw:
                base_class_name = classifier_py_names.get(base_raw, to_safe_identifier(base_raw, fallback="BaseClass"))

        package_to_classes.setdefault(package_name, []).append(
            ClassSpec(
                class_id=class_id,
                original_name=class_name_raw,
                name=class_name,
                package_name=package_name,
                definition=class_definition,
                base_class_name=base_class_name,
                is_enumeration=is_enumeration,
                is_dataclass=is_dataclass,
                attributes=tuple(attributes),
                methods=tuple(methods),
            )
        )

    frozen = {pkg: tuple(sorted(classes, key=lambda c: c.name.lower())) for pkg, classes in package_to_classes.items()}
    return XmiModel(package_to_classes=frozen)


def discover_input_xmls(xml_path: Path) -> list[Path]:
    base_path = xml_path.resolve()
    prefix = base_path.stem
    related = [
        candidate.resolve()
        for candidate in base_path.parent.glob(f"{prefix}*.xml")
        if candidate.resolve() != base_path
    ]
    return [base_path, *sorted(related, key=lambda path: path.name.lower())]


def merge_models(models: list[XmiModel]) -> XmiModel:
    merged: dict[str, dict[str, ClassSpec]] = {}
    for model in models:
        for package_name, classes in model.package_to_classes.items():
            package_classes = merged.setdefault(package_name, {})
            for cls in classes:
                package_classes.setdefault(cls.name, cls)

    return XmiModel(
        package_to_classes={
            package_name: tuple(sorted(package_classes.values(), key=lambda cls: cls.name.lower()))
            for package_name, package_classes in merged.items()
        }
    )


def to_safe_module_name(class_name: str) -> str:
    text = re.sub(r"[^0-9A-Za-z_]", "_", class_name)
    text = re.sub(r"(.)([A-Z][a-z]+)", r"\1_\2", text)
    text = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", text)
    text = re.sub(r"([A-Za-z])([0-9])", r"\1_\2", text)
    text = re.sub(r"([0-9])([A-Za-z])", r"\1_\2", text)
    text = re.sub(r"_+", "_", text).strip("_").lower()
    if not text:
        text = "generated_class"
    if text[0].isdigit():
        text = f"_{text}"
    if keyword.iskeyword(text):
        text = f"{text}_"
    return text


def extract_annotation_type_names(type_expr: str) -> set[str]:
    names = set(re.findall(r"\b[A-Za-z_]\w*\b", type_expr))
    return {n for n in names if n not in BUILTIN_TYPE_NAMES}


def render_docstring_block(doc: str, indent: str = "    ") -> list[str]:
    safe = doc.replace('"""', '\\"\\"\\"')
    lines = safe.splitlines()
    out = [f'{indent}"""\n']
    for line in lines:
        out.append(f"{indent}{line}\n")
    out.append(f'{indent}"""\n')
    return out


def render_comment_block(doc: str, indent: str = "    ") -> list[str]:
    safe = doc.strip()
    if not safe:
        return []
    out: list[str] = []
    for line in safe.splitlines():
        stripped = line.strip()
        if stripped:
            out.append(f"{indent}# {stripped}\n")
        else:
            out.append(f"{indent}#\n")
    return out


def render_safe_area(indent: str, default_body_lines: list[str]) -> list[str]:
    out = [f"{indent}# SAFE CODE AREA ˅\n"]
    for line in default_body_lines:
        out.append(f"{indent}{line}\n")
    out.append(f"{indent}# SAFE CODE AREA ˄\n")
    return out


def render_generated_code_area(indent: str, label: str, body_lines: list[str]) -> list[str]:
    out = [f"{indent}# GENERATED CODE AREA: {label} ˅\n"]
    out.extend(body_lines)
    out.append(f"{indent}# GENERATED CODE AREA: {label} ˄\n")
    return out


def append_blank_line(out: list[str]) -> None:
    if not out:
        out.append("\n")
        return
    if out[-1] != "\n":
        out.append("\n")


def extract_safe_areas(text: str) -> list[str]:
    areas: list[str] = []
    for m in SAFE_AREA_PATTERN.finditer(text):
        areas.append(m.group("body"))
    return areas


def extract_safe_areas_by_context(text: str) -> tuple[list[str], dict[str, list[str]]]:
    outside_areas: list[str] = []
    generated_area_safe_areas: dict[str, list[str]] = {}

    cursor = 0
    for match in GENERATED_CODE_AREA_PATTERN.finditer(text):
        outside_areas.extend(extract_safe_areas(text[cursor : match.start()]))
        label = match.group("label")
        generated_area_safe_areas.setdefault(label, []).extend(extract_safe_areas(match.group("body")))
        cursor = match.end()

    outside_areas.extend(extract_safe_areas(text[cursor:]))
    return outside_areas, generated_area_safe_areas


def merge_safe_areas_in_segment(new_segment: str, old_areas: list[str], start_index: int) -> tuple[str, int]:
    index = start_index

    def _replace(match: re.Match[str]) -> str:
        nonlocal index
        if index >= len(old_areas):
            return match.group(0)
        old_body = old_areas[index]
        index += 1
        if old_body.strip() == SAFE_AREA_DEFAULT_PLACEHOLDER:
            old_body = ""
        return f"{match.group('start')}{old_body}{match.group('end')}"

    return SAFE_AREA_PATTERN.sub(_replace, new_segment), index


def extract_generated_code_areas(text: str) -> dict[str, GeneratedCodeArea]:
    areas: dict[str, GeneratedCodeArea] = {}
    for match in GENERATED_CODE_AREA_PATTERN.finditer(text):
        label = match.group("label")
        areas[label] = GeneratedCodeArea(
            label=label,
            state=match.group("state"),
            start=match.group("start"),
            body=match.group("body"),
            end=match.group("end"),
        )
    return areas


def merge_generated_code_areas(new_text: str, old_text: str) -> str:
    old_areas = extract_generated_code_areas(old_text)

    def _replace(match: re.Match[str]) -> str:
        label = match.group("label")
        old_area = old_areas.get(label)
        if old_area is None or old_area.state != "FIXED":
            return match.group(0)
        return f"{old_area.start}{old_area.body}{old_area.end}"

    return GENERATED_CODE_AREA_PATTERN.sub(_replace, new_text)


def merge_safe_areas(new_text: str, old_text: str) -> str:
    old_outside_areas, old_generated_area_areas = extract_safe_areas_by_context(old_text)
    merged_parts: list[str] = []
    outside_index = 0
    generated_area_indexes: dict[str, int] = {}

    cursor = 0
    for match in GENERATED_CODE_AREA_PATTERN.finditer(new_text):
        outside_segment, outside_index = merge_safe_areas_in_segment(
            new_text[cursor : match.start()],
            old_outside_areas,
            outside_index,
        )
        merged_parts.append(outside_segment)

        label = match.group("label")
        old_areas = old_generated_area_areas.get(label, [])
        area_index = generated_area_indexes.get(label, 0)
        merged_body, area_index = merge_safe_areas_in_segment(match.group("body"), old_areas, area_index)
        generated_area_indexes[label] = area_index
        merged_parts.append(f"{match.group('start')}{merged_body}{match.group('end')}")
        cursor = match.end()

    tail_segment, outside_index = merge_safe_areas_in_segment(
        new_text[cursor:],
        old_outside_areas,
        outside_index,
    )
    merged_parts.append(tail_segment)
    return "".join(merged_parts)


def format_parameter(param: ParameterSpec) -> str:
    if param.default is None:
        return f"{param.name}: {param.type_name}"
    default = normalize_default_expr(param.default) or "None"
    return f"{param.name}: {param.type_name} = {default}"


def choose_attr_init_expr(attr: AttributeSpec, constructor_param_names: set[str]) -> str:
    if attr.default:
        default = normalize_default_expr(attr.default)
        if default:
            if default in constructor_param_names:
                return default
            return default
    return fallback_default_expr(attr.type_name)


def build_class_index(model: XmiModel) -> dict[str, tuple[str, str]]:
    idx: dict[str, tuple[str, str]] = {}
    for package_name, classes in model.package_to_classes.items():
        for cls in classes:
            idx[cls.name] = (package_name, to_safe_module_name(cls.name))
    return idx


def render_class_file(cls: ClassSpec, class_index: dict[str, tuple[str, str]]) -> str:
    module_name = to_safe_module_name(cls.name)
    imports: list[str] = []

    need_any = False
    need_callable = False
    need_numpy_alias = False
    need_pillow_image_alias = False
    external_imports: set[tuple[str, str]] = set()

    referenced_type_names: set[str] = set()
    type_expressions: list[str] = []
    for attr in cls.attributes:
        type_expressions.append(attr.type_name)
        referenced_type_names.update(extract_annotation_type_names(attr.type_name))
    for method in cls.methods:
        type_expressions.append(method.return_type)
        referenced_type_names.update(extract_annotation_type_names(method.return_type))
        for p in method.parameters:
            type_expressions.append(p.type_name)
            referenced_type_names.update(extract_annotation_type_names(p.type_name))

    base_class = "Enum" if cls.is_enumeration else (cls.base_class_name or "object")
    type_expressions.append(base_class)
    if any(re.search(r"\bAny\b", expr) for expr in type_expressions):
        need_any = True
    if any(re.search(r"\bCallable\b", expr) for expr in type_expressions):
        need_callable = True
    if any("np.ndarray" in expr for expr in type_expressions):
        need_numpy_alias = True
    if any("Image.Image" in expr for expr in type_expressions):
        need_pillow_image_alias = True

    if base_class == "Any":
        need_any = True
    elif base_class == "Callable":
        need_callable = True
    elif base_class not in {"object", "Enum"} and base_class in class_index:
        target_pkg, target_mod = class_index[base_class]
        if not (target_pkg == cls.package_name and target_mod == module_name):
            if target_pkg == cls.package_name:
                external_imports.add((f".{target_mod}", base_class))
            else:
                external_imports.add((f"{target_pkg}.{target_mod}", base_class))

    for type_name in sorted(referenced_type_names):
        if type_name == "Any":
            need_any = True
            continue
        if type_name == cls.name:
            continue
        target = class_index.get(type_name)
        if not target:
            continue
        target_pkg, target_mod = target
        if target_pkg == cls.package_name and target_mod == module_name:
            continue
        if target_pkg == cls.package_name:
            external_imports.add((f".{target_mod}", type_name))
        else:
            external_imports.add((f"{target_pkg}.{target_mod}", type_name))

    out: list[str] = ["from __future__ import annotations\n\n"]
    if cls.is_dataclass:
        imports.append("from dataclasses import dataclass")
    if cls.is_enumeration:
        imports.append("from enum import Enum, auto")
    typing_imports: list[str] = []
    if need_any:
        typing_imports.append("Any")
    if need_callable:
        typing_imports.append("Callable")
    if typing_imports:
        imports.append(f"from typing import {', '.join(typing_imports)}")
    if need_numpy_alias:
        imports.append("import numpy as np")
    if need_pillow_image_alias:
        imports.append("from PIL import Image")
    for module, name in sorted(external_imports):
        imports.append(f"from {module} import {name}")
    import_block: list[str] = []
    if imports:
        for line in imports:
            import_block.append(f"{line}\n")
        append_blank_line(import_block)
    out.extend(render_generated_code_area("", "module.imports", import_block))
    append_blank_line(out)

    out.extend(render_safe_area("", []))
    append_blank_line(out)

    if cls.is_dataclass:
        out.append("@dataclass\n")
    out.append(f"class {cls.name}({base_class}):\n")
    class_header_block: list[str] = []
    if cls.definition:
        class_header_block.extend(render_docstring_block(cls.definition))
        append_blank_line(class_header_block)
    # Class-level safe area allows adding class description/manual class-level code
    # that survives regeneration.
    class_header_block.extend(render_safe_area("    ", []))
    append_blank_line(class_header_block)
    out.extend(render_generated_code_area("    ", "class.header", class_header_block))
    append_blank_line(out)

    if cls.is_enumeration:
        enum_members = [a for a in cls.attributes if a.is_enum_literal]
        enum_block: list[str] = []
        if enum_members:
            for index, member in enumerate(enum_members):
                if member.definition:
                    enum_block.extend(render_comment_block(member.definition, indent="    "))
                enum_block.append(f"    {member.name} = auto()\n")
                if index < len(enum_members) - 1:
                    append_blank_line(enum_block)
            append_blank_line(enum_block)
            enum_block.extend(render_safe_area("    ", ["pass"]))
        else:
            enum_block.extend(render_safe_area("    ", ["pass"]))
        append_blank_line(enum_block)
        out.extend(render_generated_code_area("    ", "enum.members", enum_block))
        append_blank_line(out)
        return "".join(out)

    methods = list(cls.methods)
    attributes = [a for a in cls.attributes if not a.is_enum_literal]

    if cls.is_dataclass:
        attribute_block: list[str] = []
        for attr in attributes:
            if attr.definition:
                attribute_block.extend(render_comment_block(attr.definition, indent="    "))
            default = choose_attr_init_expr(attr, set())
            attribute_block.append(f"    {attr.name}: {attr.type_name} = {default}\n")
            append_blank_line(attribute_block)
        out.extend(render_generated_code_area("    ", "class.attributes", attribute_block))
        append_blank_line(out)
        remaining_methods = [m for m in methods if m.name != "__init__"]
        if remaining_methods:
            for method_index, method in enumerate(remaining_methods):
                method_block: list[str] = []
                params = ", ".join(["self", *(format_parameter(p) for p in method.parameters)])
                method_block.append(f"    def {method.name}({params}) -> {method.return_type}:\n")
                if method.definition:
                    method_block.extend(render_docstring_block(method.definition, indent="        "))
                    append_blank_line(method_block)
                method_block.extend(render_safe_area("        ", ["pass"]))
                out.extend(render_generated_code_area("    ", f"method.{method.name}", method_block))
                if method_index < len(remaining_methods) - 1:
                    out.append("\n")
                    out.append("\n")
                else:
                    out.append("\n")
        else:
            body_block = render_safe_area("    ", ["pass"])
            append_blank_line(body_block)
            out.extend(render_generated_code_area("    ", "class.body", body_block))
            append_blank_line(out)
        return "".join(out)

    if methods:
        for method_index, method in enumerate(methods):
            method_block: list[str] = []
            params = ", ".join(["self", *(format_parameter(p) for p in method.parameters)])
            method_block.append(f"    def {method.name}({params}) -> {method.return_type}:\n")
            if method.definition:
                method_block.extend(render_docstring_block(method.definition, indent="        "))
                append_blank_line(method_block)

            if method.name == "__init__":
                ctor_param_names = {p.name for p in method.parameters}
                for attr_index, attr in enumerate(attributes):
                    if attr.definition:
                        method_block.extend(render_comment_block(attr.definition, indent="        "))
                    init_expr = choose_attr_init_expr(attr, ctor_param_names)
                    method_block.append(f"        self.{attr.name}: {attr.type_name} = {init_expr}\n")
                    if attr_index < len(attributes) - 1:
                        append_blank_line(method_block)
                if attributes:
                    append_blank_line(method_block)
                method_block.extend(render_safe_area("        ", ["pass"]))
            else:
                method_block.extend(render_safe_area("        ", ["pass"]))
            out.extend(render_generated_code_area("    ", f"method.{method.name}", method_block))
            if method_index < len(methods) - 1:
                out.append("\n")
                out.append("\n")
            else:
                out.append("\n")
    elif attributes:
        init_block: list[str] = ["    def __init__(self) -> None:\n"]
        for attr_index, attr in enumerate(attributes):
            if attr.definition:
                init_block.extend(render_comment_block(attr.definition, indent="        "))
            init_expr = choose_attr_init_expr(attr, set())
            init_block.append(f"        self.{attr.name}: {attr.type_name} = {init_expr}\n")
            if attr_index < len(attributes) - 1:
                append_blank_line(init_block)
        if attributes:
            append_blank_line(init_block)
        init_block.extend(render_safe_area("        ", ["pass"]))
        append_blank_line(init_block)
        out.extend(render_generated_code_area("    ", "method.__init__", init_block))
        append_blank_line(out)
    else:
        body_block = render_safe_area("    ", ["pass"])
        append_blank_line(body_block)
        out.extend(render_generated_code_area("    ", "class.body", body_block))
        append_blank_line(out)

    return "".join(out)


def render_package_init(classes: tuple[ClassSpec, ...]) -> str:
    lines: list[str] = ["from __future__ import annotations\n\n"]
    sorted_classes = sorted(classes, key=lambda c: c.name.lower())
    for cls in sorted_classes:
        module = to_safe_module_name(cls.name)
        lines.append(f"from .{module} import {cls.name}\n")
    lines.append("\n")
    exported = ", ".join(f'"{c.name}"' for c in sorted_classes)
    lines.append(f"__all__ = [{exported}]\n")
    return "".join(lines)


def build_output_files(model: XmiModel, output_root: Path) -> dict[Path, str]:
    class_index = build_class_index(model)
    files: dict[Path, str] = {}

    for package_name, classes in model.package_to_classes.items():
        if package_name == "generated":
            continue
        package_dir = output_root / package_name
        files[package_dir / "__init__.py"] = render_package_init(classes)
        for cls in classes:
            module = to_safe_module_name(cls.name)
            files[package_dir / f"{module}.py"] = render_class_file(cls, class_index)
    return files


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("xml", type=Path, help="astah XMI/XML export file")
    parser.add_argument("output", type=Path, help="output directory root")
    parser.add_argument("--write", action="store_true", help="actually create/update files")
    parser.add_argument("--show-diff", action="store_true", help="print unified diffs")
    args = parser.parse_args()

    xml_inputs = discover_input_xmls(args.xml)
    model = merge_models([parse_xmi(path) for path in xml_inputs])
    files = build_output_files(model, args.output)

    changed_count = 0
    for path in sorted(files):
        new_text = files[path]
        old_text = path.read_text(encoding="utf-8") if path.exists() else ""
        if old_text:
            new_text = merge_generated_code_areas(new_text, old_text)
            new_text = merge_safe_areas(new_text, old_text)
        if old_text == new_text:
            continue
        changed_count += 1
        action = "update" if path.exists() else "create"
        print(f"{action}: {path}")
        if args.show_diff:
            print(
                "".join(
                    difflib.unified_diff(
                        old_text.splitlines(keepends=True),
                        new_text.splitlines(keepends=True),
                        fromfile=str(path),
                        tofile=str(path),
                    )
                )
            )
        if args.write:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(new_text, encoding="utf-8")

    mode = "updated" if args.write else "dry-run"
    print(f"{mode}: {changed_count} file(s)")
    if not args.write:
        print("Run again with --write to create/update files.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
