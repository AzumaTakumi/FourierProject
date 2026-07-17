#!/usr/bin/env python3
"""
Generate Python skeleton code directly from astah XMI/XML class model.

Typical usage:
  python generate_python_from_astah_xmi.py FourierSignalModel.xml generated --write
  python generate_python_from_astah_xmi.py FourierSignalModel.xml generated --target-class FourierTransform --show-diff
  python generate_python_from_astah_xmi.py FourierSignalModel.xml generated --target-file Model/fourier_transform.py --write

Without --write, this runs in dry-run mode and only reports planned files.
"""

from __future__ import annotations

import argparse
import ast
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
IMPORT_LINE_PATTERN = re.compile(r"^\s*(?:from\s+\S+\s+import\s+.+|import\s+.+?)\s*(?:#.*)?$")


@dataclass(frozen=True)
class ParameterSpec:
    name: str
    typeName: str
    default: str | None


@dataclass(frozen=True)
class AttributeSpec:
    name: str
    typeName: str
    default: str | None
    definition: str | None
    isEnumLiteral: bool
    isClassScope: bool


@dataclass(frozen=True)
class MethodSpec:
    name: str
    parameters: tuple[ParameterSpec, ...]
    returnType: str
    definition: str | None


@dataclass(frozen=True)
class ClassSpec:
    classId: str
    originalName: str
    name: str
    packageName: str
    definition: str | None
    baseClassName: str | None
    isEnumeration: bool
    isDataclass: bool
    attributes: tuple[AttributeSpec, ...]
    methods: tuple[MethodSpec, ...]


@dataclass(frozen=True)
class XmiModel:
    packageToClasses: dict[str, tuple[ClassSpec, ...]]


@dataclass(frozen=True)
class OutputFileSpec:
    path: Path
    text: str
    packageName: str
    className: str | None
    originalClassName: str | None
    moduleName: str | None


@dataclass(frozen=True)
class GeneratedCodeArea:
    label: str
    state: str
    start: str
    body: str
    end: str


def localName(tag: str) -> str:
    if "}" in tag:
        return tag.rsplit("}", 1)[1]
    if ":" in tag:
        return tag.rsplit(":", 1)[1]
    return tag


def xmiAttr(elem: ET.Element, name: str) -> str | None:
    return elem.attrib.get(f"xmi.{name}") or elem.attrib.get(name)


def directChildrenByLocal(elem: ET.Element, local: str) -> list[ET.Element]:
    return [c for c in list(elem) if localName(c.tag) == local]


def childClassifierIdref(elem: ET.Element) -> str | None:
    for child in elem.iter():
        if localName(child.tag) == "Classifier":
            return xmiAttr(child, "idref")
    return None


def decodeAstahText(value: str | None) -> str | None:
    if value is None:
        return None
    text = urllib.parse.unquote_plus(value).strip()
    return text or None


def decodeAstahName(value: str | None) -> str | None:
    return decodeAstahText(value)


def readDefinition(elem: ET.Element) -> str | None:
    for defNode in directChildrenByLocal(elem, "ModelElement.definition"):
        text = decodeAstahText(defNode.attrib.get("xmi.value") or defNode.attrib.get("value"))
        if text:
            return text
    return None


def parseParamName(rawName: str | None) -> tuple[str, str | None]:
    decoded = decodeAstahName(rawName) or ""
    if "=" in decoded:
        name, default = decoded.split("=", 1)
        return name.strip(), default.strip()
    return decoded, None


def toSafeIdentifier(name: str, fallback: str = "value") -> str:
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


def normalizeType(
    typeName: str | None,
    classNameMap: dict[str, str],
    default: str | None = None,
) -> str:
    decodedType = decodeAstahName(typeName)
    if not decodedType:
        pyType = "Any"
    else:
        pyType = TYPE_MAP.get(decodedType)
        if pyType is None:
            pyType = normalizeCollectionTypeName(decodedType)
        if pyType is None:
            pyType = classNameMap.get(decodedType, toSafeIdentifier(decodedType, fallback="Any"))
    if default is not None and default.strip() in NONE_LITERALS and pyType != "None":
        return f"{pyType} | None"
    return pyType


def isExternalModelType(className: str) -> bool:
    normalized = decodeAstahName(className) or ""
    lower = normalized.strip().lower()
    if lower in EXTERNAL_MODEL_TYPE_NAMES:
        return True
    compact = re.sub(r"\s+", "", lower)
    return any(compact.startswith(prefix) for prefix in EXTERNAL_GENERIC_PREFIXES)


def normalizeCollectionTypeName(typeName: str) -> str | None:
    compact = re.sub(r"\s+", "", typeName).lower()
    if compact.startswith(("list[", "list<")):
        return "list"
    if compact.startswith(("dict[", "dict<")):
        return "dict"
    if compact.startswith(("set[", "set<")):
        return "set"
    if compact.startswith(("tuple[", "tuple<")):
        return "tuple"
    return None


def normalizeDefaultExpr(value: str | None) -> str | None:
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


def fallbackDefaultExpr(typeName: str) -> str:
    if typeName == "None":
        return "None"
    if "| None" in typeName:
        return "None"
    if typeName == "bool":
        return "False"
    if typeName == "int":
        return "0"
    if typeName == "float":
        return "0.0"
    if typeName == "str":
        return "''"
    if typeName == "list":
        return "[]"
    if typeName == "dict":
        return "{}"
    if typeName == "set":
        return "set()"
    if typeName == "tuple":
        return "()"
    return "None"


def parseInitialValue(attr: ET.Element) -> str | None:
    for initNode in directChildrenByLocal(attr, "Attribute.initialValue"):
        for exprNode in initNode.iter():
            if localName(exprNode.tag) == "Expression.body":
                return normalizeDefaultExpr(exprNode.text)
    return None


