"""Unit tests for ConfigGenerator.

Run with:
    python -m unittest tests.test_generate_config
"""

import os
import tempfile
import unittest
from unittest.mock import patch

import yaml

from scripts.generate_config import ConfigGenerator


class ConfigGeneratorTest(unittest.TestCase):
    def setUp(self):
        self.env_patch = patch.dict(os.environ, {
            "GITHUB_REPOSITORY": "Cdaprod/example",
            "GITHUB_ACTOR": "tester",
            "GITHUB_SHA": "abcdef1234567890"
        })
        self.env_patch.start()
        self.addCleanup(self.env_patch.stop)

    def test_generate_config_populates_fields(self):
        cg = ConfigGenerator()
        mock_metadata = {
            "stars": 1,
            "forks": 2,
            "issues": 3,
            "license": "MIT",
            "latest_commit": "2025-01-01T00:00:00Z",
            "topics": ["t1"],
            "default_branch": "main"
        }
        with patch.object(cg, 'fetch_github_metadata', return_value=mock_metadata), \
             patch.object(cg, 'detect_capabilities', return_value=['pipeline']), \
             patch.object(cg, 'generate_network_identifiers', return_value={
                 'namespace': 'Cdaprod-network',
                 'domain': 'example.cdaprod.dev',
                 'service_dns': 'svc',
                 'cluster_dns': 'svc.cluster.local',
                 'service_name': 'example'
             }):
            config = cg.generate_config()

        self.assertEqual(config['metadata']['github']['stars'], 1)
        self.assertIn('pipeline', config['capabilities'])
        self.assertEqual(
            config['metadata']['custom_properties']['image'],
            'Cdaprod/example:abcdef1'
        )
        self.assertEqual(config['metadata']['github']['topics'], ['t1'])

    def test_spec_file_merge(self):
        spec = {'artifacts': {'backend': {'runtime': 'docker'}}}
        with tempfile.NamedTemporaryFile('w', delete=False) as tmp:
            yaml.safe_dump(spec, tmp)
            spec_path = tmp.name
        self.addCleanup(lambda: os.remove(spec_path))
        env = patch.dict(os.environ, {"SPEC_FILE_PATH": spec_path})
        env.start()
        self.addCleanup(env.stop)

        cg = ConfigGenerator()

        mock_metadata = {
            "stars": 0,
            "forks": 0,
            "issues": 0,
            "license": "MIT",
            "latest_commit": "2025-01-01T00:00:00Z",
            "topics": [],
            "default_branch": "main",
        }
        with patch.object(cg, 'fetch_github_metadata', return_value=mock_metadata), \
             patch.object(cg, 'detect_capabilities', return_value=[]), \
             patch.object(cg, 'generate_network_identifiers', return_value={'namespace': 'n', 'domain': 'd', 'service_dns': 's', 'cluster_dns': 'c', 'service_name': 'svc'}):
            config = cg.generate_config()
        self.assertEqual(config['artifacts']['backend']['runtime'], 'docker')


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
