# Contributing to BITCORE Swarm Plugins

## Development Standards
All contributions must adhere to the following standards to ensure swarm coherence and production reliability:

### 1. Neural Processing Standard (Guard → Do → Verify)
Every function and action must follow this flow:
- **Guard**: Validate all inputs, environment variables, and state before execution.
- **Do**: Perform the core synaptic task cleanly.
- **Verify**: Assert outputs and maintain state integrity. No silent failures allowed.

### 2. Why/What/How Docblocks
Every source file must begin with a docblock explaining the architectural purpose (Why), the functional scope (What), and the implementation logic (How).

### 3. Synaptic Storage (Resources)
All static data (registries, topologies) must be stored in the `resources/` directory. Use dynamic path resolution relative to the plugin root. Absolute paths are strictly forbidden.

### 4. Dual-Layer Testing
- **Scoped Unit Tests**: Required for every new action or service method.
- **Integration Suites**: Required for changes affecting multi-turn synaptic flow.
