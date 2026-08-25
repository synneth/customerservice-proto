<#
  start-demo.ps1

  Starter hele "Mote & Mer" kundeservice-demoen med én kommando:
  1. Starter backend (uvicorn) i et eget vindu
  2. Kaller POST /api/setup-agent og lagrer agent_id i .env

  Kjør fra prosjektroten (kundeservice-proto):
    .\start-demo.ps1

  Forutsetter: python/uvicorn er installert (pip install -r requirements.txt),
  og at .env allerede finnes med ELEVENLABS_API_KEY utfylt (kopier
  .env.example til .env forst om du ikke har gjort det).

  NB: Ingen ngrok/tunnel trengs lenger. Alle verktoy i agent_config.py er
  "client"-tools som kjores av nettleseren over WebSocket-forbindelsen til
  ElevenLabs, sa backend trenger aldri vaere naabar fra internett - kun
  fra din egen maskin (localhost).
#>

$ErrorActionPreference = "Stop"
$root        = $PSScriptRoot
$envPath     = Join-Path $root ".env"
$backendPath = Join-Path $root "backend"

if (-not (Test-Path $envPath)) {
    Write-Host "Fant ingen .env i $root." -ForegroundColor Red
    Write-Host "Kjor forst:  Copy-Item .env.example .env  -  og fyll inn ELEVENLABS_API_KEY." -ForegroundColor Red
    exit 1
}

function Set-EnvValue {
    param([string]$Key, [string]$Value)
    $lines = Get-Content $envPath
    $pattern = "^$Key="
    $found = $false
    $newLines = foreach ($line in $lines) {
        if ($line -match $pattern) {
            $found = $true
            "$Key=$Value"
        } else {
            $line
        }
    }
    if (-not $found) {
        $newLines += "$Key=$Value"
    }
    Set-Content -Path $envPath -Value $newLines
}

# --- 1. Start backend i eget vindu ------------------------------------------
Write-Host "Starter backend (uvicorn) i eget vindu..." -ForegroundColor Cyan
$uvicornCmd = Get-Command uvicorn -ErrorAction SilentlyContinue
if (-not $uvicornCmd) {
    Write-Host "Fant ikke 'uvicorn' i PATH. Har du kjort:  pip install -r requirements.txt ?" -ForegroundColor Red
    exit 1
}
Start-Process -FilePath "powershell" -ArgumentList @(
    "-NoExit", "-Command",
    "cd '$backendPath'; uvicorn main:app --reload"
)

Write-Host "Venter paa at backend skal svare paa http://localhost:8000 ..."
$ready = $false
for ($i = 0; $i -lt 30; $i++) {
    Start-Sleep -Seconds 1
    try {
        Invoke-WebRequest -Uri "http://localhost:8000/docs" -UseBasicParsing -ErrorAction Stop | Out-Null
        $ready = $true
        break
    } catch { }
}
if (-not $ready) {
    Write-Host "Backend svarte ikke innen 30 sekunder. Sjekk uvicorn-vinduet for feilmeldinger." -ForegroundColor Red
    exit 1
}
Write-Host "Backend er oppe." -ForegroundColor Green

# --- 2. Registrer/oppdater ElevenLabs-agenten -------------------------------
Write-Host "Registrerer/oppdaterer ElevenLabs-agenten..." -ForegroundColor Cyan
$result = Invoke-RestMethod -Method POST -Uri "http://localhost:8000/api/setup-agent"
Write-Host $result.melding -ForegroundColor Green
Set-EnvValue -Key "ELEVENLABS_AGENT_ID" -Value $result.agent_id

Write-Host ""
Write-Host "=================================================================" -ForegroundColor Yellow
Write-Host " Nesten ferdig - én ting gjenstaar:" -ForegroundColor Yellow
Write-Host " Gaa til backend-vinduet som aapnet seg, trykk Ctrl+C," -ForegroundColor Yellow
Write-Host " og kjor 'uvicorn main:app --reload' der en gang til." -ForegroundColor Yellow
Write-Host " (Backend leser AGENT_ID fra .env kun ved oppstart, ikke automatisk.)" -ForegroundColor Yellow
Write-Host "=================================================================" -ForegroundColor Yellow
Write-Host ""
Write-Host "Aapne deretter http://localhost:8000 i nettleseren og trykk 'Ring kundeservice'." -ForegroundColor Green
