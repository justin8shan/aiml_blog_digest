"""
Utility functions for loading configuration files.
"""
import yaml
from pathlib import Path
from typing import Dict


def load_config(config_path: str) -> Dict:
    """
    Load YAML configuration file.
    
    Args:
        config_path: Path to YAML config file
        
    Returns:
        Dictionary with configuration
    """
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)


def get_config_path(filename: str) -> Path:
    """
    Get full path to config file.
    
    Args:
        filename: Name of config file
        
    Returns:
        Path object
    """
    # Get project root directory (parent of src)
    project_root = Path(__file__).parent.parent
    return project_root / 'config' / filename
