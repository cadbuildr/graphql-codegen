# GraphQL Codegen — **Documentation & Design Primer**

> **Mission statement:** keep a _single_ GraphQL SDL as the source‑of‑truth for a data‑flow/DAG.
> Generate clean, typed Python (and later other languages) while letting authors describe higher‑level "macro" nodes that are **either executed directly by a compiler** or **auto‑expanded** into primitives when that compiler does not recognise them.

---

## 1 Why another GraphQL flavour?

- **GraphQL SDL is readable & tooling‑friendly** – editors, formatters, schema diffing, etc.
- A CAD / ETL / game‑logic _DAG_ is just a typed AST. SDL already gives us:

  - _object types_ → nodes
  - _fields_ → edges / attributes
  - _unions & enums_ → polymorphism & constants

- What SDL does **not** offer is the _procedural layer_: _how_ a node derives data or unrolls into primitives for a downstream compiler. We bridge that gap with two directives.

---

## 2 Core directives

This section outlines the core directives used to add a procedural layer to the GraphQL SDL.

### 2.1 `@compute(fn: String!)`

- **Applies to:** Field
- **Behaviour:** This directive instructs the runtime to derive the value of a field rather than storing it verbatim. The field still participates in standard validation and typing.
- **Minimal example:**
  ```graphql
  calories: Float! @compute(fn: "calcCalories")
  ```

### 2.2 `@expand(into: JSON!)`

- **Applies to:** Field _or_ Object
- **Behaviour:** This directive describes how to unfold a node into its primitive components. This expansion occurs **if, and only if,** the active compiler does not recognize the node as part of its _primitive set_.
  - By default, the JSON payload provided to `into` is processed by a **generic expansion engine**, requiring no additional user code.
  - Optionally, you can supply a JSON object like `{ "fn": "myCustomFn" }` within the `into` argument to delegate the expansion logic to a custom Python function.
- **Minimal example:** _(Refer to the smoothie SDL example further below for a practical illustration of `@expand` on a field. The directive can also be applied to an object type.)_

> **Key idea:** The `@expand` directive is designed to be _data‑only_ by default. Compilers unfamiliar with a specific node can call its `expand()` method and receive fully materialized child nodes without needing custom user-written expansion logic.

### 2.3 Execution contract

- Generated models cache directive metadata (`FieldInfo.json_schema_extra`).
- **Compute** always needs a registered Python function.
- **Expand** falls back to the generic JSON engine. Custom code only runs when the JSON includes `fn`.

---

## 3 SDL rules (subset)

1. **Valid GraphQL SDL 2021** – anything `graphql-core` 3.x can parse.
2. `!` (non‑null) maps to required Pydantic fields.
3. Custom scalars become `typing.NewType` aliases unless overridden in YAML.
4. Interfaces & input objects: _road‑mapped_ – keep them out for now.
5. Comments (`# ...` or `""" ... """`) are ignored by the generator.

---

## 4 codegen.yaml — one file to rule them all

Placed **next to** `schema.graphql`. The CLI now needs _only_ that path.

```yaml
package: smoothies # import‑safe Python package name for user to edit and implement.
runtime_package: smoothies.runtime
codegen_version: "0.1" # locks generator/auto.py ABI

scalars: # optional overrides
  DateTime: str
```

<details><summary>Field reference</summary>

| Key               | Type         | Required | Default |
| ----------------- | ------------ | -------- | ------- |
| `package`         | str          | ✅       | –       |
| `runtime_package` | str          | ✅       | –       |
| `codegen_version` | str          | ✅       | –       |
| `scalars`         | dict str→str |          | `{}`    |
| `templates`       | str/path     |          | `null`  |

</details>

---

## 5 Generated layout

```
<output>/<package>/
├─ __init__.py            (re‑export models)
├─ gen/
│   ├─ models.py          (typed Pydantic graph)
│   └─ auto.py            (generated helpers – **never edited**)
└─ runtime/
    └─ custom.py          (starts empty – user registers fns here)
```

### 5.1 gen/auto.py (immutable)

```python
"""Auto‑generated helpers – DO NOT EDIT.
   Version is locked by codegen_version in YAML.
"""
from typing import Any, Callable, Dict

_COMPUTE: Dict[str, Callable[[Any, str, dict], Any]] = {}
_EXPAND_CUSTOM: Dict[str, Callable[[Any, dict], Any]] = {}

# --- compute helpers -------------------------------------------------------

def register_compute_fn(name: str):
    def _wrap(fn):
        _COMPUTE[name] = fn
        return fn
    return _wrap


def run_compute(inst, field, meta):
    return _COMPUTE[meta["fn"]](inst, field, meta)

# --- expand helpers --------------------------------------------------------

def register_expand_fn(name: str):
    def _wrap(fn):
        _EXPAND_CUSTOM[name] = fn
        return fn
    return _wrap

# Generic JSON‑based expansion engine

def _default_expand(instance, meta):
    # <checkout the source code of graphql‑codegen for the full implementation>
    ...


def run_expand(inst, meta):
    if "fn" in meta:
        return _EXPAND_CUSTOM[meta["fn"]](inst, meta)
    return _default_expand(inst, meta)
```

