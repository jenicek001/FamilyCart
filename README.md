# FamilyCart

This application allows family members to create, manage, and share shopping lists in real-time.
This project is designed to be a full-stack application with a focus on real-time updates, user authentication, and a clean API design. It uses FastAPI for the backend, PostgreSQL for the database, and React for the frontend.

## Features

### ✅ Completed (Sprint 1-3)
- **User Authentication**: JWT-based authentication with secure token management (30-day expiration)
- **User Profiles**: Registration with email/password and nickname support
- **Shopping Lists**: Create, edit, delete, and manage multiple shopping lists
- **Item Management**: Add items with categories, quantities, and descriptions
- **Item Completion**: Mark items as purchased/unpurchased with visual feedback
- **Modern UI**: Stitch-inspired design with Material Icons and responsive layout
- **Real-time Updates**: Item changes reflect immediately in the UI
- **Audit Logging**: Track who modified items and when
- **Database Management**: PostgreSQL with Alembic migrations and timezone-aware storage

### 🚧 Planned Features
- **AI-Powered Categorization**: Automatic item categorization and icon assignment
- **List Sharing**: Collaborate with family members on shared shopping lists
- **Real-time Synchronization**: WebSocket-based live updates across devices
- **OAuth2 Integration**: Login with Google and Apple accounts
- **Advanced Organization**: Drag-and-drop reordering and category grouping
- **Search & History**: Smart search with shopping history integration
- **Internationalization**: Multi-language support

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

First make sure npx is installed by typing:
```
npx --version
```
If missing, install npx from: [https://nodejs.org/en](https://nodejs.org/en) (Node.js includes npx).

The Fetch MCP Server ([http://mcp.so/server/fetch/modelcontextprotocol](http://mcp.so/server/fetch/modelcontextprotocol)) is only required for development in VS Code with GitHub Copilot. It is not needed for running the application in production or normal usage.

Installation details here: [https://github.com/modelcontextprotocol/servers/tree/main/src/fetch](https://github.com/modelcontextprotocol/servers/tree/main/src/fetch).
1. Install the `uvx` tool, which is a command-line utility for managing MCP servers. You can install it using PowerShell on Windows:
```powershell
# Install uvx using PowerShell
irm https://astral.sh/uv/install.ps1 | iex
```
2. Ensure the `uvx` tool and other installed tools are available in your Windows `PATH`. After installation, either restart PowerShell and VS Code, or update your current session's `PATH` by running:

```powershell
$env:Path = "$env:USERPROFILE\.local\bin;$env:Path"
```
3. To install/configure into VS Code use embedded one-click install here: [https://github.com/modelcontextprotocol/servers/tree/main/src/fetch#configure-for-vs-code](https://github.com/modelcontextprotocol/servers/tree/main/src/fetch#configure-for-vs-code).

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
# Navigate to the backend directory
cd backend

# Run the start script which handles migrations and starts the server
./scripts/start.sh
```

**Important:** Always use the `scripts/start.sh` script to start the backend as it ensures database migrations are applied before starting the application. Do not run uvicorn directly.

The API will be available at `http://localhost:8000`

## Development

### Running tests

```bash
poetry run pytest
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

## Development Status

### Current Sprint: Sprint 3 - ✅ COMPLETED (2025-06-26)

**Item Completion & UI Enhancement** - All major functionality implemented and tested:

- ✅ **Backend API**: PUT /items/{item_id} endpoint for item completion with proper validation
- ✅ **Frontend UI**: Checkbox controls for marking items as purchased/unpurchased  
- ✅ **Visual Feedback**: Completed items show with strikethrough and faded styling
- ✅ **Toast Notifications**: User feedback when items are marked as complete/incomplete
- ✅ **Audit Logging**: Track who changed item completion status and when
- ✅ **Comprehensive Testing**: Backend unit tests for item completion logic and edge cases
- ✅ **Database Schema**: Timezone-aware datetime handling for proper timestamp management
- ✅ **Error Handling**: Proper validation for unauthorized access and non-existent items

### Next Sprint: Sprint 4 - AI-Powered Features
Focus on automatic item categorization, icon assignment, and category standardization using Google Gemini API.

### Testing Status
- **Backend Tests**: ✅ All core functionality tests passing
- **Database**: ✅ Alembic migrations applied, schema up-to-date
- **API**: ✅ All endpoints working correctly with proper authentication
- **Frontend**: ✅ UI components functional with Stitch design system

See [TASKS.md](./TASKS.md) for detailed sprint planning and task tracking.

## Design System & UI Components

FamilyCart uses a modern, Stitch-inspired design system built with Tailwind CSS and Radix UI components.

### Design Tokens

#### Typography
- **Primary Font**: Plus Jakarta Sans (headings and interface)
- **Secondary Font**: Noto Sans (body text and descriptions)
- **Code Font**: Monospace (code blocks and technical content)

#### Color Palette
- **Primary Colors**: Modern blue and accent colors with proper contrast ratios
- **Category Colors**: Each item category has unique colors and Material Icons
- **Status Colors**: Success, warning, error, and neutral states
- **Dark/Light Mode**: Full theme support with CSS custom properties

#### Spacing & Layout
- **Grid System**: Responsive grid with consistent spacing utilities
- **Border Radius**: Rounded corners following modern design trends
- **Shadows**: Layered shadow system for depth and hierarchy
- **Container**: Centered, max-width containers with responsive breakpoints

### Component Library

#### Core Components
- **Button**: Multiple variants (default, destructive, outline, ghost, link) with size options
- **Card**: Container component for grouped content with proper spacing
- **Input**: Form inputs with validation states and accessibility features
- **Dialog**: Modal dialogs and confirmation prompts
- **Dropdown**: Menu and select components with keyboard navigation
- **Toast**: Notification system for user feedback

#### Shopping List Components
- **ShoppingListView**: Main container with search, filters, and item management
- **ShoppingListItem**: Card-based item display with completion status, editing, and actions
- **SmartSearchBar**: Intelligent search with category filtering and quick add functionality
- **HeaderListSelector**: Multi-list navigation and selection interface

#### Specialized Components
- **UserBadge**: User avatar and information display
- **ConfirmationDialog**: Reusable confirmation prompts with variants
- **Material Icons**: Comprehensive icon system integrated throughout the UI

### Accessibility Features
- **ARIA Labels**: All interactive elements include proper accessibility labels
- **Focus States**: Visible focus indicators for keyboard navigation
- **Color Contrast**: WCAG-compliant color ratios for text and backgrounds
- **Screen Reader Support**: Semantic HTML and proper heading hierarchy
- **Keyboard Navigation**: Full keyboard accessibility for all features

### Responsive Design
- **Mobile First**: Design system optimized for mobile devices
- **Breakpoints**: sm (640px), md (768px), lg (1024px), xl (1280px), 2xl (1536px)
- **Flexible Layouts**: Components adapt gracefully across all screen sizes
- **Touch Targets**: Proper sizing for touch interactions on mobile devices

### Development Guidelines
- **Component Reusability**: All UI patterns abstracted into reusable components
- **Consistent Styling**: Centralized design tokens prevent style inconsistencies
- **Performance**: Optimized for fast loading and smooth interactions
- **Maintainability**: Well-documented components with clear prop interfaces

For implementation details, see the `/frontend/src/components/ui/` directory and `tailwind.config.ts`.

## API Documentation

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## License

MIT
# CI/CD Healthcheck Fix - Wed 24 Sep 2025 10:19:05 AM CEST
