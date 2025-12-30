
# SETUP WIZARD: Activating Your a0.b8 Node

This document provides a comprehensive, step-by-step guide to initializing your `a0.b8-plugin` environment. Follow these phases in order to establish a secure connection with the Bitcore Hive.

## PHASE 0: PRE-FLIGHT CHECKS
**Objective**: Ensure your local environment is ready for ignition.

1.  **Verify Python Version**
    *   Ensure you are running Python 3.8 or higher.
    *   Command: `python --version`

2.  **Install Dependencies**
    *   The authentication scripts require specific cryptographic libraries before they can run.
    *   Command: `pip install -r requirements.txt`

3.  **Prepare Configuration**
    *   Copy the example environment file.
    *   Command: `cp .env.example .env`

---

## PHASE 1: THE HANDSHAKE (Authentication)
**Objective**: Generate cryptographic keys and authorize your node with the central server.

1.  **Run the Setup Script**
    *   Command: `python scripts/setup_mcp.py`
    *   *Note*: This script generates a secure RSA keypair locally.

2.  **Authorize via Browser**
    *   The script will provide a URL. Open it in your web browser.
    *   Log in and approve the application.
    *   Copy the **Encrypted Payload** provided by the website.

3.  **Complete the Handshake**
    *   Paste the payload back into the terminal prompt.
    *   The script will decrypt the payload and save your credentials to `agent-profile.json`.

---

## PHASE 2: THE BRIDGE (Configuration)
**Objective**: Link your generated credentials to the runtime environment.

**CRITICAL STEP**: The runtime system reads from `.env`, but the setup script saves to `agent-profile.json`. You must bridge this gap manually.

1.  **Open `agent-profile.json`**
    *   Locate the `key` value (your API Key).
    *   Locate the `url` value (the API Endpoint).

2.  **Update `.env`**
    *   Open your `.env` file.
    *   Paste the values into the corresponding variables:
        ```bash
        BITHUB_URL=https://hub.bitwiki.org/  # (Or the URL from the profile)
        BITHUB_USER_API_KEY=your_pasted_key_here
        ```
    *   Save the file.

---

## PHASE 3: THE SYNAPSE (Registry Sync)
**Objective**: Download the neural map of available agents.

1.  **Sync Registry**
    *   Command: `python -m bithub.bithub_registry refresh`
    *   *Success*: You should see a confirmation that the registry has been updated.

2.  **Verify**
    *   Check that `bot_registry.json` exists and is not empty.

---

## PHASE 4: THE PING (Connectivity Test)
**Objective**: Verify network pathways and authentication before starting the GUI.

1.  **Run Connectivity Test**
    *   Command: `pytest tests/test_chat_connectivity.py`
    *   *Success*: All tests should pass (Green).

---

## PHASE 5: ACTIVATION (GUI & Chat)
**Objective**: Real-world usage and first contact.

1.  **Start the Agent Zero GUI**
    *   Launch your standard Agent Zero interface.

2.  **Select an Agent**
    *   Navigate to the Chat interface.
    *   In the "Agent" dropdown (or equivalent), select a remote agent from the list (populated from Phase 3).

3.  **First Contact**
    *   Send a message: "Hello, are you online?"
    *   *Verification*: The agent should reply. This confirms that:
        *   Your API Key is valid.
        *   Encryption is working.
        *   Routing is correct.