`runtime/custom.py` is generated **empty** – users import helpers from `gen.auto` and register extra functions there only when necessary.

### 5.2 `models.py` (excerpt)

```python
class Smoothie(BaseModel):
    name: String = Field(...)
    size: String = Field(...)
    parts: List[IngredientAmount] = Field(...)

class BananaStrawberrySmoothie(BaseModel, Expandable):
    size: String = Field(...)
    __expansion__ = {
        "size": "$size",        # ← placeholder resolved by default engine
        "recipe": [
            {"ingredient": "Banana",     "grams": 120},
            {"ingredient": "Strawberry", "grams":  80},
            {"ingredient": "Milk",       "grams": 200},
        ],
    }
    result: Smoothie = Field(...)
```

> The `$size` token is replaced with the instance’s `size` attribute by the default engine, so your macro node’s parameter is forwarded automatically.

---

## 6 Complete minimal SDL (smoothies)

```graphql
# -------------------------------------------------
# Global directives used by the code‑generator
# -------------------------------------------------

directive @compute(fn: String!) on FIELD_DEFINITION
# `into` accepts raw JSON (string)
directive @expand(into: String!) on FIELD_DEFINITION | OBJECT

scalar String
scalar Float

"""
Primitive parameter wrapper
"""
input FloatParameterInput {
  value: Float!
} # to illustrate param passing – not yet used by generator
type FloatParameter {
  value: Float!
}

type Ingredient {
  name: String!
  calories_per_gram: FloatParameter!
}

type IngredientAmount {
  ingredient: Ingredient!
  grams: FloatParameter!
  calories: FloatParameter! @compute(fn: "calcCalories")
}

"""
A convenience node.  If the active compiler understands
`BananaStrawberrySmoothie`, it can leave it as‑is; otherwise it calls
`.expand()` to unroll into primitives.
"""
type BananaStrawberrySmoothie {
  # Parameters ----------
  size: String!

  # Expansion spec ------
  result: Smoothie!
    @expand(
      into: """
      {
        "size": "$size",          # forwards the parameter
        "recipe": [
          { "ingredient": "Banana",     "grams": 120 },
          { "ingredient": "Strawberry", "grams":  80 },
          { "ingredient": "Milk",       "grams": 200 }
        ]
      }
      """
    )
}

type Smoothie {
  name: String!
  size: String!
  parts: [IngredientAmount!]!
}
```

## 7 Using the generated package

```python
# 1. Import the generated models ─ each schema lives under
#    <output-dir>/<pkg-name>/gen/
from smoothies.gen.models import (
    BananaStrawberrySmoothie,
    Ingredient, IngredientAmount
)

# 2. Build your DAG in plain Python
banana   = Ingredient(name="Banana",     calories_per_gram=0.89)
strawb   = Ingredient(name="Strawberry", calories_per_gram=0.32)
milk     = Ingredient(name="Milk",       calories_per_gram=0.64)

# macro-node with its own parameters
macro = BananaStrawberrySmoothie(
    name="Breakfast Booster",
    size="MEDIUM"
)

# 3. Ask a compiler if it supports that node …
if compiler.supports("BananaStrawberrySmoothie"):
    dag_node = macro            # keep high-level node
else:
    dag_node = macro.expand()   # generic engine expands JSON → Smoothie

# 4. All fields tagged with @compute have the helper:
for part in dag_node.parts:
    print(
        part.ingredient.name,
        part.compute("calories")   # calls runtime.auto._default_compute
    )
```

### Where the helpers live

| File                | Who touches it? | Purpose                                                                                       |
| ------------------- | --------------- | --------------------------------------------------------------------------------------------- |
| `gen/models.py`     | **generated**   | Pydantic classes, `Computable`, `Expandable` mix-ins                                          |
| `gen/auto.py`       | **generated**   | Immutable helpers (`_default_expand`, `_default_compute`, …) <br>_(see source for full impl)_ |
| `runtime/custom.py` | **you**         | Optional overrides<br>`@register_compute_fn`, `@register_expand_fn`                           |

> **Tip** – 99 % of projects never touch `runtime/custom.py`; the JSON you embed in
> `@expand(into: """ … """)` is enough for the default engine.

```

```
