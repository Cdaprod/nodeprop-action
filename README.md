
# NodeProp Configuration Generator Action

[![Generate the NodeProp YAML Configuration File](https://github.com/Cdaprod/nodeprop-action/actions/workflows/generate-nodeprop.yml/badge.svg)](https://github.com/Cdaprod/nodeprop-action/actions/workflows/generate-nodeprop.yml)

This GitHub Action generates and manages content-addressable repository configurations using hash-based identifiers. It analyzes your repository's structure, capabilities, and metadata to create a standardized configuration file.

## Features

- Content-addressable configuration storage using SHA-256 hashing
- Automatic detection of repository capabilities
- Integration with GitHub metadata
- Support for Docker and Docker Compose configurations
- Customizable configuration output

## Usage

Add the following workflow to your repository (e.g., `.github/workflows/nodeprop.yml`):

```yaml
name: Generate NodeProp Configuration

on:
  push:
    branches: [ '**' ]
    tags: [ '*' ]
  workflow_dispatch:
  schedule:
    - cron: '0 0 * * *' # Optional: Runs daily at midnight UTC

jobs:
  generate-config:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Generate NodeProp Configuration
        uses: cdaprod/nodeprop-action@main
        with:
          github-token: ${{ secrets.GITHUB_TOKEN }}
          config-file: '.nodeprop.yml'  # Optional: defaults to .nodeprop.yml
          storage-path: 'configs'        # Optional: path for content-addressable storage
```

## Inputs

| Input | Description | Required | Default |
|-------|-------------|----------|---------|
| `github-token` | GitHub token for API access | Yes | N/A |
| `config-file` | Name of the configuration file to generate | No | `.nodeprop.yml` |
| `storage-path` | Path to store configurations | No | `configs` |

## Outputs

| Output | Description |
|--------|-------------|
| `config-hash` | Hash of the generated configuration |
| `config-path` | Path to the generated configuration file |

## Configuration Format

The generated configuration file includes:

- Unique content-based identifier (SHA-256 hash)
- Repository metadata and capabilities
- Docker and Docker Compose configurations
- GitHub repository statistics
- Custom properties for deployment

Example configuration:

```yaml
id: <content-hash>
name: owner/repository
address: https://github.com/owner/repository
capabilities:
  - containerized
  - pipeline
status: active
metadata:
  description: "Auto-generated configuration for owner/repository"
  owner: github-username
  last_updated: "2024-11-13T00:00:00Z"
  tags: []
  github:
    stars: 0
    forks: 0
    issues: 0
    pull_requests:
      open: 0
      closed: 0
    latest_commit: ""
    license: "MIT"
    topics: []
  custom_properties:
    deploy_environment: null
    monitoring_enabled: null
    auto_scale: null
    service: null
    app: repository
    image: "owner/repository:1234567"
    network: "project-domain-namespace"
    domain: "repository.owner.dev"
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📜 License

MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👥 Connect with Cdaprod

<div align="center">
  <p>
    <a href="https://youtube.com/@Cdaprod">
      <img src="https://img.shields.io/badge/YouTube-FF0000?style=for-the-badge&logo=youtube&logoColor=white" alt="YouTube Channel" />
    </a>
    <a href="https://twitter.com/cdasmktcda">
      <img src="https://img.shields.io/badge/Twitter-1DA1F2?style=for-the-badge&logo=twitter&logoColor=white" alt="Twitter Follow" />
    </a>
    <a href="https://www.linkedin.com/in/cdasmkt">
      <img src="https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white" alt="LinkedIn" />
    </a>
    <a href="https://github.com/Cdaprod">
      <img src="https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white" alt="GitHub followers" />
    </a>
    <a href="https://sanity.cdaprod.dev">
      <img src="https://img.shields.io/badge/Blog-FF5722?style=for-the-badge&logo=blogger&logoColor=white" alt="Personal Blog" />
    </a>
  </p>
</div>

<div align="center">
  <p>Built with ❤️ by <a href="https://github.com/Cdaprod">Cdaprod</a></p>
  <p><em>Making Enterprise Software Awesome!</em></p>
</div>