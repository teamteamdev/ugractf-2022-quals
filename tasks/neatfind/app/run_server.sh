#!/usr/bin/env nix-shell
#!nix-shell -i sh -p python3 python39Packages.aiohttp

exec app/server.py "$@"
