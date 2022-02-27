#!/usr/bin/env nix-shell
#!nix-shell -i sh -p python3 python3Packages.pillow

exec ./generator.py "$@"