def collectClassifierNames(root: ET.Element) -> dict[str, str]:
    idToName: dict[str, str] = {}
    for elem in root.iter():
        if localName(elem.tag) in {"Class", "Interface", "DataType", "Primitive", "Enumeration"}:
            xid = xmiAttr(elem, "id")
            name = decodeAstahName(elem.attrib.get("name"))
            if xid and name:
                idToName[xid] = name
    return idToName


def collectPackageNames(root: ET.Element) -> dict[str, str]:
    idToName: dict[str, str] = {}
    for elem in root.iter():
        if localName(elem.tag) == "Package":
            xid = xmiAttr(elem, "id")
            name = decodeAstahName(elem.attrib.get("name"))
            if xid and name:
                idToName[xid] = name
    return idToName


def collectGeneralizationMap(root: ET.Element) -> dict[str, str]:
    childToParent: dict[str, str] = {}
    for gen in root.iter():
        if localName(gen.tag) != "Generalization":
            continue
        genId = xmiAttr(gen, "id")
        if not genId:
            continue
        childId = None
        parentId = None
        for childSection in directChildrenByLocal(gen, "Generalization.child"):
            for ge in childSection.iter():
                if localName(ge.tag) == "GeneralizableElement":
                    childId = xmiAttr(ge, "idref")
        for parentSection in directChildrenByLocal(gen, "Generalization.parent"):
            for ge in parentSection.iter():
                if localName(ge.tag) == "GeneralizableElement":
                    parentId = xmiAttr(ge, "idref")
        if childId and parentId:
            childToParent[childId] = parentId
    return childToParent


def collectStereotypeNames(root: ET.Element) -> dict[str, str]:
    idToName: dict[str, str] = {}
    for elem in root.iter():
        if localName(elem.tag) != "Stereotype":
            continue
        sid = xmiAttr(elem, "id")
        name = decodeAstahName(elem.attrib.get("name"))
        if sid and name:
            idToName[sid] = name
    return idToName


def collectDependencyEndpointId(elem: ET.Element, endpointLocal: str) -> str | None:
    for section in directChildrenByLocal(elem, endpointLocal):
        for child in section.iter():
            cid = xmiAttr(child, "idref")
            if cid:
                return cid
    return None


def isRealizeUsage(usage: ET.Element, stereotypeNames: dict[str, str]) -> bool:
    for stContainer in directChildrenByLocal(usage, "ModelElement.stereotype"):
        for stElem in stContainer.iter():
            if localName(stElem.tag) != "Stereotype":
                continue
            sid = xmiAttr(stElem, "idref")
            if not sid:
                continue
            if stereotypeNames.get(sid, "").lower() == "realize":
                return True
    return False


def classHasStereotype(elem: ET.Element, stereotypeName: str, stereotypeNames: dict[str, str]) -> bool:
    expected = stereotypeName.lower()
    for stContainer in directChildrenByLocal(elem, "ModelElement.stereotype"):
        for stElem in stContainer.iter():
            if localName(stElem.tag) != "Stereotype":
                continue
            sid = xmiAttr(stElem, "idref")
            if not sid:
                continue
            if stereotypeNames.get(sid, "").lower() == expected:
                return True
    return False


def collectRealizationMap(root: ET.Element) -> dict[str, str]:
    stereotypeNames = collectStereotypeNames(root)
    clientToSupplier: dict[str, str] = {}
    for usage in root.iter():
        if localName(usage.tag) != "Usage":
            continue
        usageId = xmiAttr(usage, "id")
        if not usageId:
            # Skip xmi.idref references under diagram presentation trees.
            continue
        if not isRealizeUsage(usage, stereotypeNames):
            continue
        clientId = collectDependencyEndpointId(usage, "Dependency.client")
        supplierId = collectDependencyEndpointId(usage, "Dependency.supplier")
        if clientId and supplierId:
            clientToSupplier[clientId] = supplierId
    return clientToSupplier


def getVisibility(elem: ET.Element) -> str | None:
    visibility = elem.attrib.get("visibility")
    if visibility:
        return visibility
    for visNode in directChildrenByLocal(elem, "ModelElement.visibility"):
        value = visNode.attrib.get("xmi.value") or visNode.attrib.get("value")
        if value:
            return value
    return None


def hasTaggedValue(elem: ET.Element, tag: str, value: str | None = None) -> bool:
    for tvContainer in directChildrenByLocal(elem, "ModelElement.taggedValue"):
        for tagged in directChildrenByLocal(tvContainer, "TaggedValue"):
            if tagged.attrib.get("tag") != tag:
                continue
            if value is None or tagged.attrib.get("value") == value:
                return True
    return False


def collectNamespaceId(elem: ET.Element) -> str | None:
    for nsContainer in directChildrenByLocal(elem, "ModelElement.namespace"):
        for ns in nsContainer.iter():
            if localName(ns.tag) == "Namespace":
                return xmiAttr(ns, "idref")
    return None


