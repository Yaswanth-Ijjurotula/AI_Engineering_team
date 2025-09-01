# AI Engineering Team

## Description
This project utilizes a **CrewAI framework** to automate the software development process. It simulates a team of AI agents, each with a specific role:

- **Engineering Lead** – Creates detailed design documentation.  
- **Backend Engineer** – Implements Python backend code.  
- **Frontend Engineer** – Builds a Gradio-based UI.  
- **Test Engineer** – Writes unit tests for validation.  

The system takes any set of high-level requirements and generates a complete, tested software module.

### Example Project
As a demonstration, the AI Engineering Team builds an **Account Management System** for a trading simulation platform.  

**Requirements:**
- Create accounts, deposit, and withdraw funds.  
- Record buying and selling of shares.  
- Calculate portfolio value and profit/loss.  
- Report holdings, profit/loss, and transaction history.  
- Prevent negative balances, overspending, or selling non-existent shares.  
- Use a mock function `get_share_price(symbol)` for share prices.  

The true power of this project lies in its **flexibility** — provide your own high-level requirements, and the AI Engineering Team will build software tailored to them.

**Workflow:**
1. **Design** → Engineering Lead produces a markdown design doc.  
2. **Backend** → Backend Engineer writes Python implementation.  
3. **Frontend** → Frontend Engineer creates a Gradio UI demo.  
4. **Test** → Test Engineer generates unit tests.  

**Final Output:**  
- 1 design document (`.md`)  
- 3 Python files (`.py`): backend module, Gradio app, unit tests  

---

## Table of Contents
- **Installation**
- **Usage**
- **Project Structure** 
- **Output Snapshots**
- **Known Issues / Limitations**
- **Acknowledgments / Credits**
  
---

## Installation
Follow these steps to set up and run the project:

1. **Clone the repository:**
   ```bash
   git clone <your-repository-url>
   cd engineering_team
   ```

2. **Create a virtual environment and install dependencies (using `uv`):**
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install uv
   uv pip install -r requirements.txt
   ```

3. **Set up environment variables:**
   Create a `.env` file in the root directory with API keys for the LLM provider(s) you’ll use.  

   Example:
   ```bash
   # For Gemini
   GEMINI_API_KEY="your-gemini-api-key"

   # For OpenAI
   OPENAI_API_KEY="sk-your-openai-api-key"

   # For Anthropic
   ANTHROPIC_API_KEY="sk-ant-your-anthropic-api-key"
   ```

   You can also assign different models to agents in  
   `src/engineering_team/config/agents.yaml`.

---

## Usage
Run the Engineering Team crew from the project root:

```bash
crewai run
```

This executes the workflow defined in `src/engineering_team/main.py`.  
Outputs are saved in the `output/` directory.

### Providing Custom Requirements
To build your own software instead of the example:

- Open `src/engineering_team/main.py`
- Update these variables:
  - `requirements` → your high-level requirements  
  - `module_name` → name for your module (e.g., `"todo_list"`)  
  - `class_name` → primary class name (e.g., `"TodoList"`)  

The AI Engineering Team will then generate new design, code, UI, and tests.

### Running the Generated Frontend
After generation, run the Gradio app:

```bash
cd output
uv run app.py
```

If you don’t have **Gradio** installed:
```bash
uv pip install gradio
```

---

## Project Structure
```plaintext
engineering_team/
├── knowledge/
├── output/
│   ├── accounts_design.md
│   ├── accounts.py
│   ├── app.py
│   └── test_accounts.py
├── src/
│   └── engineering_team/
│       ├── __init__.py
│       ├── config/
│       │   ├── agents.yaml
│       │   └── tasks.yaml
│       ├── crew.py
│       ├── main.py
│       └── tools/
├── tests/
└── uv.lock
```
---

## Output Snapshots
<img width="1351" height="777" alt="Screenshot 2025-09-01 at 4 17 29 PM" src="https://github.com/user-attachments/assets/f9b42eb7-d57a-467c-bf57-7f7d36503597" />

<img width="1351" height="777" alt="Screenshot 2025-09-01 at 4 17 18 PM" src="https://github.com/user-attachments/assets/1aa3512e-2cc3-4c1e-b77a-01f0382bded7" />

---

## Known Issues / Limitations
- Outputs may vary between runs.  
- `get_share_price(symbol)` uses fixed mock prices, not real data.  
- Occasionally, generated Python files may include Markdown formatting (e.g., ```python). These need manual cleanup.  

---

## Acknowledgments / Credits
- Built using the **CrewAI framework**.  
- Frontend powered by **Gradio**.  
