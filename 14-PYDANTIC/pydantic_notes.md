# Pydantic — Complete Notes (from 1_basic.py → 7_serialization.py)

---

## 1. What is Pydantic?

Pydantic is a **data validation and settings management library** for Python. It uses Python **type hints** to:

- Validate incoming data (check types, ranges, formats)
- **Coerce** data into the correct type when possible (e.g. `"30"` → `30`)
- Give clear, structured error messages when data is invalid
- Serialize (convert) Python objects to dict/JSON easily
- Auto-generate JSON Schemas (used heavily by FastAPI for docs)

**Core idea:** instead of manually writing `if not isinstance(...)` checks everywhere, you *declare* the shape of your data once as a class, and Pydantic enforces it every time an object is created.

---

## 2. Why use Pydantic? (`2_pydantic_why.py`)

### The problem with plain classes / dicts
A normal Python class or dict does **not** validate anything:
```python
class patient(BaseModel):
    name: str
    age: int
```
Without Pydantic, nothing stops someone from passing `age="thirty"` or forgetting a required field until your code crashes deep inside a function — bad for APIs, data pipelines, or any place external/user data enters your system.

### What Pydantic gives you (seen in `2_pydantic_why.py`)
```python
class Patient(BaseModel):
    name: Annotated[str, Field(max_length=50, title='...', description='...', examples=['Nitish'])]
    email: EmailStr
    linkedin_url: AnyUrl
    age: int = Field(gt=0, lt=120)
    weight: Annotated[float, Field(gt=0, strict=True)]
    married: Annotated[bool, Field(default=None, description='...')]
    allergies: Annotated[Optional[List[str]], Field(default=None, max_length=5)]
    contact_details: Dict[str, str]
```

Key building blocks:

| Feature | Purpose |
|---|---|
| `EmailStr` | Validates proper email format (needs `email-validator` package installed) |
| `AnyUrl` | Validates that a string is a proper URL |
| `Field(gt=0, lt=120)` | Numeric constraints — greater than / less than |
| `Field(max_length=50)` | String/list length constraints |
| `Field(strict=True)` | Disables type coercion for that field (won't convert `"75.2"` → `75.2`) |
| `Field(default=None, description=...)` | Default values + metadata (used for docs/schema) |
| `Annotated[type, Field(...)]` | Modern way to attach `Field` constraints to a type hint |
| `Optional[List[str]]` | Field can be `None` or a list of strings |
| `Dict[str, str]` | A dictionary with string keys and string values |

**Type coercion example:** `'age': '30'` (a string in the input dict) becomes `patient1.age == 30` (an `int`) automatically — Pydantic tries to convert compatible types unless `strict=True` is set.

**Why this matters (general use cases):**
- **API request/response validation** (this is *the* reason FastAPI is built on Pydantic)
- **Config/settings management** (`pydantic-settings`, reading `.env` files with validation)
- **Data pipelines / ETL** — validate rows before processing
- **Data classes with guarantees** — anywhere you want "if this object exists, its data is guaranteed valid"

---

## 3. Basic Model (`1_basic.py`)

```python
from pydantic import BaseModel

class patient(BaseModel):
    name: str
    age: int
```

- Every Pydantic model inherits from `BaseModel`.
- Fields are declared like class attributes with **type annotations** — no `= value` needed unless you want a default.
- Creating an instance: `patient1 = patient(**patient_info)` — this is where validation happens (at **instantiation time**).
- Convention note: class names are usually **PascalCase** (`Patient`), not lowercase — file 1 uses lowercase `patient` as a simple example, later files fix this to `Patient`.
- You then pass the *validated object* around your functions (`insert_patient_data(patient1)`), instead of passing a raw/unchecked dict. This is a key pattern: **validate once at the boundary, trust the object everywhere after.**

---

## 4. `field_validator` — Custom Field-Level Validation (`3_filed_validator.py`)

Use `@field_validator` when you need **custom logic on a single field** beyond what `Field(...)` constraints can express (e.g., checking against a list of allowed values, transforming data).

```python
from pydantic import field_validator

class Patient(BaseModel):
    name: str
    email: EmailStr
    age: int
    ...

    @field_validator('email')
    @classmethod
    def email_validator(cls, value):
        valid_domains = ['hdfc.com', 'icici.com']
        domain_name = value.split('@')[-1]
        if domain_name not in valid_domains:
            raise ValueError('Not a valid domain')
        return value

    @field_validator('name')
    @classmethod
    def transform_name(cls, value):
        return value.upper()   # validators can also TRANSFORM data

    @field_validator('age', mode='after')
    @classmethod
    def validate_age(cls, value):
        if 0 < value < 100:
            return value
        raise ValueError('Age should be in between 0 and 100')
```

### Key points
- Decorated with `@field_validator('field_name')` then `@classmethod`.
- Must `return` the value (validated or transformed) — whatever you return becomes the field's final value.
- Raise `ValueError` (or `TypeError`/`AssertionError`) to reject the input — Pydantic wraps this into a structured `ValidationError`.
- **`mode` parameter:**
  - `mode='before'` (default in some contexts) — runs **before** Pydantic's own type coercion/validation. You get the raw input.
  - `mode='after'` — runs **after** Pydantic has already coerced the type. You get a value guaranteed to already be the correct type (e.g., `age` is already `int` here).
- A validator can also be used purely to **transform** data (like `transform_name` uppercasing the name) — validation and transformation are the same mechanism.
- Multiple validators can exist on different fields in the same model.

**Use case:** business-rule validation — allowed domains, allowed value ranges, formatting/normalizing strings, checking against enums or external constraints that a plain type hint can't express.

---

## 5. `model_validator` — Cross-Field Validation (`4_model_validator.py`)

`field_validator` only sees **one field at a time**. When a rule depends on **multiple fields together**, use `@model_validator`.

```python
from pydantic import model_validator

class Patient(BaseModel):
    name: str
    email: EmailStr
    age: int
    contact_details: Dict[str, str]
    ...

    @model_validator(mode='after')
    def validate_emergency_contact(cls, model):
        if model.age > 60 and 'emergency' not in model.contact_details:
            raise ValueError('Patients older than 60 must have an emergency contact')
        return model
```

### Key points
- `@model_validator(mode='after')` runs after **all** individual fields have already been validated/coerced. `model` here is the **entire model instance**, so you can access `model.age`, `model.contact_details`, etc. together.
- `mode='before'` also exists — runs on the **raw input dict** before any field validation, useful for restructuring input data before Pydantic even looks at individual fields.
- Must return the model (in `after` mode) or the (possibly modified) data (in `before` mode).
- **Use case:** rules that involve relationships between fields — e.g. "if age > 60, an emergency contact is required", "password and confirm_password must match", "start_date must be before end_date".

**`field_validator` vs `model_validator` — quick comparison:**

| | `field_validator` | `model_validator` |
|---|---|---|
| Scope | One field | Whole model (all fields) |
| Use case | Format/range checks, per-field transforms | Cross-field business rules |
| `mode` options | `'before'`, `'after'` | `'before'`, `'after'` |
| Access to other fields | No (directly) | Yes |

---

## 6. `computed_field` — Derived/Calculated Fields (`5_computed_fields.py`)

Sometimes you want a field that is **derived from other fields**, not supplied by the user, and you want it to appear automatically when the model is used/serialized (e.g. in an API response).

```python
from pydantic import computed_field

class Patient(BaseModel):
    weight: float  # kg
    height: float  # mtr
    ...

    @computed_field
    @property
    def bmi(self) -> float:
        bmi = round(self.weight / (self.height ** 2), 2)
        return bmi
```

### Key points
- Combine `@computed_field` with Python's normal `@property`.
- It is **not** something you pass in when creating the object (`weight` and `height` are inputs; `bmi` is computed from them).
- It recalculates automatically whenever accessed: `patient1.bmi`.
- It **shows up in `.model_dump()` / `.model_dump_json()`** output too, unlike a plain `@property`, which wouldn't be included in serialization by default.
- **Use case:** BMI from height/weight, `full_name` from `first_name` + `last_name`, `age` from `date_of_birth`, totals/derived stats in API responses — anywhere the client shouldn't send the value but should receive it.

---

## 7. Nested Models (`6_nested.py`)

You can use one Pydantic model **as the type of a field** in another model — this is how you represent structured/hierarchical data.

```python
class Address(BaseModel):
    city: str
    state: str
    pin: str

class Patient(BaseModel):
    name: str
    gender: str
    age: int
    address: Address        # <-- nested model
```

```python
address1 = Address(city='gurgaon', state='haryana', pin='122001')
patient1 = Patient(name='nitish', gender='male', age=35, address=address1)
```

### Why nest models instead of one flat model?
- **Better organization** of related data (e.g., grouping `vitals`, `address`, `insurance` separately).
- **Reusability** — `Address` can be reused inside `Patient`, `Hospital`, `MedicalRecord`, etc., instead of duplicating fields.
- **Readability** — mirrors real-world structure, easier for other developers/API consumers to understand.
- **Automatic validation** — nested models are validated automatically when the parent is validated; no extra manual work needed. If `Address` data is invalid, `Patient(...)` creation fails with a clear nested error path (e.g. `address.pin`).

### `model_dump(include=...)`
```python
temp = patient1.model_dump(include={'name', 'age', 'address'})
```
- `model_dump()` converts the model into a plain Python **dict**.
- `include={...}` lets you pick only specific top-level fields to include in the output (there's also `exclude={...}` to do the opposite).
- Result type is `dict` (confirmed by `print(type(temp))` → `<class 'dict'>`).

---

## 8. Serialization (`7_serialization.py`)

**Serialization** = converting a Pydantic model into a plain Python `dict` or JSON string, typically to send over an API, save to a file, etc.

```python
class Patient(BaseModel):
    name: str
    gender: str = 'Male'   # default value
    age: int
    address: Address

patient_dict = {'name': 'nitish', 'age': 35, 'address': address1}  # 'gender' NOT provided
patient1 = Patient(**patient_dict)

temp = patient1.model_dump(exclude_unset=True)
print(temp)   # {'name': 'nitish', 'age': 35, 'address': {...}}  -- 'gender' is excluded
```

### Key `model_dump()` options

| Option | Effect |
|---|---|
| `model_dump()` | Full dict of all fields |
| `model_dump(include={...})` | Only the listed fields |
| `model_dump(exclude={...})` | All fields except the listed ones |
| `model_dump(exclude_unset=True)` | Only fields that were **explicitly passed in** by the caller — fields that fell back to their default (like `gender` here) are **left out** |
| `model_dump(exclude_defaults=True)` | Excludes fields that currently equal their default value (even if explicitly passed) |
| `model_dump(exclude_none=True)` | Excludes fields whose value is `None` |
| `model_dump_json()` | Same as `model_dump()` but returns a **JSON string** instead of a dict |

**Why `exclude_unset` matters (real use case):** PATCH-style API updates. You only want to update the fields the client actually sent, not overwrite other fields with their defaults. `exclude_unset=True` lets you distinguish "user didn't send this field" from "user sent the default value."

---

## 9. Big Picture — Pydantic Validation Flow

```
Raw input (dict / JSON)
        │
        ▼
model_validator(mode='before')   ← optional: reshape raw data
        │
        ▼
Per-field: type coercion + Field(...) constraints
        │
        ▼
field_validator(mode='before'/'after') per field ← optional: custom checks/transforms
        │
        ▼
model_validator(mode='after')    ← optional: cross-field rules
        │
        ▼
computed_field properties become available
        │
        ▼
Valid Model Instance  ──►  model_dump() / model_dump_json()  ──►  dict / JSON
```

If validation fails at any step, Pydantic raises a `pydantic.ValidationError` containing **all** the errors found, with the exact field path, the bad value, and a readable message — extremely useful for API error responses.

---

## 10. Other Real-World Use Cases of Pydantic

- **FastAPI**: request bodies, query params, and response models are all Pydantic models — validation + auto-generated OpenAPI docs come for free.
- **Settings/config management**: `pydantic-settings` reads env vars / `.env` files into a validated `BaseSettings` model (e.g., `DATABASE_URL`, `SECRET_KEY` with types enforced).
- **LLM/tool-call structured outputs**: many LLM frameworks use Pydantic models to define the exact JSON schema a model must return, then parse/validate the response.
- **Data pipelines**: validating rows of incoming data (CSV, Kafka messages, webhooks) before they enter a database.
- **Config files for CLIs**: validating YAML/JSON config against a schema.
- **Form/input validation** in any backend service, independent of the web framework.

---

## 11. Cheat-Sheet Summary

| Concept | Decorator / Tool | Purpose |
|---|---|---|
| Basic model | `class X(BaseModel)` | Define shape + types of data |
| Constraints | `Field(gt=, lt=, max_length=, ...)` | Declarative validation rules |
| Special types | `EmailStr`, `AnyUrl` | Pre-built format validation |
| Per-field custom rule | `@field_validator('field')` | Custom validation / transformation on one field |
| Cross-field rule | `@model_validator(mode='after')` | Validation depending on multiple fields |
| Derived field | `@computed_field` + `@property` | Auto-calculated field included in output |
| Nested structure | `field: OtherModel` | Compose models; auto-validated |
| To dict | `.model_dump(...)` | Serialize to Python dict |
| To JSON | `.model_dump_json(...)` | Serialize to JSON string |
| Only-sent fields | `.model_dump(exclude_unset=True)` | Useful for PATCH/update endpoints |

**One-line takeaway:** Pydantic lets you declare *what your data should look like* using ordinary Python type hints, and it handles validation, coercion, custom rules, derived fields, nested structures, and serialization automatically — making it the backbone of reliable data handling in modern Python APIs (especially FastAPI).
