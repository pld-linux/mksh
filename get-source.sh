#!/bin/sh
set -e

CVSROOT=_anoncvs@anoncvs.mirbsd.org:/cvs
module=mksh
tag=mksh-R50d
branch=mksh-R50stable
out=branch.diff

d=$-
filter() {
	set -$d
	# remove revno's for smaller diffs
	sed -e 's,^\([-+]\{3\} .*\)\t(revision [0-9]\+)$,\1,'
}

echo >&2 "Running diff: $tag -> $branch"

cvs -qz8 -d "$CVSROOT" rdiff -u -r"$tag" -r"$branch" "$module" > $out.tmp

if cmp -s $out{,.tmp}; then
	echo >&2 "No new diffs..."
	rm -f $out.tmp
	exit 0
fi
mv -f $out{.tmp,}

./dropin $out
