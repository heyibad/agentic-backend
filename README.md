# Agentic Backend
Dedicated to Create Ai Agentic Backend wrapper, Full Functional AI Agent Wrapper

Framework: FastAPI

[![Hacktoberfest](https://img.shields.io/badge/hacktoberfest-welcome-brightgreen?style=flat-square)](https://hacktoberfest.com)

This repository contains the backend services for the Agentic project.

## Hacktoberfest

We welcome contributions! This repo is set up to be friendly for Hacktoberfest contributors.

See `CONTRIBUTING.md` for ways to get started. If you're participating in Hacktoberfest, check the `good first issue` label and the issue templates when opening an issue.

See [GOOD_FIRST_ISSUES.md](GOOD_FIRST_ISSUES.md) for some small starter tasks you can pick up.

## Running locally
To run the backend server locally, follow these steps:
## Run Locally

To run this project locally:

1. Clone the repo  
   ```bash
   git clone https://github.com/heyibad/agentic-backend.git
   cd agentic-backend

2. Install dependencies (this project uses `uv` as a package manager, but you can adapt accordingly):

 ```powershell
 uv sync  
```
```powershell
 uv venv  
```
> Note: If you use a different package manager, adapt the command accordingly or Install UV.
3. Run the server locally with uvicorn:

```powershell
uvicorn app.main:app --reload --port 8080
``` 