def parseXmi(xmlPath: Path) -> XmiModel:
    root = ET.parse(xmlPath).getroot()
    idToName = collectClassifierNames(root)
    classifierPyNames = {name: toSafeIdentifier(name, fallback="TypeName") for name in set(idToName.values())}
    packageIdToName = collectPackageNames(root)
    childToParentId = collectGeneralizationMap(root)
    childToInterfaceId = collectRealizationMap(root)
    stereotypeNames = collectStereotypeNames(root)

    packageToClasses: dict[str, list[ClassSpec]] = {}

    for cls in root.iter():
        if localName(cls.tag) not in {"Class", "Interface"}:
            continue
        classId = xmiAttr(cls, "id")
        classNameRaw = decodeAstahName(cls.attrib.get("name"))
        className = toSafeIdentifier(classNameRaw or "", fallback="GeneratedClass")
        if not classId or not classNameRaw:
            continue
        if isExternalModelType(classNameRaw):
            continue

        packageId = collectNamespaceId(cls)
        packageName = packageIdToName.get(packageId or "", "generated")
        classDefinition = readDefinition(cls)
        isEnumeration = hasTaggedValue(cls, "jude.enumeration", "true")
        isDataclass = classHasStereotype(cls, "dataclass", stereotypeNames)

        attributes: list[AttributeSpec] = []
        methods: list[MethodSpec] = []

        for feature in directChildrenByLocal(cls, "Classifier.feature"):
            for attr in directChildrenByLocal(feature, "Attribute"):
                attrName = decodeAstahName(attr.attrib.get("name"))
                if not attrName:
                    continue
                attrName = toSafeIdentifier(attrName)

                typeRef = None
                for typeNode in directChildrenByLocal(attr, "StructuralFeature.type"):
                    typeRef = childClassifierIdref(typeNode)
                umlType = idToName.get(typeRef or "")

                defaultValue = parseInitialValue(attr)
                attrType = normalizeType(umlType, classifierPyNames, defaultValue)
                attrDefinition = readDefinition(attr)
                isEnumLiteral = hasTaggedValue(attr, "jude.enumeration_literal", "true")
                isClassScope = attr.attrib.get("ownerScope") == "classifier"

                attributes.append(
                    AttributeSpec(
                        name=attrName,
                        typeName=attrType,
                        default=defaultValue,
                        definition=attrDefinition,
                        isEnumLiteral=isEnumLiteral,
                        isClassScope=isClassScope,
                    )
                )

            for op in directChildrenByLocal(feature, "Operation"):
                methodName = decodeAstahName(op.attrib.get("name"))
                if not methodName:
                    continue
                if getVisibility(op) == "protected" and not methodName.startswith("_"):
                    methodName = f"_{methodName}"
                methodName = toSafeIdentifier(methodName, fallback="method")

                params: list[ParameterSpec] = []
                returnType = "None"

                for bfParam in directChildrenByLocal(op, "BehavioralFeature.parameter"):
                    for param in directChildrenByLocal(bfParam, "Parameter"):
                        kind = param.attrib.get("kind")
                        typeRef = None
                        for typeNode in directChildrenByLocal(param, "Parameter.type"):
                            typeRef = childClassifierIdref(typeNode)
                        umlType = idToName.get(typeRef or "")

                        if kind == "return":
                            returnType = normalizeType(umlType, classifierPyNames)
                            continue
                        if kind not in {"in", "inout", "out"}:
                            continue

                        name, default = parseParamName(param.attrib.get("name"))
                        if not name:
                            continue
                        params.append(
                            ParameterSpec(
                                name=toSafeIdentifier(name),
                                typeName=normalizeType(umlType, classifierPyNames, default),
                                default=default,
                            )
                        )

                methods.append(
                    MethodSpec(
                        name=methodName,
                        parameters=tuple(params),
                        returnType=returnType,
                        definition=readDefinition(op),
                    )
                )

        baseClassName = None
        parentId = childToParentId.get(classId)
        if not parentId:
            parentId = childToInterfaceId.get(classId)
        if parentId:
            baseRaw = idToName.get(parentId)
            if baseRaw:
                baseClassName = classifierPyNames.get(baseRaw, toSafeIdentifier(baseRaw, fallback="BaseClass"))

        packageToClasses.setdefault(packageName, []).append(
            ClassSpec(
                classId=classId,
                originalName=classNameRaw,
                name=className,
                packageName=packageName,
                definition=classDefinition,
                baseClassName=baseClassName,
                isEnumeration=isEnumeration,
                isDataclass=isDataclass,
                attributes=tuple(attributes),
                methods=tuple(methods),
            )
        )

    frozen = {pkg: tuple(sorted(classes, key=lambda c: c.name.lower())) for pkg, classes in packageToClasses.items()}
    return XmiModel(packageToClasses=frozen)


def discoverInputXmls(xmlPath: Path) -> list[Path]:
    basePath = xmlPath.resolve()
    prefix = basePath.stem
    related = [
        candidate.resolve()
        for candidate in basePath.parent.glob(f"{prefix}*.xml")
        if candidate.resolve() != basePath
    ]
    return [basePath, *sorted(related, key=lambda path: path.name.lower())]


def mergeModels(models: list[XmiModel]) -> XmiModel:
    merged: dict[str, dict[str, ClassSpec]] = {}
    for model in models:
        for packageName, classes in model.packageToClasses.items():
            packageClasses = merged.setdefault(packageName, {})
            for cls in classes:
                packageClasses.setdefault(cls.name, cls)

    return XmiModel(
        packageToClasses={
            packageName: tuple(sorted(packageClasses.values(), key=lambda cls: cls.name.lower()))
            for packageName, packageClasses in merged.items()
        }
    )


def toSafeModuleName(className: str) -> str:
    text = re.sub(r"[^0-9A-Za-z_]", "_", className)
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


def extractAnnotationTypeNames(typeExpr: str) -> set[str]:
    names = set(re.findall(r"\b[A-Za-z_]\w*\b", typeExpr))
    return {n for n in names if n not in BUILTIN_TYPE_NAMES}


def renderDocstringBlock(doc: str, indent: str = "    ") -> list[str]:
    safe = doc.replace('"""', '\\"\\"\\"')
    lines = safe.splitlines()
    out = [f'{indent}"""\n']
    for line in lines:
        out.append(f"{indent}{line}\n")
    out.append(f'{indent}"""\n')
    return out


def renderCommentBlock(doc: str, indent: str = "    ") -> list[str]:
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


def renderSafeArea(indent: str, defaultBodyLines: list[str]) -> list[str]:
    out = [f"{indent}# SAFE CODE AREA ˅\n"]
    for line in defaultBodyLines:
        out.append(f"{indent}{line}\n")
    out.append(f"{indent}# SAFE CODE AREA ˄\n")
    return out


def renderGeneratedCodeArea(indent: str, label: str, bodyLines: list[str]) -> list[str]:
    out = [f"{indent}# GENERATED CODE AREA: {label} ˅\n"]
    out.extend(bodyLines)
    out.append(f"{indent}# GENERATED CODE AREA: {label} ˄\n")
    return out


def appendBlankLine(out: list[str]) -> None:
    if not out:
        out.append("\n")
        return
    if out[-1] != "\n":
        out.append("\n")


