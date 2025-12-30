# 📋 REVISED ROADMAP: DUAL-MODE EVOLUTION

## PHASE 1: STABILITY (Core Seed)
- [x] **Implement Core Seed Pattern** (bithub_cores.py)
  - [ ] Add deploy_seed(title, category) -> Returns ID.
  - [ ] Add refine_seed(post_id, content) -> Updates Post.
  - **Goal:** Prevent context loss. Secure the ID first, then inject the heavy payload.

## PHASE 2: USABILITY (Audience Flag)
- [x] **Implement Audience Flag** (bithub_comms.py)
  - [ ] Add target_audience param (enum: 'human', 'ai').
  - [x] **Logic:**
    - ai: Enforce strict JSON output (no markdown fluff).
    - human: Enforce Markdown formatting (headers, bolding).

## PHASE 3: FLEXIBILITY (Dual-Mode Sync/Async)
- [x] **Implement Dual-Mode Comms** (bithub_comms.py)
  - [ ] Add sync: bool = False to send_message and deploy_core.
  - [x] **Async (Default):** Fire & Forget. Returns {"post_id": 123}.
  - [x] **Sync (Ping Pong):** Fire & Wait. Returns {"content": "Reply text..."}.
- [x] **Dynamic Polling Strategy**
  - [ ] Add poll_interval arg to support long waits (>15m) without spamming the API.

## FUTURE: v1.0.2 (Genome Integration)
- [ ] **Genome Payloads**: Standardize sending full Holobiont Genomes via Bithub topics.
- [ ] **Profile Integration**: Load Genomes directly from a0.b8-profile/artifacts.
