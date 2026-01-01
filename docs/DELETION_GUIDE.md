# 🛡️ BITCORE Deletion & Hygiene Guide

## The BITHUB_JANITOR (Immune System)
The `BITHUB_JANITOR` component is responsible for maintaining swarm hygiene through 'apoptosis' (controlled deletion) of stale topics and necrotic test artifacts.

## Safe Deletion Protocols
1. **Guard**: Verify the category ID and topic age before deletion.
2. **Do**: Execute the `deleteTopic` or `nukeCategory` command via the Bithub Service.
3. **Verify**: Confirm the deletion via the Bithub API and log the event.

## Resource Cleanup
Temporary artifacts generated during execution are stored in the `resources/` directory and should be periodically cleared by the Janitor to prevent synaptic clutter.
