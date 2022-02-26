#!/usr/bin/env nix-shell
#!nix-shell -i sh -p python39 gcc python39Packages.jinja2 python39Packages.pillow libudev-zero

exec ./generator.py "$@"
