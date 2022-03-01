#!/usr/bin/env nix-shell
#!nix-shell -i bash -p python3 steam-run-native socat

rm -f $TMPDIR/shout.sock
export BWRAP_PROPAGATE_MOUNTS="/bin /usr/bin /nix/store"
exec socat -T30 unix-l:$TMPDIR/shout.sock,fork exec:"$(pwd)/app/run_worker.sh $1"
