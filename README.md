# Propy Test

## design philosophy

* **LLM is fuzzy parser only**
* **validation is deterministic**
* **fail closed not guess**
* **minimal deps**
* **Decimal for money**
* **everything important is explicit**

## how to run

**Make venv & install deps:**
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**set key:**
```bash
export OPENAI_API_KEY=your_key_here
```

**run script:**
```bash
python -m src.main
```


**run tests:**
```bash
pytest -q
```

## Approach: Pure Paranoid Enterprise ready code 
LLM only gives JSON that it,
it returns structured json and we immediately validate it with pydantic (extra forbid, strict types).

after that everything important is deterministic python:

normalize + resolve county (no fuzzy guessing)

date_recorded must not be before date_signed

numeric amount must exactly match the words

we re-parse the words ourselves

money is Decimal, never float

if anything looks wrong we throw. we dont auto-fix. we dont guess. fail closed.