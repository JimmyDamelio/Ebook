#!/bin/sh
# New session: install the shared toolkit (skills, agents, voices, Agent Reach), then this project's Remotion deps.
set -e
cd "$(dirname "$0")"
[ -d /tmp/edunos-toolkit ] || git clone -q --depth 1 https://github.com/JimmyDamelio/edunos-claude-toolkit /tmp/edunos-toolkit
sh /tmp/edunos-toolkit/install.sh
(cd remotion && npm install --silent)
echo "Ebook media setup ready"
