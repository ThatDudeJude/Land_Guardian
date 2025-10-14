#!/usr/bin/env python3
"""Test runner script for LandGuardian."""
import pytest
import sys

if __name__ == '__main__':
    # Run tests and exit with proper code
    exit_code = pytest.main(['tests/', '-v', '--tb=short'])
    sys.exit(exit_code)