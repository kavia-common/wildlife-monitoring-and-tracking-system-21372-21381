#!/bin/bash
cd /home/kavia/workspace/code-generation/wildlife-monitoring-and-tracking-system-21372-21381/wildlife_tracking_backend
source venv/bin/activate
flake8 .
LINT_EXIT_CODE=$?
if [ $LINT_EXIT_CODE -ne 0 ]; then
  exit 1
fi

