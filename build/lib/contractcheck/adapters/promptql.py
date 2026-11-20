"""PromptQL / Hasura DDN adapter: parses DDN metadata YAML files into
the normalized model.

Reads ObjectType, Model, Command, Relationship, and permission objects
(ModelPermissions, CommandPermissions, TypePermissions) from a metadata
directory, plus reviewed shared-context entries (business definitions,
assumptions, and coverage statements) where present as metadata
documents or in a context file.

Mapping discipline: what the metadata declares is mapped onto the
normalized model; where DDN metadata has no equivalent for a contract
element, the field is left unset so the engine codes it not documented
with the reason. Nothing is inferred from names alone.
"""

from __future__ import annotations

from pathlib import Path

import yaml

from ..model import Artifact, ContextEntry, Project

CONTEXT_KINDS = {
    "GlossaryTerm": "definition",
    "BusinessDefinition": "definition",
    "SharedContext": "definition",
    "ContextEntry": "definition",
    "Assumption": "assumption",
    "CoverageStatement": "coverage",
}

PERMISSION_KINDS = {"ModelPermissions", "CommandPermissions", "TypePermissions"}


def _iter_docs(root: Path):
    for ext in ("*.yaml", "*.yml", "*.hml"):
        for f in sorted(root.rglob(ext)):
            try:
                docs = list(yaml.safe_load_all(f.read_text(encoding="utf-8")))
            except yaml.YAMLError:
                continue
            for doc in docs:
                if isinstance(doc, dict):
                    yield f, doc


def _definition(doc: dict) -> dict:
    d = doc.get("definition")
    return d if isinstance(d, dict) else doc


def _doc_name(doc: dict) -> str | None:
    return doc.get("name") or _definition(doc).get("name")


def load_project(path: str | Path) -> Project:
    root = Path(path)
    if not root.is_dir():
        raise FileNotFoundError(f"PromptQL adapter expects a metadata directory: {root}")
    proj_name = root.name or "promptql project"
    if proj_name == "metadata" and root.parent.name:
        proj_name = root.parent.name
    project = Project(platform="promptql", name=proj_name)

    object_fields: dict[str, list[str]] = {}   # object type -> field names
    relationships: dict[str, list[str]] = {}   # source type -> relationship names
    permission_roles: dict[str, list[str]] = {}  # target name -> roles
    pending_models: list[tuple[Artifact, str | None]] = []  # (artifact, objectType)

    for f, doc in _iter_docs(root):
        kind = doc.get("kind")
        d = _definition(doc)
        name = _doc_name(doc)
        rel = str(f.relative_to(root)) if f.is_relative_to(root) else str(f)

        if kind == "ObjectType" and name:
            fields = d.get("fields") or []
            object_fields[name] = [fld.get("name") for fld in fields
                                   if isinstance(fld, dict) and fld.get("name")]
            project.underlying_models.append(Artifact(
                name=name, kind="model", source=f"{rel}#{name}",
                description=d.get("description") or None,
            ))
        elif kind == "Model" and name:
            agg = d.get("aggregate")
            aggregation = None
            if isinstance(agg, dict) and agg:
                fns = agg.get("aggregateFunctionDefinitions") or agg.get("functions") or []
                aggregation = ("aggregate expressions declared"
                               + (f" ({len(fns)} function definitions)" if fns else ""))
            art = Artifact(
                name=name, kind="model", source=f"{rel}#{name}",
                description=d.get("description") or None,
                aggregation=aggregation,
                deprecation="deprecated" if d.get("deprecated") else None,
            )
            pending_models.append((art, d.get("objectType")))
            project.artifacts.append(art)
        elif kind == "Command" and name:
            project.artifacts.append(Artifact(
                name=name, kind="command", source=f"{rel}#{name}",
                description=d.get("description") or None,
                deprecation="deprecated" if d.get("deprecated") else None,
            ))
        elif kind == "Relationship":
            src_type = d.get("sourceType") or d.get("source")
            if src_type and name:
                relationships.setdefault(src_type, []).append(name)
        elif kind in PERMISSION_KINDS:
            target = d.get("modelName") or d.get("commandName") or d.get("typeName")
            roles = [p.get("role") for p in (d.get("permissions") or [])
                     if isinstance(p, dict) and p.get("role")]
            if target and roles:
                permission_roles.setdefault(target, []).extend(roles)
        elif kind in CONTEXT_KINDS:
            entry_kind = CONTEXT_KINDS[kind]
            term = name or d.get("term") or "context"
            project.context_entries.append(ContextEntry(
                term=term,
                definition=d.get("definition") or d.get("text") or "",
                source=f"{rel}#{term}",
                reviewed=bool(d.get("reviewed") or d.get("status") in ("reviewed", "approved")),
                kind=d.get("kind") if d.get("kind") in ("assumption", "coverage") else entry_kind,
            ))
        # A context file may carry a top-level "context:" list instead.
        ctx_list = doc.get("context")
        if isinstance(ctx_list, list):
            for entry in ctx_list:
                if not isinstance(entry, dict):
                    continue
                project.context_entries.append(ContextEntry(
                    term=entry.get("term") or entry.get("name") or "context",
                    definition=entry.get("definition") or entry.get("text") or "",
                    source=rel,
                    reviewed=bool(entry.get("reviewed")
                                  or entry.get("status") in ("reviewed", "approved")),
                    kind=entry.get("kind") if entry.get("kind") in
                    ("definition", "assumption", "coverage") else "definition",
                ))

    # Second pass: relationships and object fields are the declared
    # slicing paths for a model; permissions attach as access evidence.
    for art, object_type in pending_models:
        dims: list[str] = []
        if object_type:
            dims.extend(object_fields.get(object_type, []))
            dims.extend(relationships.get(object_type, []))
        art.dimensions = dims
    for art in project.artifacts:
        roles = permission_roles.get(art.name)
        if roles:
            art.access = f"role-based permissions declared (roles: {', '.join(sorted(set(roles)))})"

    # Reviewed context entries act as provenance notes for artifacts they name.
    for entry in project.context_entries:
        for art in project.artifacts:
            if entry.term.lower() in art.name.lower() or art.name.lower() in entry.term.lower():
                art.provenance_note = entry.definition
    return project
