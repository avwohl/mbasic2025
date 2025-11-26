#!/bin/bash
# Wrapper to filter output and prevent terminal corruption
"$@" 2>&1 | LC_ALL=C tr -cd '\11\12\15\40-\176'
echo  # ensure newline at end
