# FamilyCart

This application allows family members to create, manage, and share shopping lists in real-time.
This project is designed to be a full-stack application with a focus on real-time updates, user authentication, and a clean API design. It uses FastAPI for the backend, PostgreSQL for the database, and React for the frontend.

## Features

- User authentication with JWT
- OAuth2 with Google and Apple
- Real-time updates with WebSockets
- RESTful API for shopping lists and items
- Database migrations with Alembic

## Prerequisites    

- Docker and Docker Compose
- Python 3.12+
- Git
- pipx: [https://pipx.pypa.io/stable/installation/](https://pipx.pypa.io/stable/installation/)
```powershell
# Install pipx on Windows
python -m pip install --user pipx
python -m pipx ensurepath
echo %PATH%
```
- Poetry: [https://python-poetry.org/docs/#installation](https://python-poetry.org/docs/#installation)
```powershell
# Install Poetry on Windows
pipx install poetry
```
It will be installed into the `%APPDATA%\pypoetry` directory, which should be added to your PATH environment variable.

## (Development Only) Setup VS Code Development Environment and GitHub Copilot and Install and Configure MCP Servers: Fetch, PostgreSQL, Brave Search

To instruct Copilot in VS Code to use workspace/project-specific rules, see documentation: [https://code.visualstudio.com/docs/copilot/copilot-customization](https://code.visualstudio.com/docs/copilot/copilot-customization). Create a file .github/copilot-instructions.md (part of this the repository). Enable VS Code to use GitHub Copilot custom instructions by setting the `github.copilot.customInstructions` setting to `true` in your VS Code settings - [vscode://settings/github.copilot.chat.codeGeneration.useInstructionFiles](vscode://settings/github.copilot.chat.codeGeneration.useInstructionFiles).

> **Note:** The Model Context Protocol (MCP) is a development tool that enhances the experience of using AI tools like GitHub Copilot in VS Code. It is not required for running the application in production or normal usage. General information about MCP [https://modelcontextprotocol.io/introduction](https://modelcontextprotocol.io/introduction), available MCP servers could be found at [https://mcp.so/servers](https://mcp.so/servers) or [https://github.com/modelcontextprotocol/servers](https://github.com/modelcontextprotocol/servers). 

The Fetch MCP Server ([http://mcp.so/server/fetch/modelcontextprotocol](http://mcp.so/server/fetch/modelcontextprotocol)) is only required for development in VS Code with GitHub Copilot. It is not needed for running the application in production or normal usage.

Installation details here: [https://github.com/modelcontextprotocol/servers/tree/main/src/fetch](https://github.com/modelcontextprotocol/servers/tree/main/src/fetch).
1. install uvx - see [https://docs.astral.sh/uv/getting-started/installation/](https://docs.astral.sh/uv/getting-started/installation/): powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
2. See instructions - ensure uvx tool and other are in the Windows PATH either restarting PowerShell / VS Code or in PowerShell type: $env:Path = "C:\Users\janza\.local\bin;$env:Path"
4. To install/configure into VS Code use embedded one-click install here: [https://github.com/modelcontextprotocol/servers/tree/main/src/fetch#configure-for-vs-code](https://github.com/modelcontextprotocol/servers/tree/main/src/fetch#configure-for-vs-code).

> **Note:** The PostgreSQL MCP Server ([http://mcp.so/server/postgres/modelcontextprotocol](http://mcp.so/server/postgres/modelcontextprotocol)) is only required for development in VS Code with GitHub Copilot. It is not needed for running the application in production or normal usage.

1. In the VS Code top search bar, put '>MCP' and choose 'MCP: Add Server...', Choose NPM package, Package name: '@modelcontextprotocol/server-postgres' and store to Workspace settings.
2. Name it postgres
3. In the mcp.json edit the PostgreSQL connect string as per .env file or generally deployed PostgreSQL server, e.g. `postgresql://username:password@localhost:5432/familycart`.
4. It appears as a new Tool in Copilot chat - MCP Server: postgres.
5. To use it in the Copilot chat, you can use the `#query` tag to query the PostgreSQL MCP server.

Brave Search MCP Server ([https://github.com/modelcontextprotocol/servers-archived/tree/main/src/brave-search#usage-with-vs-code](https://github.com/modelcontextprotocol/servers-archived/tree/main/src/brave-search#usage-with-vs-code)) - click on VS Code icon and in VS Code confirm on 'Install Server'. Replace the placeholder in the `mcp.json` file with your Brave Search API key - [https://api-dashboard.search.brave.com/app/keys] (https://api-dashboard.search.brave.com/app/keys).

> **Note:** Recommended MCP Server: GistPad - This server allows you to use GitHub Gists as a storage for your code snippets and other data, which can be very useful for development. See [https://github.com/lostintangent/gistpad-mcp?tab=readme-ov-file](https://github.com/lostintangent/gistpad-mcp?tab=readme-ov-file). Register with GitHub: [https://gistpad.dev/](https://gistpad.dev/), Install GistPad extension in VS Code, and follow the instructions and authorize access to GitHub Gists via GitHub. Check with 'How many gists have I edited this month?' in Agent Chat in VS Code.

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/FamilyCart.git
cd FamilyCart
```

### 2. Set up environment variables

Copy the example environment file and update the values:

```bash
cp .env.example .env
```

Edit the `.env` file with your configuration.

### 3. Start the database

```bash
docker-compose up -d db
```

### 4. Set up Python environment (Backend)

The backend uses [Poetry](https://python-poetry.org/) for dependency management and virtual environment creation.

Navigate to the backend directory:
```bash
cd backend
```

Install dependencies and create/activate the virtual environment:
```bash
poetry install
```
This command will create a `.venv` folder in the `backend` directory and install all necessary dependencies specified in `pyproject.toml`.

To activate the virtual environment, you can use:
```bash
poetry shell
```
Alternatively, you can run commands within the virtual environment using `poetry run <command>`.

### 5. Initialize the database

```bash
# Run migrations
alembic upgrade head

# Or initialize the database directly
python scripts/init_db.py
```

### 6. Run the application

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

## Development

### Running tests

```bash
pytest
```

### Code formatting

```bash
black .
isort .
flake8
```

### Database migrations

To create a new migration:

```bash
alembic revision --autogenerate -m "Your migration message"
```

To apply migrations:

```bash
alembic upgrade head
```

## API Documentation

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## License

MIT
