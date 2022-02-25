#!/usr/bin/env nix-shell
#!nix-shell -i sh -p python3 lilypond strace

exec strace -f -e trace=file ./generator.py "$@"
