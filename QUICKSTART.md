# ⚡ a0.b8 Quickstart

## 1. Installation
```bash
cd a0.b8-plugin
pip install -e .
```

## 2. Environment
```bash
export BITHUB_URL="https://hub.bitwiki.org"
export BITHUB_USER_API_KEY="your_key_here"
```

## 3. Basic Usage

### Send a Message
```python
from bithub.bithub_comms import BithubComms
comms = BithubComms()
comms.send_private_message(recipients=['target_user'], title='Hello', raw='World')
```

### Deploy a Core Workflow
```python
from bithub.bithub_cores import BithubCores
cores = BithubCores()
result = cores.deploy_core(title='Task', content='Payload', category_id=54, sync=True)
print(f"Result: {result}")
```
