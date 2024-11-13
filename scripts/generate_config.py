#!/usr/bin/env python3

import os
import yaml
import hashlib
import json
from datetime import datetime, UTC
import urllib.request
import urllib.error
import sys
from typing import Dict, Any, Tuple

class NoAliasDumper(yaml.SafeDumper):
    """Custom YAML dumper that prevents alias creation."""
    def ignore_aliases(self, data):
        return True

class ConfigGenerator:
    """Generates standardized configuration files for repository properties."""
    
    def __init__(self):
        """Initialize the configuration generator with environment variables."""
        self.config_file = os.getenv('CONFIG_FILE_NAME', '.nodeprop.yml')
        self.storage_path = os.getenv('STORAGE_PATH', 'configs')
        self.github_token = os.getenv('GITHUB_TOKEN')
        self.github_repository = os.getenv('GITHUB_REPOSITORY', 'unknown/unknown')
        self.github_sha = os.getenv('GITHUB_SHA', '')
        self.github_actor = os.getenv('GITHUB_ACTOR', 'unknown')
        
        # Parse repository information
        self.repo_owner = self.github_repository.split('/')[0] if '/' in self.github_repository else 'unknown'
        self.repo_name = self.github_repository.split('/')[1] if '/' in self.github_repository else 'unknown'
        
        # Network and domain configuration
        self.network_namespace = f"{self.repo_owner}-network"
        self.domain_base = "cdaprod.dev"

    def get_current_utc(self) -> str:
        """Get current UTC time in ISO format."""
        return datetime.now(UTC).strftime('%Y-%m-%dT%H:%M:%SZ')

    def fetch_github_metadata(self) -> Dict[str, Any]:
        """Fetch repository metadata from GitHub API."""
        default_metadata = {
            "stars": 0,
            "forks": 0,
            "issues": 0,
            "license": "No License",
            "latest_commit": self.get_current_utc()
        }

        if not self.github_token:
            print("Warning: GITHUB_TOKEN not set")
            return default_metadata

        try:
            repo_url = f"https://api.github.com/repos/{self.github_repository}"
            headers = {
                "Authorization": f"token {self.github_token}",
                "Accept": "application/vnd.github.v3+json"
            }

            request = urllib.request.Request(repo_url, headers=headers)
            try:
                with urllib.request.urlopen(request) as response:
                    repo_data = json.loads(response.read().decode())
                    return {
                        "stars": repo_data.get("stargazers_count", 0),
                        "forks": repo_data.get("forks_count", 0),
                        "issues": repo_data.get("open_issues_count", 0),
                        "license": repo_data.get("license", {}).get("spdx_id", "No License"),
                        "latest_commit": repo_data.get("updated_at", self.get_current_utc())
                    }
            except Exception as e:
                print(f"Warning: Failed to fetch repo data: {str(e)}")
                return default_metadata

        except Exception as e:
            print(f"Warning: Failed to fetch GitHub metadata: {str(e)}")
            return default_metadata

    def detect_capabilities(self) -> list:
        """Detect repository capabilities based on file presence."""
        capabilities = []
        files_to_check = {
            'Dockerfile': 'containerized',
            'docker-compose.yml': 'docker-compose',
            'docker-compose.yaml': 'docker-compose',
            '.github/workflows': 'pipeline',
            'deploy.yaml': 'deployable',
            'deploy.yml': 'deployable'
        }
        
        for file_path, capability in files_to_check.items():
            if os.path.exists(file_path):
                capabilities.append(capability)
        
        return list(set(capabilities))

    def generate_network_identifiers(self) -> Dict[str, str]:
        """Generate network-related identifiers for the repository."""
        domain = f"{self.repo_name}.{self.domain_base}"
        return {
            'namespace': self.network_namespace,
            'domain': domain,
            'service_dns': f"{self.repo_name}.{self.network_namespace}.svc",
            'cluster_dns': f"{self.repo_name}.{self.network_namespace}.svc.cluster.local",
            'service_name': self.repo_name
        }

    def compute_config_hash(self, config_data: Dict) -> Tuple[str, str]:
        """Compute content hash of configuration data."""
        config_yaml = yaml.dump(config_data, sort_keys=True, default_flow_style=False)
        header = f"config {len(config_yaml.encode('utf-8'))}\0"
        combined = header.encode('utf-8') + config_yaml.encode('utf-8')
        config_hash = hashlib.sha256(combined).hexdigest()
        return config_hash, config_yaml

    def generate_config(self) -> Dict:
        """Generate the complete configuration."""
        try:
            metadata = self.fetch_github_metadata()
            capabilities = self.detect_capabilities()
            network_ids = self.generate_network_identifiers()

            base_config = {
                'name': self.github_repository,
                'address': f"https://github.com/{self.github_repository}",
                'capabilities': capabilities,
                'status': 'active',
                'metadata': {
                    'description': f"Auto-generated configuration for {self.github_repository}",
                    'owner': self.github_actor,
                    'last_updated': self.get_current_utc(),
                    'github': {
                        'stars': metadata.get('stars', 0),
                        'forks': metadata.get('forks', 0),
                        'issues': metadata.get('issues', 0),
                        'latest_commit': metadata.get('latest_commit', ''),
                        'license': metadata.get('license', 'No License')
                    },
                    'custom_properties': {
                        'deploy_environment': None,
                        'monitoring_enabled': None,
                        'auto_scale': None,
                        'service': None,
                        'app': self.repo_name,
                        'image': f"{self.github_repository}:{self.github_sha[:7]}",
                        'domain': network_ids['domain'],
                        'network': self.network_namespace,
                        'networking': network_ids
                    }
                }
            }

            return base_config

        except Exception as e:
            print(f"Error in generate_config: {str(e)}")
            raise

    def main(self) -> int:
        """Main execution function."""
        try:
            # Ensure storage directory exists
            os.makedirs(self.storage_path, exist_ok=True)

            # Generate base configuration
            base_config = self.generate_config()
            
            # Compute hash
            config_hash, _ = self.compute_config_hash(base_config)
            
            # Create final config with ID at the top
            final_config = {
                'id': config_hash,
                **base_config
            }
            
            # Write configuration file
            with open(self.config_file, 'w') as f:
                yaml.dump(final_config, f, 
                         sort_keys=False, 
                         default_flow_style=False, 
                         Dumper=NoAliasDumper)
            
            # Store hash for GitHub Actions output
            with open('.nodeprop-hash', 'w') as f:
                f.write(config_hash)

            print(f"Successfully generated configuration with hash: {config_hash}")
            return 0

        except Exception as e:
            print(f"Fatal error: {str(e)}")
            return 1

if __name__ == "__main__":
    generator = ConfigGenerator()
    sys.exit(generator.main())