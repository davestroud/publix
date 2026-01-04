#!/bin/bash
# Quick script to activate the virtual environment

source venv/bin/activate
echo "✓ Virtual environment activated"
echo "Python: $(python --version)"
echo "Pip: $(pip --version)"
echo ""
echo "To deactivate, run: deactivate"

