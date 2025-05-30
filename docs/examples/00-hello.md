# 00 - Hello GraphQL Codegen

**Hello-World: From Schema to Python Magic** ✨

In this first step we'll see how you can export enums and basic types from your graphql file to a `Pydantic` importable file.

---

## 🎯 What We're Building

By the end of this tutorial, you'll see how a humble GraphQL schema transforms into:

- 🔒 **Type-safe Pydantic models** (no more guessing what fields exist!)
- 🎨 **Beautiful enums** (goodbye magic strings, hello autocomplete!)  
- ⚡ **Instant validation** (catch bugs before they catch you!)

---

## 🚀 The Complete Example

Let's dive into a smoothie shop schema that showcases the foundational GraphQL-to-Python magic:

### Schema Input 📝

Copy this code into `hello.graphql`:

```graphql
--8<-- "test/inputs/smoothies/schema.graphql:12:35"
```

**What's cooking here?**
- **Scalars**: The building blocks (`String`, `Float`, plus a custom `CaloriesPerGram`)
- **Enums**: Type-safe choices (`Size` with `SMALL`, `MEDIUM`, `LARGE`)
- **Basic Types**: Real objects with multiple fields (`NutritionalInfo` - because nutrition matters!)

*🎭 Plot twist: Those `@compute` and `@expand` directives at the top? They're the secret sauce for advanced features we'll explore in future episodes. For now, just know they're there, looking mysterious and powerful.*

### Config File ⚙️

Tell the generator how to work its magic with `codegen.yaml`:

```yaml
--8<-- "test/inputs/smoothies/codegen.yaml:1:12"
```

**Breaking it down:**
- **schema**: Points to our GraphQL masterpiece
- **output_dir**: Where the Python magic lands (we're using stdout here, but you can also just specify a python pacakge)
- **scalars**: Custom type mappings (because `CaloriesPerGram` should obviously be a `float`)

### Run the Generator 🏃‍♂️

Ready for the magic show?

```bash
graphql-codegen . --stdout --flat
```

*Watch as GraphQL types transform into Python poetry...*

### Generated Output 🎉


```python
--8<-- "docs/outputs/hello.py"
```

**Let's decode this :**

🔹 **Import Section**: All the Python machinery needed for type safety and validation  
🔹 **Helper Functions**: Registration decorators for those mysterious directives (stay tuned!)  
🔹 **Enums**: `Size` becomes a proper Python enum with IDE-friendly autocomplete  
🔹 **Basic Types**: `NutritionalInfo` becomes a full Pydantic model with typed fields
🔹 **Model Rebuilding**: The final step that ensures everything works together seamlessly

---

## 💡 What You Just Unlocked

🎯 **Type Safety**: Your IDE now knows every field, every type, every relationship  
🛡️ **Runtime Validation**: Pydantic catches invalid data before it causes chaos  
🚀 **Developer Experience**: Autocomplete, type hints, and error highlighting everywhere  
📦 **JSON Ready**: Serialize/deserialize to/from JSON without breaking a sweat  
🔍 **Static Analysis**: mypy and pylint become your new best friends

---

## 🎪 The Magic Behind the Curtain

Notice those helper functions and registration decorators? They're preparing the stage for advanced features like:

- **Computed fields** that calculate values on the fly
- **Schema expansion** that transforms simple inputs into complex structures
- **Custom validation** that goes beyond basic type checking

We'll explore these superpowers in upcoming tutorials, but for now, just appreciate that the foundation is already there, waiting to surprise you!

---

[← Home](../index.md) | [Next: Interfaces & Unions →](01-interfaces-and-unions.md) 