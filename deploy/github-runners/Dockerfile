FROM ubuntu:22.04

# Avoid prompts from apt
ENV DEBIAN_FRONTEND=noninteractive

# Set runner version and architecture
ARG RUNNER_VERSION=2.317.0
ARG RUNNER_ARCH=x64

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

# Install Python 3.11
RUN add-apt-repository ppa:deadsnakes/ppa \
    && apt-get update \
    && apt-get install -y \
        python3.11 \
        python3.11-dev \
        python3.11-distutils \
        python3-pip \
    && update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 1 \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 - \
    && ln -s /root/.local/bin/poetry /usr/local/bin/poetry

# Install additional tools for FamilyCart builds
RUN npm install -g \
        typescript \
        eslint \
        prettier \
        @playwright/test \
    && python3 -m pip install \
        black \
        isort \
        pylint \
        bandit \
        pytest \
        pytest-cov

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
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
  CMD pgrep -f "Runner.Listener" || exit 1

ENTRYPOINT ["/entrypoint.sh"]