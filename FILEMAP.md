# Project File Map (Root: a0.b8-plugin)

a0.b8-plugin/
  resources/           # Synaptic Storage (Registries, Topologies)
    bot_registry.json
    cores_registry.json
    topology.json
  bithub/              # Core Logic (Neural Net Link)
    bithub_config.py   # Dynamic Configuration
    bithub_comms.py    # Transport Layer (Telepathy)
    bithub_cores.py    # Genesis Layer (Core Synapse)
    bithub_janitor.py  # Immune System (Cleanup)
    ...
  tests/               # Dual-Layer Testing
    test_comms.py
    test_cores.py
    ...
  docs/                # Documentation
    ARCHITECTURE_SUMMARY.md
    SWARM_ORCHESTRATION.md
  README.md
  AGENTS.md
  CHANGELOG.md
  TODO.md
  INIT.md
