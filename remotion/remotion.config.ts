import { Config } from '@remotion/cli/config';
import fs from 'fs';

// Use the Chromium that ships with Playwright in cloud sessions (Remotion's own download host is unreachable there).
const pw = '/opt/pw-browsers/chromium_headless_shell-1243/chrome-headless-shell-linux64/chrome-headless-shell';
if (fs.existsSync(pw)) Config.setBrowserExecutable(pw);