def extractSafeAreas(text: str) -> list[str]:
    areas: list[str] = []
    for m in SAFE_AREA_PATTERN.finditer(text):
        areas.append(m.group("body"))
    return areas


def extractSafeAreasByContext(text: str) -> tuple[list[str], dict[str, list[str]]]:
    outsideAreas: list[str] = []
    generatedAreaSafeAreas: dict[str, list[str]] = {}

    cursor = 0
    for match in GENERATED_CODE_AREA_PATTERN.finditer(text):
        outsideAreas.extend(extractSafeAreas(text[cursor : match.start()]))
        label = match.group("label")
        generatedAreaSafeAreas.setdefault(label, []).extend(extractSafeAreas(match.group("body")))
        cursor = match.end()

    outsideAreas.extend(extractSafeAreas(text[cursor:]))
    return outsideAreas, generatedAreaSafeAreas


def mergeSafeAreasInSegment(newSegment: str, oldAreas: list[str], startIndex: int) -> tuple[str, int]:
    index = startIndex

    def _replace(match: re.Match[str]) -> str:
        nonlocal index
        if index >= len(oldAreas):
            return match.group(0)
        oldBody = oldAreas[index]
        index += 1
        if oldBody.strip() == SAFE_AREA_DEFAULT_PLACEHOLDER:
            oldBody = ""
        return f"{match.group('start')}{oldBody}{match.group('end')}"

    return SAFE_AREA_PATTERN.sub(_replace, newSegment), index


def extractGeneratedCodeAreas(text: str) -> dict[str, GeneratedCodeArea]:
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


def mergeGeneratedCodeAreas(newText: str, oldText: str) -> tuple[str, list[str]]:
    oldAreas = extractGeneratedCodeAreas(oldText)
    blockedLabels: list[str] = []

    def _replace(match: re.Match[str]) -> str:
        label = match.group("label")
        oldArea = oldAreas.get(label)
        if oldArea is None or oldArea.state != "FIXED":
            return match.group(0)
        if oldArea.body != match.group("body") and label not in blockedLabels:
            blockedLabels.append(label)
        return f"{oldArea.start}{oldArea.body}{oldArea.end}"

    merged = GENERATED_CODE_AREA_PATTERN.sub(_replace, newText)
    return merged, blockedLabels


def mergeSafeAreas(newText: str, oldText: str) -> str:
    oldOutsideAreas, oldGeneratedAreaAreas = extractSafeAreasByContext(oldText)
    mergedParts: list[str] = []
    outsideIndex = 0
    generatedAreaIndexes: dict[str, int] = {}

    cursor = 0
    for match in GENERATED_CODE_AREA_PATTERN.finditer(newText):
        outsideSegment, outsideIndex = mergeSafeAreasInSegment(
            newText[cursor : match.start()],
            oldOutsideAreas,
            outsideIndex,
        )
        mergedParts.append(outsideSegment)

        label = match.group("label")
        oldAreas = oldGeneratedAreaAreas.get(label, [])
        areaIndex = generatedAreaIndexes.get(label, 0)
        mergedBody, areaIndex = mergeSafeAreasInSegment(match.group("body"), oldAreas, areaIndex)
        generatedAreaIndexes[label] = areaIndex
        mergedParts.append(f"{match.group('start')}{mergedBody}{match.group('end')}")
        cursor = match.end()

    tailSegment, outsideIndex = mergeSafeAreasInSegment(
        newText[cursor:],
        oldOutsideAreas,
        outsideIndex,
    )
    mergedParts.append(tailSegment)
    return "".join(mergedParts)


def importedNamesFromLine(line: str) -> set[str]:
    if not IMPORT_LINE_PATTERN.match(line):
        return set()
    try:
        module = ast.parse(line)
    except SyntaxError:
        return set()

    names: set[str] = set()
    for node in module.body:
        if isinstance(node, ast.Import):
            for alias in node.names:
                names.add(alias.asname or alias.name.split(".", 1)[0])
        elif isinstance(node, ast.ImportFrom):
            for alias in node.names:
                if alias.name == "*":
                    continue
                names.add(alias.asname or alias.name)
    return names


def extractModuleImportLines(text: str) -> list[str]:
    area = extractGeneratedCodeAreas(text).get("module.imports")
    if area is None:
        return []
    importLines: list[str] = []
    seen: set[str] = set()
    for line in area.body.splitlines():
        stripped = line.strip()
        if not stripped or stripped in seen:
            continue
        if importedNamesFromLine(stripped):
            importLines.append(stripped)
            seen.add(stripped)
    return importLines


def removeGeneratedArea(text: str, label: str) -> str:
    parts: list[str] = []
    cursor = 0
    for match in GENERATED_CODE_AREA_PATTERN.finditer(text):
        if match.group("label") == label:
            parts.append(text[cursor : match.start()])
            cursor = match.end()
    parts.append(text[cursor:])
    return "".join(parts)


def textReferencesImportedName(text: str, names: set[str]) -> bool:
    return any(re.search(rf"\b{re.escape(name)}\b", text) for name in names)


def appendModuleImportLines(text: str, importLines: list[str]) -> str:
    if not importLines:
        return text

    def _replace(match: re.Match[str]) -> str:
        if match.group("label") != "module.imports":
            return match.group(0)

        bodyLines = match.group("body").splitlines(keepends=True)
        while bodyLines and not bodyLines[-1].strip():
            bodyLines.pop()

        existing = {line.strip() for line in bodyLines if line.strip()}
        for importLine in importLines:
            if importLine not in existing:
                bodyLines.append(f"{importLine}\n")
                existing.add(importLine)
        if bodyLines:
            bodyLines.append("\n")
        return f"{match.group('start')}{''.join(bodyLines)}{match.group('end')}"

    return GENERATED_CODE_AREA_PATTERN.sub(_replace, text)


