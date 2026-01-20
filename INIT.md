# PROJECT: Bithub Client System (a0.b8)

## INIT_SEQUENCE
1. **ENV_SETUP**: python scripts/setup_env.py
2. **RESOURCE_CHECK**: Ensure `resources/` contains necessary JSON registries.
3. **VALIDATION**: Run `pytest` to verify synaptic integrity.

## MINIMUM_RUNTIME_CONTEXT_LOAD
- Python 3.8+
- Active venv
- BITHUB_USER_API_KEY in environment
