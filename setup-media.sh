#!/bin/sh
# New session: install the shared toolkit (skills, agents, voices, Agent Reach), then this project's Remotion deps.
# The toolkit repo is private: in a cloud session, attach it first (add_repo JimmyDamelio/edunos-claude-toolkit),
# which clones it to /home/user/edunos-claude-toolkit.
set -e
cd "$(dirname "$0")"
T=/home/user/edunos-claude-toolkit
[ -d "$T/skills" ] || T=/tmp/edunos-toolkit
[ -d "$T/skills" ] || git clone -q --depth 1 https://github.com/JimmyDamelio/edunos-claude-toolkit "$T"
sh "$T/install.sh"
(cd remotion && npm install --silent)
echo "Ebook media setup ready"