def preserveReferencedModuleImports(newText: str, oldText: str) -> str:
    oldImports = extractModuleImportLines(oldText)
    if not oldImports:
        return newText

    currentImports = set(extractModuleImportLines(newText))
    referenceText = removeGeneratedArea(newText, "module.imports")
    importsToPreserve: list[str] = []
    for importLine in oldImports:
        if importLine in currentImports:
            continue
        if textReferencesImportedName(referenceText, importedNamesFromLine(importLine)):
            importsToPreserve.append(importLine)
    return appendModuleImportLines(newText, importsToPreserve)


def extractChangedGeneratedAreaLabels(oldText: str, newText: str) -> list[str]:
    oldAreas = extractGeneratedCodeAreas(oldText)
    newAreas = extractGeneratedCodeAreas(newText)
    changed: list[str] = []
    for label in sorted(set(oldAreas) & set(newAreas)):
        if oldAreas[label].body != newAreas[label].body:
            changed.append(label)
    return changed


def summarizeChangedLabels(changedLabels: list[str]) -> dict[str, list[str]]:
    methods: list[str] = []
    sections: list[str] = []
    seenMethods: set[str] = set()
    seenSections: set[str] = set()

    for label in changedLabels:
        if label.startswith("method."):
            methodName = label.split(".", 1)[1]
            if methodName not in seenMethods:
                seenMethods.add(methodName)
                methods.append(methodName)
            continue
        if label not in seenSections:
            seenSections.add(label)
            sections.append(label)

    return {
        "methods": methods,
        "sections": sections,
    }


def extractOutsideGeneratedText(text: str) -> str:
    parts: list[str] = []
    cursor = 0
    for match in GENERATED_CODE_AREA_PATTERN.finditer(text):
        parts.append(text[cursor : match.start()])
        cursor = match.end()
    parts.append(text[cursor:])
    return "".join(parts)


def summarizeNonGeneratedChanges(oldText: str, newText: str) -> dict[str, str]:
    oldSafe = extractSafeAreas(oldText)
    newSafe = extractSafeAreas(newText)
    safeChanged = oldSafe != newSafe

    oldOutside = extractOutsideGeneratedText(oldText)
    newOutside = extractOutsideGeneratedText(newText)
    outsideChanged = oldOutside != newOutside

    whitespaceOnly = (
        oldText != newText
        and re.sub(r"\s+", "", oldText) == re.sub(r"\s+", "", newText)
    )

    return {
        "safe_areas": "changed" if safeChanged else "unchanged",
        "outside_generated": "changed" if outsideChanged else "unchanged",
        "whitespace": "changed-only" if whitespaceOnly else "not-only",
    }


def isSingleBlankLineAddition(oldText: str, newText: str) -> bool:
    if oldText == newText:
        return False

    oldLines = oldText.splitlines(keepends=True)
    newLines = newText.splitlines(keepends=True)
    matcher = difflib.SequenceMatcher(a=oldLines, b=newLines)

    blankAdded = 0
    for tag, _, _, j1, j2 in matcher.get_opcodes():
        if tag == "equal":
            continue
        if tag != "insert":
            return False
        for line in newLines[j1:j2]:
            if line.strip():
                return False
            blankAdded += 1
            if blankAdded > 1:
                return False
    return blankAdded == 1


def isWhitespaceOnlyChange(oldText: str, newText: str) -> bool:
    return (
        oldText != newText
        and re.sub(r"\s+", "", oldText) == re.sub(r"\s+", "", newText)
    )


def formatParameter(param: ParameterSpec) -> str:
    if param.default is None:
        return f"{param.name}: {param.typeName}"
    default = normalizeDefaultExpr(param.default) or "None"
    return f"{param.name}: {param.typeName} = {default}"


def chooseAttrInitExpr(attr: AttributeSpec, constructorParamNames: set[str]) -> str:
    if attr.default:
        default = normalizeDefaultExpr(attr.default)
        if default:
            if default in constructorParamNames:
                return default
            return default
    return fallbackDefaultExpr(attr.typeName)


def buildClassIndex(model: XmiModel) -> dict[str, tuple[str, str]]:
    idx: dict[str, tuple[str, str]] = {}
    for packageName, classes in model.packageToClasses.items():
        for cls in classes:
            idx[cls.name] = (packageName, toSafeModuleName(cls.name))
    return idx


