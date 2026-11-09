# DeepKeep hook launcher (Windows).
#
# Cursor executes hook commands through PowerShell on Windows, so this is the
# counterpart to the POSIX launcher. It locates a usable JavaScript runtime and hands off to
# the bundled CLI. See deepkeep-hook for the rationale; the resolution order is the
# same, and the failure path likewise avoids JavaScript so that a missing
# runtime still produces a well-formed decision.
#
# stdout carries the Cursor decision JSON and nothing else; diagnostics go to
# stderr so they cannot corrupt what Cursor parses.

param([Parameter(Position = 0)][string]$Event = '')

$ErrorActionPreference = 'Stop'
$MinMajor = 20

# Cursor may hand the payload over with a UTF-8 BOM; the CLI strips it, but keep
# our own output clean of one.
$OutputEncoding = New-Object System.Text.UTF8Encoding $false

if ($Event -eq 'hook' -and $args.Count -ge 1) { $Event = [string]$args[0] }

function Write-Deny([string]$Reason) {
    $m = "DeepKeep guardrails could not start: $Reason. Contact your administrator."
    # Hand-built JSON with an explicit escape: ConvertTo-Json differs across
    # PowerShell versions and the message is fully under our control.
    $e = $m.Replace('\', '\\').Replace('"', '\"')
    if ($Event -eq 'prompt') {
        [Console]::Out.Write('{"continue":false,"user_message":"' + $e + '"}' + "`n")
    } else {
        [Console]::Out.Write('{"permission":"deny","user_message":"' + $e + '","agent_message":"' + $e + '"}' + "`n")
    }
    exit 0
}

# A candidate is only usable if it executes and reports a supported major
# version. An unrelated or too-old node.exe must not be accepted on name alone.
function Test-Usable([string]$Path) {
    if ([string]::IsNullOrWhiteSpace($Path)) { return $false }
    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) { return $false }
    try {
        $v = & $Path --version 2>$null
    } catch { return $false }
    if ($LASTEXITCODE -ne 0 -or -not $v) { return $false }
    if ($v -notmatch '^v(\d+)\.') { return $false }
    return [int]$Matches[1] -ge $MinMajor
}

# Derive Cursor's application root from VSCODE_NLS_CONFIG, inherited from the
# parent process. Plain string handling, no external tooling.
function Get-CursorRootFromNls() {
    $nls = $env:VSCODE_NLS_CONFIG
    if ([string]::IsNullOrWhiteSpace($nls)) { return $null }
    if ($nls -notmatch '"defaultMessagesFile"\s*:\s*"([^"]+)"') { return $null }
    $f = $Matches[1] -replace '\\\\', '\'
    $i = $f.LastIndexOf('/out/')
    if ($i -lt 0) { $i = $f.LastIndexOf('\out\') }
    if ($i -lt 0) { return $null }
    return $f.Substring(0, $i)
}

function Resolve-Node() {
    # 1. Explicit administrator override always wins.
    if (Test-Usable $env:DEEPKEEP_NODE) { return $env:DEEPKEEP_NODE }

    # 2. A runtime the customer already has.
    $cmd = Get-Command node.exe -CommandType Application -ErrorAction SilentlyContinue |
           Select-Object -First 1
    if ($cmd -and (Test-Usable $cmd.Source)) { return $cmd.Source }

    # 3. Cursor's own bundled runtime, located from the inherited environment.
    $root = Get-CursorRootFromNls
    if ($root) {
        $c = Join-Path $root 'resources\helpers\node.exe'
        if (Test-Usable $c) { return $c }
    }

    # 4. Cursor's bundled runtime at the default install locations.
    $bases = @(
        (Join-Path $env:LOCALAPPDATA 'Programs\cursor\resources\app'),
        (Join-Path ${env:ProgramFiles} 'cursor\resources\app'),
        (Join-Path ${env:ProgramFiles} 'Cursor\resources\app')
    )
    foreach ($b in $bases) {
        if ([string]::IsNullOrWhiteSpace($b)) { continue }
        $c = Join-Path $b 'resources\helpers\node.exe'
        if (Test-Usable $c) { return $c }
    }

    return $null
}

if ([string]::IsNullOrWhiteSpace($Event)) { Write-Deny 'no hook event was supplied' }

# ${CURSOR_PLUGIN_ROOT} is expanded by Cursor for plugin hooks; fall back to the
# directory holding this script.
$root = $env:CURSOR_PLUGIN_ROOT
if ([string]::IsNullOrWhiteSpace($root)) { $root = Split-Path -Parent $PSScriptRoot }

$cli = Join-Path $root 'bin\cli.js'
if (-not (Test-Path -LiteralPath $cli -PathType Leaf)) { Write-Deny 'the plugin payload is missing' }

$node = Resolve-Node
if (-not $node) { Write-Deny 'no compatible JavaScript runtime was found' }

if ($env:DEEPKEEP_DEBUG) { [Console]::Error.WriteLine("[deepkeep] runtime: $node") }

# Forward stdin untouched and let the child own stdout.
& $node $cli hook $Event
exit $LASTEXITCODE
