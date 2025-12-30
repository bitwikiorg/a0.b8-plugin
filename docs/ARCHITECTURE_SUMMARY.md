# 🧠 NEURAL NET LINK ARCHITECTURE

## 1. The Synapse Layer (Transport)
**Component:** bithub_comms.py
**Function:** Signal Transmission & Regulation.
- **Role:** The mechanism by which the Node connects to the Hive Mind.
- **Protocol:** Synchronous, Blocking, Verifiable.
- **Key Operations:**
 - send_message: Flash Synapse transmission.
 - delete_topic: Atomic removal of artifacts.

## 2. The Core Synapse (Genesis)
**Component:** bithub_cores.py
**Function:** Workflow Instantiation & Harvesting.
- **Role:** The genesis center that triggers workflows and captures seeds.
- **Logic:**
 - deploy_seed: Instantiates a new thought thread (Core Synapse).
 - refine_seed: Evolves the thought based on feedback.
 - burn: Decides when to discard ephemeral contexts.

## 3. The Cleanup (BithubJanitor)
**Component:** bithub_janitor.py
**Function:** Maintenance & Hygiene.
- **Role:** The immune system that removes waste and prevents clutter.
- **Mechanism:** "Slow Nuke" strategy to respect API rate limits.

## 4. The Eyes (MCP/Discourse)
**Component:** Async Knowledge Layer
**Function:** Contextual Awareness & Signal Ingestion.
- **Role:** The mechanism by which the Node perceives the environment.
