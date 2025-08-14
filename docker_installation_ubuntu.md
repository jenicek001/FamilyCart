# Docker installation on x64/AMD64 Ubuntu

Here is a comprehensive, step-by-step guide to get Docker running on your x64/AMD64 Ubuntu machine, presented from an industry-professional perspective.

### **Philosophy: Why We Follow These Steps**

We don't just run commands; we understand why we're running them. This method uses Docker's official APT repository. Why?

* **Trust and Security:** We are installing directly from the source, ensuring the software is authentic and hasn't been tampered with. The GPG key verification is a critical part of this trust chain.
* **Up-to-Date Versions:** The official repository guarantees you get the latest stable releases, patches, and security updates as soon as they are available. The version in the standard Ubuntu repositories can be outdated.
* **Ease of Maintenance:** Using a dedicated repository allows you to manage Docker's installation and updates using standard `apt` system tools, just like any other piece of software.

---

### **Step 0: Prerequisites and System Check**

Before we begin, let's ensure your system is ready.

1.  **Supported Ubuntu Version:** Docker is supported on the latest LTS (Long Term Support) versions of Ubuntu and some recent non-LTS versions. As of mid-2025, this includes Ubuntu 24.04, 22.04, and 20.04. You can check your version with:
    ```bash
    lsb_release -a
    ```

2.  **x64/AMD64 Architecture:** Verify your system architecture. This guide is specifically for `x64` (also known as `amd64`).
    ```bash
    dpkg --print-architecture
    ```
    The output should be `amd64`.

3.  **Terminal Access:** You will need a terminal and `sudo` privileges to execute administrative commands.

---

### **Step 1: Uninstall Old Docker Versions**

First, it's crucial to remove any older, unofficial, or conflicting Docker packages that might be on your system. This ensures a clean slate.

```bash
# This command will remove older versions of Docker. It's okay if it reports that none of these packages are installed.
sudo apt-get remove docker docker-engine docker.io containerd runc
```

The contents of `/var/lib/docker/`, including images, containers, and volumes, are preserved. If you need to start completely fresh, you would manually remove that directory, but this is typically not necessary for a standard upgrade.

---

### **Step 2: Set Up Docker's Official APT Repository**

This is the core of the installation. We will configure your system's package manager (`apt`) to download Docker from the official Docker repository.

**1. Update Your Package Index and Install Dependencies:**

First, refresh your local package database and install a few prerequisite packages that allow `apt` to use a repository over HTTPS.

```bash
sudo apt-get update
sudo apt-get install \
    ca-certificates \
    curl \
    gnupg
```

**2. Add Docker's Official GPG Key:**

Next, we download Docker's official GPG key and add it to the system's keychain. This key is used to verify that the Docker packages you download are authentic and have not been tampered with.

```bash
# Create the directory for the key if it doesn't exist
sudo install -m 0755 -d /etc/apt/keyrings

# Download Docker's GPG key
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

# Make the key readable by the apt process
sudo chmod a+r /etc/apt/keyrings/docker.gpg
```

**3. Set Up the Repository Source:**

Now, we add the official Docker repository to your APT sources list. This command sets up the "stable" repository.

```bash
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
```

This command automatically determines your Ubuntu version's codename (e.g., `jammy` for 22.04) and creates the appropriate repository entry.

---

### **Step 3: Install Docker Engine**

With the repository configured, installing Docker is now straightforward.

**1. Update the Package Index Again:**

Since we just added a new repository, we need to update our `apt` package index one more time.

```bash
sudo apt-get update
```

**2. Install Docker Engine, CLI, and Containerd:**

Install the latest stable version of Docker Engine, the command-line interface (CLI), containerd (the container runtime), and the Docker Compose plugin.

```bash
sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```

* **`docker-ce`**: The Docker Community Edition engine.
* **`docker-ce-cli`**: The command-line tool for interacting with the Docker engine.
* **`containerd.io`**: The industry-standard container runtime that actually manages the container lifecycle.
* **`docker-buildx-plugin`**: Enables advanced build features with BuildKit.
* **`docker-compose-plugin`**: Integrates Docker Compose functionality directly into the `docker` command (e.g., `docker compose up`).

---

### **Step 4: Verify the Installation**

Let's ensure Docker is installed and running correctly.

**1. Check the Docker Service Status:**

The Docker service should start automatically upon installation. You can verify this with `systemctl`.

```bash
sudo systemctl status docker
```
You should see output indicating the service is `active (running)`. Press `q` to exit.

**2. Run the "hello-world" Container:**

The canonical way to test a Docker installation is to run the `hello-world` image. This command downloads a minimal test image and runs it in a container. If it runs, your installation is successful.

```bash
sudo docker run hello-world
```

You should see a message that begins with: "Hello from Docker!" This confirms that you can pull images from Docker Hub and run them in containers.

---

### **Step 5: Post-Installation Configuration (Crucial for Usability)**

By default, you must use `sudo` to run Docker commands. This is a security feature, but it's often inconvenient for development. To run Docker commands without `sudo`, you must add your user to the `docker` group.

**1. Create the `docker` Group (if it doesn't already exist):**

The `docker` group is created during installation, but this command will create it if it's missing for any reason.

```bash
sudo groupadd docker
```
*(You can ignore any error that says the group already exists.)*

**2. Add Your User to the `docker` Group:**

Replace `$USER` with your actual username, though the `$USER` variable will typically work correctly.

```bash
sudo usermod -aG docker $USER
```
* `-a` (append): Adds the user to the supplementary group.
* `-G` (group): Specifies the group name.

**3. Apply the New Group Membership:**

**IMPORTANT:** For this change to take effect, you must log out of your current session and log back in, or reboot your machine. You can also activate the changes for the current terminal session with the following command:

```bash
newgrp docker
```
However, a full log-out/log-in cycle is the most reliable method.

After logging back in, you can verify that you can run Docker commands without `sudo`:

```bash
docker run hello-world
```

If this command works without `sudo`, your setup is complete and ready for development.

---

You have now successfully installed and configured Docker on your Ubuntu system following industry best practices. Your environment is secure, maintainable, and ready to build and run containerized applications.
