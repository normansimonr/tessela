#!/bin/bash
source .venv/bin/activate
export PYTHONPATH=$PYTHONPATH:$PWD
python3 scripts/run_normalization.py
