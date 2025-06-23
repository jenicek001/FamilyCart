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

- Docker and Docker Compose – see [docker_installation_ubuntu.md](./docker_installation_ubuntu.md) in this repository for installation instructions.
- Python 3.12+
- Git
- pipx: [https://pipx.pypa.io/stable/installation/](https://pipx.pypa.io/stable/installation/)
```powershell
# Install pipx on Windows
python -m pip install --user pipx
python -m pipx ensurepath
echo %PATH%
```
```bash
# Install pipx on Linux
sudo apt update
sudo apt install pipx
pipx ensurepath
```
- Poetry: [https://python-poetry.org/docs/#installation](https://python-poetry.org/docs/#installation)
```powershell
# Install Poetry on Windows
pipx install poetry
```
It will be installed into the `%APPDATA%\pypoetry` directory, which should be added to your PATH environment variable.

## (Development Only) Setup VS Code Development Environment and GitHub Copilot and Install and Configure MCP Servers: Fetch, PostgreSQL, Brave Search

### First time Git configuration
```bash
git config --global user.name "Jan Zahradnik"
git config --global user.email jan.zahradnik@centrum.cz
```

To instruct Copilot in VS Code to use workspace/project-specific rules, see documentation: [https://code.visualstudio.com/docs/copilot/copilot-customization](https://code.visualstudio.com/docs/copilot/copilot-customization). Create a file .github/copilot-instructions.md (part of this the repository). Enable VS Code to use GitHub Copilot custom instructions by setting the `github.copilot.customInstructions` setting to `true` in your VS Code settings - [vscode://settings/github.copilot.chat.codeGeneration.useInstructionFiles](vscode://settings/github.copilot.chat.codeGeneration.useInstructionFiles).

> **Note:** The Model Context Protocol (MCP) is a development tool that enhances the experience of using AI tools like GitHub Copilot in VS Code. It is not required for running the application in production or normal usage. General information about MCP [https://modelcontextprotocol.io/introduction](https://modelcontextprotocol.io/introduction), available MCP servers could be found at [https://mcp.so/servers](https://mcp.so/servers) or [https://github.com/modelcontextprotocol/servers](https://github.com/modelcontextprotocol/servers). 

The Fetch MCP Server ([http://mcp.so/server/fetch/modelcontextprotocol](http://mcp.so/server/fetch/modelcontextprotocol)) is only required for development in VS Code with GitHub Copilot. It is not needed for running the application in production or normal usage.

Installation details here: [https://github.com/modelcontextprotocol/servers/tree/main/src/fetch](https://github.com/modelcontextprotocol/servers/tree/main/src/fetch).
1. install uvx - see [https://docs.astral.sh/uv/getting-started/installation/](https://docs.astral.sh/uv/getting-started/installation/): powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
2. See instructions - ensure uvx tool and other are in the Windows PATH either restarting PowerShell / VS Code or in PowerShell type: $env:Path = "C:\Users\janza\.local\bin;$env:Path"
4. To install/configure into VS Code use embedded one-click install here: [https://github.com/modelcontextprotocol/servers/tree/main/src/fetch#configure-for-vs-code](https://github.com/modelcontextprotocol/servers/tree/main/src/fetch#configure-for-vs-code).

> **Note:** The PostgreSQL MCP Server ([http://mcp.so/server/postgres/modelcontextprotocol](http://mcp.so/server/postgres/modelcontextprotocol)) is only required for development in VS Code with GitHub Copilot. It is not needed for running the application in production or normal usage.

1. Install npx - see [https://ubuntushell.com/install-npx/](https://ubuntushell.com/install-npx/) - 
```bash
sudo apt install npm
npx -v
```
2. In the VS Code top search bar, put '>MCP' and choose 'MCP: Add Server...', Choose NPM package, Package name: '@modelcontextprotocol/server-postgres' and store to Workspace settings.
3. Name it postgres
4. In the mcp.json edit the PostgreSQL connect string as per .env file or generally deployed PostgreSQL server, e.g. `postgresql://username:password@localhost:5432/familycart`.
5. It appears as a new Tool in Copilot chat - MCP Server: postgres.
6. To use it in the Copilot chat, you can use the `#query` tag to query the PostgreSQL MCP server.

Brave Search MCP Server ([https://github.com/modelcontextprotocol/servers-archived/tree/main/src/brave-search#usage-with-vs-code](https://github.com/modelcontextprotocol/servers-archived/tree/main/src/brave-search#usage-with-vs-code)) - click on VS Code icon and in VS Code confirm on 'Install Server'. Replace the placeholder in the `mcp.json` file with your Brave Search API key - [https://api-dashboard.search.brave.com/app/keys] (https://api-dashboard.search.brave.com/app/keys).

> **Note:** Recommended MCP Server: GistPad - This server allows you to use GitHub Gists as a storage for your code snippets and other data, which can be very useful for development. See [https://github.com/lostintangent/gistpad-mcp?tab=readme-ov-file](https://github.com/lostintangent/gistpad-mcp?tab=readme-ov-file). Register with GitHub: [https://gistpad.dev/](https://gistpad.dev/), Install GistPad extension in VS Code, and follow the instructions and authorize access to GitHub Gists via GitHub. Check with 'How many gists have I edited this month?' in Agent Chat in VS Code.

---

**Playwright MCP Server** ([https://github.com/microsoft/playwright-mcp/](https://github.com/microsoft/playwright-mcp/))

The Playwright MCP server provides browser automation capabilities using Playwright, enabling LLMs and tools to interact with web pages through structured accessibility snapshots (not screenshots). This is useful for automated browser testing, scraping, and LLM-driven web navigation.

**Key Features:**
- Fast, lightweight, and deterministic (uses Playwright's accessibility tree)
- LLM-friendly (no vision models required)
- Supports multiple browsers: Chrome, Firefox, WebKit, Edge
- Can run in snapshot (default) or vision (screenshot-based) mode

**Requirements:**
- Node.js 18 or newer
- VS Code, Cursor, or any MCP-compatible client

**Installation & Configuration:**
1. Install via VS Code MCP integration or manually add to your `mcp.json`:
   ```json
   {
     "mcpServers": {
       "playwright": {
         "command": "npx",
         "args": ["@playwright/mcp@latest"]
       }
     }
   }
   ```
2. To enable vision (screenshot) mode, add the `--vision` flag to the args list.
3. For advanced configuration (browser, port, user data dir, etc.), see the [Playwright MCP README](https://github.com/microsoft/playwright-mcp/) or run:
   ```bash
   npx @playwright/mcp@latest --help
   ```
4. To run as a standalone server (e.g., for remote access or custom port):
   ```bash
   npx @playwright/mcp@latest --port 8931
   ```
   Then set the MCP client config `url` to `http://localhost:8931/sse`.

**User Profile Modes:**
- Persistent (default): Stores login/session state between runs (location can be overridden with `--user-data-dir`)
- Isolated: Each session is stateless (useful for testing, can provide initial state with `--storage-state`)

See the [official documentation](https://github.com/microsoft/playwright-mcp/) for more details and advanced options.

**GitHub MCP Server** ([https://mcp.so/server/github/modelcontextprotocol](https://mcp.so/server/github/modelcontextprotocol?tab=tools))

The GitHub MCP server enables repository management, file operations, and full GitHub API integration via the Model Context Protocol. It provides tools for creating/updating files, searching repositories/code/issues, managing pull requests, issues, branches, and more—all accessible to LLMs and automation tools.

**Key Features:**
- Create, update, and search repositories, files, code, and issues
- Manage pull requests, branches, and commits
- Integrate with GitHub Actions and workflows
- Supports all major repository management operations

**Requirements:**
- Docker (recommended for easiest setup)
- A GitHub Personal Access Token (with appropriate repo permissions)

**Installation & Configuration:**
1. Add the following to your `mcp.json` (or MCP client configuration):
   ```json
   {
     "mcpServers": {
       "github": {
         "command": "docker",
         "args": [
           "run",
           "-i",
           "--rm",
           "-e",
           "GITHUB_PERSONAL_ACCESS_TOKEN",
           "mcp/github"
         ],
         "env": {
           "GITHUB_PERSONAL_ACCESS_TOKEN": "<YOUR_TOKEN>"
         }
       }
     }
   }
   ```
   Replace `<YOUR_TOKEN>` with your GitHub Personal Access Token.
2. For more details and advanced usage, see the [official documentation](https://github.com/modelcontextprotocol/servers/tree/main/src/github).

After setup, the GitHub MCP server will be available as a tool in your MCP-compatible client (e.g., Copilot Chat in VS Code), allowing you to automate and manage GitHub repositories programmatically.

**Context7 MCP Server** ([https://github.com/upstash/context7](https://github.com/upstash/context7?tab=readme-ov-file))

Context7 MCP provides up-to-date, version-specific code documentation and examples for LLMs and AI coding assistants. It fetches the latest docs and code snippets for libraries and frameworks, reducing hallucinated or outdated code in AI-generated answers.

**Key Features:**
- Fetches real-time, version-specific documentation and code examples
- Supports a wide range of libraries and frameworks
- Integrates with Cursor, Windsurf, Claude Desktop, VS Code, and other MCP clients
- Tools for resolving library IDs and fetching docs by topic

**Requirements:**
- Node.js >= 18
- MCP-compatible client (Cursor, Windsurf, Claude Desktop, VS Code, etc.)

**Installation & Configuration:**
1. Install via VS Code MCP integration or manually add to your `mcp.json`:
   ```json
   {
     "mcpServers": {
       "context7": {
         "command": "npx",
         "args": ["-y", "@upstash/context7-mcp@latest"]
       }
     }
   }
   ```
2. To run as a standalone server with HTTP or SSE transport (for remote or custom port):
   ```bash
   npx -y @upstash/context7-mcp@latest --transport http --port 8080
   ```
   Then set the MCP client config `url` to `http://localhost:8080` (or your chosen port).
3. For advanced usage, see the [official documentation](https://github.com/upstash/context7?tab=readme-ov-file).

After setup, Context7 MCP will be available as a tool in your MCP-compatible client, providing instant, up-to-date code docs and examples for your prompts.


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

#### Get Google API key
Get key on [Google AI Studio](https://aistudio.google.com/apikey).

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

### Install Prettier Extension for VS Code

To ensure consistent code formatting, install the official Prettier extension in VS Code:

1. Open VS Code and go to the Extensions view (`Ctrl+Shift+X`).
2. Search for "Prettier - Code formatter" by Prettier.
3. Click "Install".
4. (Recommended) Set Prettier as your default formatter:
   - Open Command Palette (`Ctrl+Shift+P`), type `Format Document With...`, then select `Configure Default Formatter` and choose `Prettier - Code formatter`.
5. (Optional) Enable format on save:
   - Go to Settings (`Ctrl+,`), search for "format on save", and enable `Editor: Format On Save`.

This will help maintain code style consistency across the project.

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