def renderClassFile(cls: ClassSpec, classIndex: dict[str, tuple[str, str]]) -> str:
    moduleName = toSafeModuleName(cls.name)
    imports: list[str] = []

    needAny = False
    needCallable = False
    needNumpyAlias = False
    needPillowImageAlias = False
    externalImports: set[tuple[str, str]] = set()

    referencedTypeNames: set[str] = set()
    typeExpressions: list[str] = []
    for attr in cls.attributes:
        typeExpressions.append(attr.typeName)
        referencedTypeNames.update(extractAnnotationTypeNames(attr.typeName))
    for method in cls.methods:
        typeExpressions.append(method.returnType)
        referencedTypeNames.update(extractAnnotationTypeNames(method.returnType))
        for p in method.parameters:
            typeExpressions.append(p.typeName)
            referencedTypeNames.update(extractAnnotationTypeNames(p.typeName))

    baseClass = "Enum" if cls.isEnumeration else (cls.baseClassName or "object")
    typeExpressions.append(baseClass)
    if any(re.search(r"\bAny\b", expr) for expr in typeExpressions):
        needAny = True
    if any(re.search(r"\bCallable\b", expr) for expr in typeExpressions):
        needCallable = True
    if any("np.ndarray" in expr for expr in typeExpressions):
        needNumpyAlias = True
    if any("Image.Image" in expr for expr in typeExpressions):
        needPillowImageAlias = True

    if baseClass == "Any":
        needAny = True
    elif baseClass == "Callable":
        needCallable = True
    elif baseClass not in {"object", "Enum"} and baseClass in classIndex:
        targetPkg, targetMod = classIndex[baseClass]
        if not (targetPkg == cls.packageName and targetMod == moduleName):
            if targetPkg == cls.packageName:
                externalImports.add((f".{targetMod}", baseClass))
            else:
                externalImports.add((f"{targetPkg}.{targetMod}", baseClass))

    for typeName in sorted(referencedTypeNames):
        if typeName == "Any":
            needAny = True
            continue
        if typeName == cls.name:
            continue
        target = classIndex.get(typeName)
        if not target:
            continue
        targetPkg, targetMod = target
        if targetPkg == cls.packageName and targetMod == moduleName:
            continue
        if targetPkg == cls.packageName:
            externalImports.add((f".{targetMod}", typeName))
        else:
            externalImports.add((f"{targetPkg}.{targetMod}", typeName))

    out: list[str] = ["from __future__ import annotations\n\n"]
    if cls.isDataclass:
        imports.append("from dataclasses import dataclass")
    if cls.isEnumeration:
        imports.append("from enum import Enum, auto")
    typingImports: list[str] = []
    if needAny:
        typingImports.append("Any")
    if needCallable:
        typingImports.append("Callable")
    if typingImports:
        imports.append(f"from typing import {', '.join(typingImports)}")
    if needNumpyAlias:
        imports.append("import numpy as np")
    if needPillowImageAlias:
        imports.append("from PIL import Image")
    for module, name in sorted(externalImports):
        imports.append(f"from {module} import {name}")
    importBlock: list[str] = []
    if imports:
        for line in imports:
            importBlock.append(f"{line}\n")
        appendBlankLine(importBlock)
    out.extend(renderGeneratedCodeArea("", "module.imports", importBlock))
    appendBlankLine(out)

    out.extend(renderSafeArea("", []))
    appendBlankLine(out)

    if cls.isDataclass:
        out.append("@dataclass\n")
    out.append(f"class {cls.name}({baseClass}):\n")
    classHeaderBlock: list[str] = []
    if cls.definition:
        classHeaderBlock.extend(renderDocstringBlock(cls.definition))
        appendBlankLine(classHeaderBlock)
    # Class-level safe area allows adding class description/manual class-level code
    # that survives regeneration.
    classHeaderBlock.extend(renderSafeArea("    ", []))
    appendBlankLine(classHeaderBlock)
    out.extend(renderGeneratedCodeArea("    ", "class.header", classHeaderBlock))
    appendBlankLine(out)

    if cls.isEnumeration:
        enumMembers = [a for a in cls.attributes if a.isEnumLiteral]
        enumBlock: list[str] = []
        if enumMembers:
            for index, member in enumerate(enumMembers):
                if member.definition:
                    enumBlock.extend(renderCommentBlock(member.definition, indent="    "))
                enumBlock.append(f"    {member.name} = auto()\n")
                if index < len(enumMembers) - 1:
                    appendBlankLine(enumBlock)
            appendBlankLine(enumBlock)
            enumBlock.extend(renderSafeArea("    ", ["pass"]))
        else:
            enumBlock.extend(renderSafeArea("    ", ["pass"]))
        appendBlankLine(enumBlock)
        out.extend(renderGeneratedCodeArea("    ", "enum.members", enumBlock))
        appendBlankLine(out)
        return "".join(out)

    methods = list(cls.methods)
    attributes = [a for a in cls.attributes if not a.isEnumLiteral]
    instanceAttributes = [a for a in attributes if not a.isClassScope]

    if cls.isDataclass:
        attributeBlock: list[str] = []
        for attr in instanceAttributes:
            if attr.definition:
                attributeBlock.extend(renderCommentBlock(attr.definition, indent="    "))
            default = chooseAttrInitExpr(attr, set())
            attributeBlock.append(f"    {attr.name}: {attr.typeName} = {default}\n")
            appendBlankLine(attributeBlock)
        if attributeBlock:
            out.extend(renderGeneratedCodeArea("    ", "class.attributes", attributeBlock))
            appendBlankLine(out)
        remainingMethods = [m for m in methods if m.name != "__init__"]
        if remainingMethods:
            for methodIndex, method in enumerate(remainingMethods):
                methodBlock: list[str] = []
                params = ", ".join(["self", *(formatParameter(p) for p in method.parameters)])
                methodBlock.append(f"    def {method.name}({params}) -> {method.returnType}:\n")
                if method.definition:
                    methodBlock.extend(renderDocstringBlock(method.definition, indent="        "))
                    appendBlankLine(methodBlock)
                methodBlock.extend(renderSafeArea("        ", ["pass"]))
                out.extend(renderGeneratedCodeArea("    ", f"method.{method.name}", methodBlock))
                if methodIndex < len(remainingMethods) - 1:
                    out.append("\n")
                    out.append("\n")
                else:
                    out.append("\n")
        else:
            bodyBlock = renderSafeArea("    ", ["pass"])
            appendBlankLine(bodyBlock)
            out.extend(renderGeneratedCodeArea("    ", "class.body", bodyBlock))
            appendBlankLine(out)
        return "".join(out)

    if methods:
        ctor = next((m for m in methods if m.name == "__init__"), None)
        remainingMethods = [m for m in methods if m.name != "__init__"]

        if ctor is None and instanceAttributes:
            initBlock: list[str] = ["    def __init__(self) -> None:\n"]
            for attrIndex, attr in enumerate(instanceAttributes):
                if attr.definition:
                    initBlock.extend(renderCommentBlock(attr.definition, indent="        "))
                initExpr = chooseAttrInitExpr(attr, set())
                initBlock.append(f"        self.{attr.name}: {attr.typeName} = {initExpr}\n")
                if attrIndex < len(instanceAttributes) - 1:
                    appendBlankLine(initBlock)
            appendBlankLine(initBlock)
            initBlock.extend(renderSafeArea("        ", ["pass"]))
            appendBlankLine(initBlock)
            out.extend(renderGeneratedCodeArea("    ", "method.__init__", initBlock))
            appendBlankLine(out)

        renderedMethods = [ctor] if ctor is not None else []
        renderedMethods.extend(remainingMethods)

        for methodIndex, method in enumerate(renderedMethods):
            if method is None:
                continue
            methodBlock: list[str] = []
            params = ", ".join(["self", *(formatParameter(p) for p in method.parameters)])
            methodBlock.append(f"    def {method.name}({params}) -> {method.returnType}:\n")
            if method.definition:
                methodBlock.extend(renderDocstringBlock(method.definition, indent="        "))
                appendBlankLine(methodBlock)

            if method.name == "__init__":
                ctorParamNames = {p.name for p in method.parameters}
                for attrIndex, attr in enumerate(instanceAttributes):
                    if attr.definition:
                        methodBlock.extend(renderCommentBlock(attr.definition, indent="        "))
                    initExpr = chooseAttrInitExpr(attr, ctorParamNames)
                    methodBlock.append(f"        self.{attr.name}: {attr.typeName} = {initExpr}\n")
                    if attrIndex < len(instanceAttributes) - 1:
                        appendBlankLine(methodBlock)
                if instanceAttributes:
                    appendBlankLine(methodBlock)
                methodBlock.extend(renderSafeArea("        ", ["pass"]))
            else:
                methodBlock.extend(renderSafeArea("        ", ["pass"]))
            out.extend(renderGeneratedCodeArea("    ", f"method.{method.name}", methodBlock))
            if methodIndex < len(renderedMethods) - 1:
                out.append("\n")
                out.append("\n")
            else:
                out.append("\n")
    elif instanceAttributes:
        initBlock: list[str] = ["    def __init__(self) -> None:\n"]
        for attrIndex, attr in enumerate(instanceAttributes):
            if attr.definition:
                initBlock.extend(renderCommentBlock(attr.definition, indent="        "))
            initExpr = chooseAttrInitExpr(attr, set())
            initBlock.append(f"        self.{attr.name}: {attr.typeName} = {initExpr}\n")
            if attrIndex < len(instanceAttributes) - 1:
                appendBlankLine(initBlock)
        if instanceAttributes:
            appendBlankLine(initBlock)
        initBlock.extend(renderSafeArea("        ", ["pass"]))
        appendBlankLine(initBlock)
        out.extend(renderGeneratedCodeArea("    ", "method.__init__", initBlock))
        appendBlankLine(out)
    else:
        bodyBlock = renderSafeArea("    ", ["pass"])
        appendBlankLine(bodyBlock)
        out.extend(renderGeneratedCodeArea("    ", "class.body", bodyBlock))
        appendBlankLine(out)

    return "".join(out)


