# ⚡ Quick Setup (Windows)

**Copy this entire line into PowerShell and press Enter:**

```powershell
$d="$env:USERPROFILE\Desktop\ai-agent"; if(!(Test-Path "$d\index.html")){ git clone https://github.com/kiyanshsaini604-cmyk/ai-agent.git $d }; if(Get-Command python -ErrorAction SilentlyContinue){ Start-Process python -ArgumentList '-m','http.server','8123','--bind','127.0.0.1' -WorkingDirectory $d } elseif(Get-Command py -ErrorAction SilentlyContinue){ Start-Process py -ArgumentList '-m','http.server','8123','--bind','127.0.0.1' -WorkingDirectory $d } elseif(Get-Command npx -ErrorAction SilentlyContinue){ Start-Process npx -ArgumentList '-y','serve','-l','8123',$d } else { Write-Host 'No server found - install Python: winget install Python.Python.3.12' -ForegroundColor Yellow }; Start-Sleep 3; Start-Process 'http://127.0.0.1:8123/index.html'
```

That's it — it will:

1. 📥 Clone the repo to your Desktop (skipped if already there)
2. 🚀 Start a local server on port `8123` (uses Python, `py`, or Node `npx` — whichever you have)
3. 🌐 Open `http://127.0.0.1:8123/index.html` in your default browser

## After it opens

- Click **Allow** when the browser asks for microphone access
- Say **"Hey Phoenix"** or press **[SPACE]** (tap the mic button on phones)
- Speak your command — the window opens, he replies in a deep voice, then asks you a question

## Troubleshooting

| Problem | Fix |
|---|---|
| "No server found" | Install Python: `winget install Python.Python.3.12` then run the command again |
| Page won't open / port busy | Stop the old server first: `Get-Process python,py -ErrorAction SilentlyContinue \| Stop-Process` |
| Mic says `MIC NEEDED` | Open the page in **Chrome/Edge** and allow microphone for the site |
| Clone failed | Install git: `winget install Git.Git` |
