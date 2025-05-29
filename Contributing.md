## Repository Structure and Contribution Guidelines

**Core Stack:**

- **Dependency Management:** `pyproject.toml` + `poetry` for installation
- **Testing:** `test/` folder is used to test the codegen on a few examples. (`/test/output` contains outputs packages created. `outputs/` is under version control, but not `output/<package>/gen`) as it is the generated code. However we have validation tests in `output/<package>/tests...` to try importing generated classes, and write basic export scripts
- **Command-Line Interface:** `cli.py` contains the cli

### Project Folder Structure

```
graphql_codegen/
├── __init__.py                # Package initialization
├── cli.py                     # Entry point CLI
├── config.py                  # YAML config parser
├── parser.py                  # GraphQL SDL parsing with directive support
├── generator.py               # Main codegen orchestrator
├── model_gen.py               # Pydantic model generation
├── runtime_gen.py             # Runtime system generation
├── templates/                 # Jinja2 templates for code generation
│   ├── __init__.py
│   ├── models.py.j2           # Pydantic models template
│   ├── auto.py.j2             # Generated runtime helpers template
│   ├── custom.py.j2           # User runtime template
│   └── package_init.py.j2     # Package __init__.py template
└── utils.py                   # Helper utilities

test/
├── inputs/                    # Test schemas
│   ├── smoothies/
│   │   ├── schema.graphql     # GraphQL schema with @compute/@expand
│   │   └── codegen.yaml       # Generation configuration
│   ├── userpost/              # Additional test case
│   └── minifound/             # Additional test case
├── outputs/                   # Generated packages (auto-created)
│   └── smoothies/             # Generated package structure:
│       ├── __init__.py        #   ├── __init__.py (re-exports)
│       ├── gen/               #   ├── gen/
│       │   ├── models.py      #   │   ├── models.py (Pydantic classes)
│       │   └── auto.py        #   │   └── auto.py (runtime helpers)
│       └── runtime/           #   └── runtime/
│           └── custom.py      #       └── custom.py (user code)
└── test_integration.py        # Integration tests
```

### Implementation Phases

**Phase 1: Core Infrastructure**

- CLI that accepts schema directory path
- Configuration parsing from `codegen.yaml`
- GraphQL schema parsing with directive extraction
- Basic code generation pipeline

**Phase 2: Code Generation Engine**

- Pydantic model generation with directive metadata
- Runtime system generation (`auto.py`, `custom.py`)
- Template-based file generation

**Phase 3: Testing & Validation**

- Complete smoothies test case
- Integration tests for generated packages
- Validation of @compute and @expand functionality

### Contribution Rules

- **Conciseness:** keep files short, functions as short as possible
- **Pydantic:** use pydantic extensively
- **DRY Principle:** be extremely dry (this is the point of this tool so it should be reflected in its codebase. )
- **No Unnecessary Code:** no fluff, no code that is not reflected in dedicated tests.
- **Focused Tests:** test should also not be overly verbose and present key specific features. They are to be used both as examples and testing.
