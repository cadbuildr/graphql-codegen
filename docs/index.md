# GraphQL Codegen Documentation

**Progressive Examples: From Basic Types to Advanced Directives**

This documentation walks through GraphQL Codegen features with progressive examples using a smoothie recipe schema. Each example builds on the previous one, demonstrating core concepts step by step.

> **Mission statement:** keep a _single_ GraphQL SDL as the source‑of‑truth for a data‑flow/DAG.
> Generate clean, typed Python (and later other languages) while letting authors describe higher‑level "macro" nodes that are **either executed directly by a compiler** or **auto‑expanded** into primitives when that compiler does not recognise them.

---

## 1. Why another GraphQL flavour?

- **GraphQL SDL is readable & tooling‑friendly** – editors, formatters, schema diffing, etc.
- A CAD / ETL / game‑logic _DAG_ is just a typed AST. SDL already gives us:

  - _object types_ → nodes
  - _fields_ → edges / attributes
  - _unions & enums_ → polymorphism & constants

- What SDL does **not** offer is the _procedural layer_: _how_ a node derives data or unrolls into primitives for a downstream compiler. We bridge that gap with directives ( see `@compute` and `@expand`)

---

## 🚀 Quick Start

### Installation

#### Option 1: Native Installation (Recommended)
Install directly with pip for system-wide access:

```bash
# Install in development mode (links to source)
pip install -e .

# Or build and install the package
poetry build
pip install dist/graphql_codegen-*.whl
```

After installation, the CLI is available globally:
```bash
graphql-codegen --help
```

#### Option 2: Poetry Environment
If you prefer to keep it in the Poetry environment:

```bash
# Install dependencies
poetry install

# Use via poetry run
poetry run graphql-codegen --help

# Or activate the poetry shell
poetry shell
graphql-codegen --help
```

---

## 📚 Learning Path

| Example | Description |
|---------|-------------|
| [Hello](examples/00-hello.md) | Foundation: From basic scalars to complete objects |
| [Interfaces](examples/01-interfaces-and-unions.md) | Shared behavior with inheritance and type unions|
| [Compute Directive](examples/02-compute-directive.md) | Calculated fields with `@compute` |
| [Expand Directive](examples/03-expand-directive.md) | JSON template expansion with `@expand` |

---

## The Smoothie Schema Example 

Throughout the documentation we'll explore a smoothie recipe example, incrementally increasing complexity to introduce different features of the language step by step.