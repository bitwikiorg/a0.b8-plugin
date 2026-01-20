# 🧙 BITCORE Setup Wizard

## Environment Initialization
1. **Resource Check**: Ensure the `resources/` directory contains `bot_registry.json` and `cores_registry.json`.
2. **API Configuration**: Set `BITHUB_URL` and `BITHUB_USER_API_KEY` in your environment.
3. **Synaptic Integrity Check**: Run the test suite to verify connectivity and path resolution.

## Production Hardening
The plugin includes built-in guards that will prevent initialization if critical environment variables are missing or if the `resources/` directory is inaccessible.
