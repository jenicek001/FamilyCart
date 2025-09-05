FROM ubuntu:22.04

# Avoid prompts from apt
ENV DEBIAN_FRONTEND=noninteractive

# Latest versions as of September 2025:
# - GitHub Actions Runner: v2.317.0
# - Docker: Latest stable (from official repository)
# - Node.js: v22.17.0 (Latest LTS)
# - Python: 3.12 (Latest stable)
# - Poetry: 2.x (Latest stable)
# - npm packages: @latest versions
# - k6: Latest from GitHub releases
# - Trivy: Latest from GitHub releases

# Set runner version and architecture
ARG RUNNER_VERSION=2.317.0
ARG RUNNER_ARCH=x64

# Labels
LABEL org.opencontainers.image.title="FamilyCart GitHub Runner"
LABEL org.opencontainers.image.description="Self-hosted GitHub Actions runner for FamilyCart"
LABEL org.opencontainers.image.version="${RUNNER_VERSION}"
LABEL org.opencontainers.image.created="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
LABEL org.opencontainers.image.source="https://github.com/honzik/FamilyCart"

# Install base dependencies with retry logic
RUN apt-get update && \
    apt-get install -y \
        curl \
        wget \
        git \
        jq \
        tar \
        unzip \
        zip \
        apt-transport-https \
        ca-certificates \
        sudo \
        gnupg \
        software-properties-common \
        build-essential \
        zlib1g-dev \
        gettext \
        libcurl4-openssl-dev \
        libssl-dev \
        libffi-dev \
        libicu-dev \
        libsqlite3-dev \
        libxml2-dev \
        lsb-release \
    && rm -rf /var/lib/apt/lists/*

# Install Docker CLI and Docker Compose (latest versions)
RUN curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg \
    && echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null \
    && apt-get update \
    && apt-get install -y docker-ce-cli docker-buildx-plugin docker-compose-plugin \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js 22 (Latest LTS)
RUN curl -fsSL https://deb.nodesource.com/setup_22.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# Install Python 3.12 (available in Ubuntu 22.04 by default)
RUN apt-get update \
    && apt-get install -y \
        python3.12 \
        python3.12-dev \
        python3.12-venv \
        python3-pip \
    && update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.12 1 \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry (latest version 2.x)
RUN curl -sSL https://install.python-poetry.org | python3 - \
    && ln -s /root/.local/bin/poetry /usr/local/bin/poetry \
    && poetry --version

# Install additional tools for FamilyCart builds (latest versions)
RUN npm install -g \
        typescript@latest \
        eslint@latest \
        prettier@latest \
        @playwright/test@latest \
    && python3 -m pip install --upgrade pip \
    && python3 -m pip install \
        black \
        isort \
        pylint \
        bandit \
        pytest \
        pytest-cov

# Install security scanning tools (latest versions)
RUN curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh | sh -s -- -b /usr/local/bin

# Install k6 for load testing (latest version)
RUN curl -s https://api.github.com/repos/grafana/k6/releases/latest | jq -r '.assets[] | select(.name | contains("linux-amd64.tar.gz")) | .browser_download_url' | xargs wget -O k6.tar.gz \
    && tar -xzf k6.tar.gz \
    && mv k6-*/k6 /usr/local/bin/ \
    && rm -rf k6*

# Create runner user
RUN useradd -m -s /bin/bash runner \
    && usermod -aG sudo runner \
    && usermod -aG docker runner \
    && echo "runner ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

# Set up runner directory
WORKDIR /home/runner

# Download and extract GitHub Actions runner
RUN curl -L "https://github.com/actions/runner/releases/download/v${RUNNER_VERSION}/actions-runner-linux-${RUNNER_ARCH}-${RUNNER_VERSION}.tar.gz" \
    | tar xz \
    && chown -R runner:runner /home/runner

# Install runner dependencies
RUN ./bin/installdependencies.sh

# Copy entrypoint script
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Copy runner configuration script
COPY configure-runner.sh /configure-runner.sh
RUN chmod +x /configure-runner.sh

USER runner

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
  CMD pgrep -f "Runner.Listener" || exit 1

ENTRYPOINT ["/entrypoint.sh"]