def renderPackageInit(classes: tuple[ClassSpec, ...]) -> str:
    lines: list[str] = ["from __future__ import annotations\n\n"]
    sortedClasses = sorted(classes, key=lambda c: c.name.lower())
    for cls in sortedClasses:
        module = toSafeModuleName(cls.name)
        lines.append(f"from .{module} import {cls.name}\n")
    lines.append("\n")
    exported = ", ".join(f'"{c.name}"' for c in sortedClasses)
    lines.append(f"__all__ = [{exported}]\n")
    return "".join(lines)


def buildOutputFileSpecs(model: XmiModel, outputRoot: Path) -> tuple[OutputFileSpec, ...]:
    classIndex = buildClassIndex(model)
    specs: list[OutputFileSpec] = []

    for packageName, classes in model.packageToClasses.items():
        if packageName == "generated":
            continue
        packageDir = outputRoot / packageName
        specs.append(
            OutputFileSpec(
                path=packageDir / "__init__.py",
                text=renderPackageInit(classes),
                packageName=packageName,
                className=None,
                originalClassName=None,
                moduleName="__init__",
            )
        )
        for cls in classes:
            module = toSafeModuleName(cls.name)
            specs.append(
                OutputFileSpec(
                    path=packageDir / f"{module}.py",
                    text=renderClassFile(cls, classIndex),
                    packageName=packageName,
                    className=cls.name,
                    originalClassName=cls.originalName,
                    moduleName=module,
                )
            )
    return tuple(specs)


def buildOutputFiles(model: XmiModel, outputRoot: Path) -> dict[Path, str]:
    return {spec.path: spec.text for spec in buildOutputFileSpecs(model, outputRoot)}


def splitTargetValues(values: list[str]) -> tuple[str, ...]:
    targets: list[str] = []
    seen: set[str] = set()
    for value in values:
        for item in value.split(","):
            target = item.strip()
            if not target or target in seen:
                continue
            seen.add(target)
            targets.append(target)
    return tuple(targets)


def normalizeTargetPath(value: str) -> str:
    return value.strip().replace("\\", "/")


def outputPathCandidates(path: Path, outputRoot: Path) -> set[str]:
    candidates = {path.as_posix(), path.name, path.stem}
    try:
        candidates.add(path.relative_to(outputRoot).as_posix())
    except ValueError:
        pass

    resolvedPath = path.resolve()
    resolvedOutput = outputRoot.resolve()
    candidates.add(resolvedPath.as_posix())
    try:
        candidates.add(resolvedPath.relative_to(resolvedOutput).as_posix())
    except ValueError:
        pass
    try:
        candidates.add(resolvedPath.relative_to(Path.cwd().resolve()).as_posix())
    except ValueError:
        pass
    return candidates


def outputFileMatchesTarget(spec: OutputFileSpec, outputRoot: Path, target: str) -> bool:
    normalized = normalizeTargetPath(target)
    candidates = outputPathCandidates(spec.path, outputRoot)
    if normalized in candidates:
        return True
    if "/" in normalized or normalized.endswith(".py"):
        return any(candidate.endswith(f"/{normalized}") for candidate in candidates)
    return normalized in {spec.path.stem, spec.moduleName}


def outputClassMatchesTarget(spec: OutputFileSpec, target: str) -> bool:
    if spec.className is None:
        return False

    normalized = target.strip()
    shortName = normalized.rsplit(".", 1)[-1]
    safeShortName = toSafeIdentifier(shortName, fallback="GeneratedClass")
    candidates = {
        spec.className,
        spec.originalClassName or "",
        spec.moduleName or "",
        f"{spec.packageName}.{spec.className}",
        f"{spec.packageName}.{spec.originalClassName}" if spec.originalClassName else "",
    }
    return normalized in candidates or shortName in candidates or safeShortName == spec.className


