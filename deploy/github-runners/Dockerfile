FROM ubuntu:24.04

# Avoid prompts from apt
ENV DEBIAN_FRONTEND=noninteractive

# Set runner version and architecture
ARG RUNNER_VERSION=2.317.0
ARG RUNNER_ARCH=x64
ARG DOCKER_GID=999

# Labels
LABEL org.opencontainers.image.title="FamilyCart GitHub Runner"
LABEL org.opencontainers.image.description="Self-hosted GitHub Actions runner for FamilyCart"
LABEL org.opencontainers.image.version="${RUNNER_VERSION}"

# Install base dependencies
RUN apt-get update \
    && apt-get install -y \
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
        gpg-agent \
        software-properties-common \
        build-essential \
        zlib1g-dev \
        gettext \
        libcurl4-openssl-dev \
        libedit-dev \
        libssl-dev \
        libffi-dev \
        libicu-dev \
        libsqlite3-dev \
        libxml2-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Docker CLI and Docker Compose
RUN curl -fsSL https://get.docker.com | sh \
    && curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose \
    && chmod +x /usr/local/bin/docker-compose

# Install Node.js 20
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs

# Install Python 3.12 (native in Ubuntu 24.04)
RUN apt-get update \
    && apt-get install -y \
        python3.12 \
        python3.12-dev \
        python3.12-venv \
        python3-pip \
    && update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.12 1 \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | POETRY_HOME=/opt/poetry python3 - \
    && ln -s /opt/poetry/bin/poetry /usr/local/bin/poetry \
    && chmod +x /opt/poetry/bin/poetry

# Install additional tools for FamilyCart builds
RUN npm install -g \
        typescript \
        eslint \
        prettier \
        @playwright/test

# Create minimal Poetry project for runner tools
RUN mkdir -p /runner-tools && cd /runner-tools && \
    echo '[tool.poetry]' > pyproject.toml && \
    echo 'name = "github-runner-tools"' >> pyproject.toml && \
    echo 'version = "0.1.0"' >> pyproject.toml && \
    echo 'description = "Development tools for GitHub Actions runner"' >> pyproject.toml && \
    echo 'authors = ["FamilyCart Team"]' >> pyproject.toml && \
    echo 'package-mode = false' >> pyproject.toml && \
    echo '' >> pyproject.toml && \
    echo '[tool.poetry.dependencies]' >> pyproject.toml && \
    echo 'python = "^3.12"' >> pyproject.toml && \
    echo '' >> pyproject.toml && \
    echo '[tool.poetry.group.dev.dependencies]' >> pyproject.toml && \
    echo 'black = "*"' >> pyproject.toml && \
    echo 'isort = "*"' >> pyproject.toml && \
    echo 'pylint = "*"' >> pyproject.toml && \
    echo 'bandit = "*"' >> pyproject.toml && \
    echo 'pytest = "*"' >> pyproject.toml && \
    echo 'pytest-cov = "*"' >> pyproject.toml && \
    echo '' >> pyproject.toml && \
    echo '[build-system]' >> pyproject.toml && \
    echo 'requires = ["poetry-core"]' >> pyproject.toml && \
    echo 'build-backend = "poetry.core.masonry.api"' >> pyproject.toml && \
    poetry config virtualenvs.create false && \
    poetry install --no-root

# Install security scanning tools
RUN curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh | sh -s -- -b /usr/local/bin

# Install k6 for load testing
RUN wget https://github.com/grafana/k6/releases/download/v0.47.0/k6-v0.47.0-linux-amd64.tar.gz \
    && tar -xzf k6-v0.47.0-linux-amd64.tar.gz \
    && mv k6-v0.47.0-linux-amd64/k6 /usr/local/bin/ \
    && rm -rf k6-v0.47.0-linux-amd64*

# Create runner user
RUN useradd -m -s /bin/bash runner \
    && usermod -aG sudo runner \
    && echo "runner ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

# Fix docker group GID to match host and add runner to docker group
RUN groupmod -g ${DOCKER_GID} docker \
    && usermod -aG docker runner

# Set up runner directory
WORKDIR /home/runner

# Download and extract GitHub Actions runner
RUN curl -L "https://github.com/actions/runner/releases/download/v${RUNNER_VERSION}/actions-runner-linux-${RUNNER_ARCH}-${RUNNER_VERSION}.tar.gz" \
    | tar xz \
    && chown -R runner:runner /home/runner

# Install runner dependencies
RUN ./bin/installdependencies.sh

# Create work directory with proper permissions
RUN mkdir -p /home/runner/work \
    && chown -R runner:runner /home/runner/work \
    && chmod -R 755 /home/runner/work

# Copy entrypoint script
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

USER runner

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
  CMD pgrep -f "Runner.Listener" || exit 1

ENTRYPOINT ["/entrypoint.sh"]