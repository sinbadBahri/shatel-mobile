#!/bin/bash

echo "Apply Tests"
pytest

exec "$@"