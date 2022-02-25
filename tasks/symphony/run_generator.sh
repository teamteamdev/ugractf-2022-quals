#!/usr/bin/env nix-shell
#!nix-shell -i sh -p python3 lilypond

exec strace -f -e trace=file ./generator.py "$@"
