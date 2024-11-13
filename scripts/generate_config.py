#!/usr/bin/env python3

import os
import yaml
import hashlib
import json
from datetime import datetime
import subprocess
from typing import Tuple, Dict, Any
import urllib.request
import urllib.error
import sys

class ConfigGenerator:
    def __init__(self):
        self.config_file = os.getenv('CONFIG_FILE_NAME', '.nodeprop.yml')
        self.storage_path = os.getenv('STORAGE_PATH', 'configs')
        self.github_token = os.getenv('GITHUB_TOKEN')
        self.github_repository = os.getenv('GITHUB_REPOSITORY', 'unknown/unknown')
        self.github_sha = os.getenv('GITHUB_SHA', '')
        self.github_actor = os.getenv('GITHUB_ACTOR', 'unknown')

    def run_command(self, cmd: str) -> str:
        """Execute a shell command and return its output."""
        try:
            result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            print(f"Warning: Command failed: {cmd}")
            print(f"Error: {e.stderr}")
            return ""

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
                if capability not in capabilities:
                    capabilities.append(capability)
        
        return capabilities

    def fetch_github_metadata(self) -> Dict[str, Any]:
        """Fetch repository metadata from GitHub API with improved error handling."""
        if not self.github_token:
            print("Warning: GITHUB_TOKEN not set. Limited API access available.")
            return self._get_default_metadata()

        repo_owner, repo_name = self.github_repository.split('/')
        base_url = f"https://api.github.com/repos/{self.github_repository}"
        headers = {
            "Authorization": f"token {self.github_token}",
            "Accept": "application/vnd.github.v3+json"
        }

        def fetch_url(url: str, default_value: Dict = None) -> Dict:
            if default_value is None:
                default_value = {}
            
            try:
                request = urllib.request.Request(url, headers=headers)
                with urllib.request.urlopen(request) as response:
                    return json.loads(response.read().decode())
            except urllib.error.HTTPError as e:
                print(f"Warning: Failed to fetch {url}: HTTP {e.code}")
                return default_value
            except urllib.error.URLError as e:
                print(f"Warning: Failed to fetch {url}: {e.reason}")
                return default_value
            except Exception as e:
                print(f"Warning: Unexpected error fetching {url}: {e}")
                return default_value

        # Fetch basic repository information
        repo_data = fetch_url(base_url, {"message": "Not Found"})
        
        # Check if we got a valid response
        if repo_data.get("message") == "Not Found":
            print(f"Warning: Repository {self.github_repository} not found or token lacks permissions")
            return self._get_default_metadata()

        # Fetch additional metadata with default values
        topics_data = fetch_url(f"{base_url}/topics", {"names": []})
        pulls_open = len(fetch_url(f"{base_url}/pulls?state=open", []))
        pulls_closed = len(fetch_url(f"{base_url}/pulls?state=closed", []))
        issues_open = len(fetch_url(f"{base_url}/issues?state=open", []))
        issues_closed = len(fetch_url(f"{base_url}/issues?state=closed", []))

        return {
            "stars": repo_data.get("stargazers_count", 0),
            "forks": repo_data.get("forks_count", 0),
            "issues": repo_data.get("open_issues_count", 0),
            "license": repo_data.get("license", {}).get("spdx_id", "No License"),
            "topics": topics_data.get("names", []),
            "pulls": {
                "open": pulls_open,
                "closed": pulls_closed
            },
            "issues": {
                "open": issues_open,
                "closed": issues_closed
            },
            "latest_commit": repo_data.get("updated_at", datetime.utcnow().isoformat())
        }

    def _get_default_metadata(self) -> Dict[str, Any]:
        """Return default metadata when GitHub API access fails."""
        return {
            "stars": 0,
            "forks": 0,
            "issues": 0,
            "license": "No License",
            "topics": [],
            "pulls": {
                "open": 0,
                "closed": 0
            },
            "issues": {
                "open": 0,
                "closed": 0
            },
            "latest_commit": datetime.utcnow().isoformat()
        }

    def compute_config_hash(self, config_data: Dict) -> Tuple[str, str]:
        """Compute content hash of configuration data."""
        # Serialize the configuration data to a canonical YAML string
        config_yaml = yaml.dump(config_data, sort_keys=True, default_flow_style=False)
        
        # Prepare the header
        object_type = 'config'
        content_size = len(config_yaml.encode('utf-8'))
        header = f"{object_type} {content_size}\0"
        
        # Combine header and content
        combined = header.encode('utf-8') + config_yaml.encode('utf-8')
        
        # Compute SHA-256 hash
        config_hash = hashlib.sha256(combined).hexdigest()
        
        return config_hash, config_yaml

    def store_config(self, config_hash: str, config_yaml: str) -> None:
        """Store configuration in content-addressable storage."""
        try:
            if not os.path.exists(self.storage_path):
                os.makedirs(self.storage_path)
                
            hash_path = os.path.join(self.storage_path, f"{config_hash[:2]}")
            if not os.path.exists(hash_path):
                os.makedirs(hash_path)
                
            config_path = os.path.join(hash_path, config_hash[2:])
            with open(config_path, 'w') as f:
                f.write(config_yaml)
        except Exception as e:
            print(f"Warning: Failed to store configuration: {e}")

    def generate_config(self) -> Dict:
        """Generate the complete configuration."""
        try:
            repo_owner, repo_name = self.github_repository.split('/')
            capabilities = self.detect_capabilities()
            github_metadata = self.fetch_github_metadata()
            
            config = {
                'name': self.github_repository,
                'address': f"https://github.com/{self.github_repository}",
                'capabilities': capabilities,
                'status': 'active',
                'metadata': {
                    'description': f"Auto-generated configuration for {self.github_repository}",
                    'owner': self.github_actor,
                    'last_updated': datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'),
                    'tags': github_metadata.get('topics', []),
                    'github': github_metadata,
                    'custom_properties': {
                        'deploy_environment': None,
                        'monitoring_enabled': None,
                        'auto_scale': None,
                        'service': None,
                        'app': repo_name,
                        'image': f"{self.github_repository}:{self.github_sha[:7]}",
                        'network': "project-domain-namespace",
                        'domain': f"{repo_name}.{repo_owner}.dev"
                    }
                }
            }
            
            return config
        except Exception as e:
            print(f"Error generating configuration: {e}")
            sys.exit(1)

    def main(self):
        """Main execution function."""
        try:
            # Generate configuration
            config = self.generate_config()
            
            # Compute final hash and YAML
            config_hash, config_yaml = self.compute_config_hash(config)
            
            # Store configuration
            self.store_config(config_hash, config_yaml)
            
            # Write configuration file
            with open(self.config_file, 'w') as f:
                f.write(config_yaml)
                
            # Write hash to file for GitHub Actions output
            with open('.nodeprop-hash', 'w') as f:
                f.write(config_hash)
                
        except Exception as e:
            print(f"Fatal error: {e}")
            sys.exit(1)

if __name__ == "__main__":
    generator = ConfigGenerator()
    generator.main()