#!/usr/bin/env nix-shell
#!nix-shell -i sh -p python3 lilypond

exec ./generator.py "$@"