def formatAvailableTargets(specs: tuple[OutputFileSpec, ...], outputRoot: Path) -> str:
    files = sorted(spec.path.relative_to(outputRoot).as_posix() for spec in specs)
    classes = sorted(
        f"{spec.packageName}.{spec.className}"
        for spec in specs
        if spec.className is not None
    )
    fileText = "\n  ".join(files)
    classText = "\n  ".join(classes)
    return f"Available files:\n  {fileText}\nAvailable classes:\n  {classText}"


def filterOutputFileSpecs(
    specs: tuple[OutputFileSpec, ...],
    outputRoot: Path,
    targetFiles: tuple[str, ...],
    targetClasses: tuple[str, ...],
) -> tuple[OutputFileSpec, ...]:
    if not targetFiles and not targetClasses:
        return specs

    selected: list[OutputFileSpec] = []
    matchedFiles: set[str] = set()
    matchedClasses: set[str] = set()
    for spec in specs:
        include = False
        for targetFile in targetFiles:
            if outputFileMatchesTarget(spec, outputRoot, targetFile):
                include = True
                matchedFiles.add(targetFile)
        for targetClass in targetClasses:
            if outputClassMatchesTarget(spec, targetClass):
                include = True
                matchedClasses.add(targetClass)
        if include:
            selected.append(spec)

    missingFiles = [target for target in targetFiles if target not in matchedFiles]
    missingClasses = [target for target in targetClasses if target not in matchedClasses]
    if missingFiles or missingClasses:
        messages: list[str] = []
        if missingFiles:
            messages.append(f"unknown target file(s): {', '.join(missingFiles)}")
        if missingClasses:
            messages.append(f"unknown target class(es): {', '.join(missingClasses)}")
        messages.append(formatAvailableTargets(specs, outputRoot))
        raise ValueError("\n".join(messages))

    return tuple(selected)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("xml", type=Path, help="astah XMI/XML export file")
    parser.add_argument("output", type=Path, help="output directory root")
    parser.add_argument("--write", action="store_true", help="actually create/update files")
    parser.add_argument("--show-diff", action="store_true", help="print unified diffs")
    parser.add_argument(
        "--target-file",
        action="append",
        default=[],
        help="only process matching generated Python file; repeat or use commas for multiple targets",
    )
    parser.add_argument(
        "--target-class",
        action="append",
        default=[],
        help="only process the generated module for matching class; repeat or use commas for multiple targets",
    )
    args = parser.parse_args()

    xmlInputs = discoverInputXmls(args.xml)
    model = mergeModels([parseXmi(path) for path in xmlInputs])
    targetFiles = splitTargetValues(args.targetFile)
    targetClasses = splitTargetValues(args.targetClass)
    outputSpecs = buildOutputFileSpecs(model, args.output)
    try:
        outputSpecs = filterOutputFileSpecs(outputSpecs, args.output, targetFiles, targetClasses)
    except ValueError as exc:
        parser.error(str(exc))
    files = {spec.path: spec.text for spec in outputSpecs}

    changedCount = 0
    notes: list[str] = []
    changeLogs: list[str] = []

    for path in sorted(files):
        newText = files[path]
        oldText = path.read_text(encoding="utf-8") if path.exists() else ""
        blockedFixedLabels: list[str] = []
        if oldText:
            newText, blockedFixedLabels = mergeGeneratedCodeAreas(newText, oldText)
            newText = mergeSafeAreas(newText, oldText)
            newText = preserveReferencedModuleImports(newText, oldText)
        if blockedFixedLabels:
            labels = ", ".join(blockedFixedLabels)
            notes.append(f"[NOTE] {path}: FIXED CODE AREA prevented updates: {labels}")
        if isWhitespaceOnlyChange(oldText, newText):
            continue
        if isSingleBlankLineAddition(oldText, newText):
            continue
        if oldText == newText:
            continue
        changedCount += 1
        action = "update" if path.exists() else "create"
        if action == "update":
            changedLabels = extractChangedGeneratedAreaLabels(oldText, newText)
            summary = summarizeChangedLabels(changedLabels)
            nonGenerated = summarizeNonGeneratedChanges(oldText, newText)
            methodText = ", ".join(summary["methods"]) if summary["methods"] else "(none)"
            sectionText = ", ".join(summary["sections"]) if summary["sections"] else "(none)"
            changeLogs.append(
                f"[UPDATE] {path} | methods: {methodText} | sections: {sectionText} "
                f"| safe_areas: {nonGenerated['safe_areas']} "
                f"| outside_generated: {nonGenerated['outside_generated']} "
                f"| whitespace: {nonGenerated['whitespace']}"
            )
        else:
            changeLogs.append(f"[CREATE] {path}")
        if args.show_diff:
            print(
                "".join(
                    difflib.unified_diff(
                        oldText.splitlines(keepends=True),
                        newText.splitlines(keepends=True),
                        fromfile=str(path),
                        tofile=str(path),
                    )
                )
            )
        if args.write:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(newText, encoding="utf-8")

    if notes:
        print("=== Notes ===")
        for line in notes:
            print(line)
        print("")

    if changeLogs:
        print("=== Planned Changes ===" if not args.write else "=== Applied Changes ===")
        for line in changeLogs:
            print(line)
        print("")

    mode = "write mode" if args.write else "dry-run"
    print(f"=== Summary ===")
    print(f"Mode: {mode}")
    print(f"Changed files: {changedCount}")
    if targetFiles or targetClasses:
        targetSummary: list[str] = []
        if targetFiles:
            targetSummary.append(f"files: {', '.join(targetFiles)}")
        if targetClasses:
            targetSummary.append(f"classes: {', '.join(targetClasses)}")
        print(f"Targets: {'; '.join(targetSummary)}")
    if not args.write:
        print("Next: run again with --write to apply these changes.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
