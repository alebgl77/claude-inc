$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$RepoRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot ".."))
$TestRoot = Join-Path ([IO.Path]::GetTempPath()) ("claude-inc-installer-tests-" + [Guid]::NewGuid().ToString("N"))
$Utf8NoBom = New-Object Text.UTF8Encoding($false)

function Fail([string]$Message) { throw "FAIL: $Message" }
function Write-Utf8([string]$Path, [string]$Content) { [IO.File]::WriteAllText($Path, $Content, $Utf8NoBom) }
function Get-TestFileFingerprint([string]$Path) {
    $sha = [Security.Cryptography.SHA256]::Create()
    try {
        $stream = [IO.File]::OpenRead($Path)
        try { return (($sha.ComputeHash($stream) | ForEach-Object { $_.ToString("x2") }) -join "") }
        finally { $stream.Dispose() }
    } finally { $sha.Dispose() }
}
function Assert-Text([string]$Path, [string]$Expected) {
    $actual = [IO.File]::ReadAllText($Path).TrimEnd("`r", "`n")
    if ($actual -cne $Expected) { Fail "unexpected content in ${Path}: $actual" }
}

function New-Fixture([string]$Path) {
    $null = New-Item -ItemType Directory -Force -Path (Join-Path $Path "skills/alpha"), (Join-Path $Path "skills/beta"), (Join-Path $Path "agents"), (Join-Path $Path "commands"), (Join-Path $Path "onboarding"), (Join-Path $Path "bin"), (Join-Path $Path ".claude-plugin")
    Copy-Item -LiteralPath (Join-Path $RepoRoot "install.ps1") -Destination (Join-Path $Path "install.ps1")
    Write-Utf8 (Join-Path $Path "skills/alpha/data.txt") "alpha-v1`n"
    Write-Utf8 (Join-Path $Path "skills/alpha/SKILL.md") "# Alpha`n"
    Write-Utf8 (Join-Path $Path "skills/beta/SKILL.md") "# Beta`n"
    Write-Utf8 (Join-Path $Path "agents/head.md") "agent-v1`n"
    Write-Utf8 (Join-Path $Path "commands/company.md") "command-v1`n"
    Write-Utf8 (Join-Path $Path "onboarding/ONBOARDING.md") "# Onboarding`n"
    Write-Utf8 (Join-Path $Path ".claude-plugin/plugin.json") '{"name":"fixture"}'
    Write-Utf8 (Join-Path $Path "bin/company") "#!/usr/bin/env bash`nif [ `"`${1:-}`" = version ]; then echo `"company v1.2.0`"; else echo company; fi`n"
}

function Invoke-Global([string]$Fixture, [string]$HomePath, [switch]$NoBin) {
    $oldHome = $env:HOME
    try {
        $env:HOME = $HomePath
        if ($NoBin) { & (Join-Path $Fixture "install.ps1") -NoBin | Out-Null }
        else { & (Join-Path $Fixture "install.ps1") | Out-Null }
    } finally {
        $env:HOME = $oldHome
    }
}

function Expect-Failure([scriptblock]$Action) {
    try {
        & $Action
        Fail "command unexpectedly succeeded"
    } catch {
        if ($_.Exception.Message -like "FAIL:*") { throw }
        if ($_.Exception.Message -notmatch 'collision|modified|reparse|special|unsafe|lock|hook|executable|changed|simulated|recovery|invalid|canonical|incomplete|appeared|cleanup') {
            Fail "failure was not actionable: $($_.Exception.Message)"
        }
    }
}

try {
    $null = New-Item -ItemType Directory -Path $TestRoot

    # Clean install, path with spaces, wrapper, manifest, and idempotence.
    $fixture = Join-Path $TestRoot "source with spaces"; $TestHome = Join-Path $TestRoot "home with spaces"
    New-Fixture $fixture; $null = New-Item -ItemType Directory -Path $TestHome
    Invoke-Global $fixture $TestHome
    Assert-Text (Join-Path $TestHome ".claude/skills/alpha/data.txt") "alpha-v1"
    Assert-Text (Join-Path $TestHome ".claude/agents/head.md") "agent-v1"
    Assert-Text (Join-Path $TestHome ".claude/commands/company.md") "command-v1"
    $wrapper = Join-Path $TestHome ".local/bin/company.cmd"
    if (-not (Test-Path -LiteralPath $wrapper -PathType Leaf)) { Fail "CLI wrapper missing" }
    $manifest = Join-Path $TestHome ".claude/.claude-inc-cli-manifest-v1"
    if (-not ([IO.File]::ReadAllText($manifest).Contains("cli`tcompany.cmd`tfile`t"))) { Fail "CLI type and fingerprint missing from global CLI manifest" }
    Invoke-Global $fixture $TestHome

    # Intact managed update.
    Write-Utf8 (Join-Path $fixture "skills/alpha/data.txt") "alpha-v2`n"
    Write-Utf8 (Join-Path $fixture "commands/company.md") "command-v2`n"
    Invoke-Global $fixture $TestHome
    Assert-Text (Join-Path $TestHome ".claude/skills/alpha/data.txt") "alpha-v2"
    Assert-Text (Join-Path $TestHome ".claude/commands/company.md") "command-v2"

    # Modified managed entry blocks all updates.
    Write-Utf8 (Join-Path $TestHome ".claude/agents/head.md") "user-agent`n"
    Write-Utf8 (Join-Path $fixture "skills/alpha/data.txt") "alpha-v3`n"
    Expect-Failure { Invoke-Global $fixture $TestHome }
    Assert-Text (Join-Path $TestHome ".claude/agents/head.md") "user-agent"
    Assert-Text (Join-Path $TestHome ".claude/skills/alpha/data.txt") "alpha-v2"

    # Extra file in a managed directory is a modification.
    $fixture = Join-Path $TestRoot "extra source"; $TestHome = Join-Path $TestRoot "extra home"
    New-Fixture $fixture; $null = New-Item -ItemType Directory -Path $TestHome
    Invoke-Global $fixture $TestHome -NoBin
    Assert-Text (Join-Path $TestHome ".claude/commands/company.md") "command-v1"
    Write-Utf8 (Join-Path $TestHome ".claude/skills/alpha/user.txt") "extra`n"
    Expect-Failure { Invoke-Global $fixture $TestHome -NoBin }
    if (-not (Test-Path -LiteralPath (Join-Path $TestHome ".claude/skills/alpha/user.txt"))) { Fail "extra file was removed" }

    # Divergent unmanaged skill collision remains untouched.
    $fixture = Join-Path $TestRoot "skill source"; $TestHome = Join-Path $TestRoot "skill home"
    New-Fixture $fixture; $null = New-Item -ItemType Directory -Force -Path (Join-Path $TestHome ".claude/skills/alpha")
    Write-Utf8 (Join-Path $TestHome ".claude/skills/alpha/data.txt") "user-skill`n"
    Expect-Failure { Invoke-Global $fixture $TestHome -NoBin }
    Assert-Text (Join-Path $TestHome ".claude/skills/alpha/data.txt") "user-skill"
    if (Test-Path -LiteralPath (Join-Path $TestHome ".claude/agents/head.md")) { Fail "partial agent install after skill collision" }

    # Divergent unmanaged agent collision remains untouched.
    $fixture = Join-Path $TestRoot "agent source"; $TestHome = Join-Path $TestRoot "agent home"
    New-Fixture $fixture; $null = New-Item -ItemType Directory -Force -Path (Join-Path $TestHome ".claude/agents")
    Write-Utf8 (Join-Path $TestHome ".claude/agents/head.md") "user-agent`n"
    Expect-Failure { Invoke-Global $fixture $TestHome -NoBin }
    Assert-Text (Join-Path $TestHome ".claude/agents/head.md") "user-agent"
    if (Test-Path -LiteralPath (Join-Path $TestHome ".claude/skills/alpha")) { Fail "partial skill install after agent collision" }

    # Late CLI collision prevents all earlier planned copies.
    $fixture = Join-Path $TestRoot "cli source"; $TestHome = Join-Path $TestRoot "cli home"
    New-Fixture $fixture; $null = New-Item -ItemType Directory -Force -Path (Join-Path $TestHome ".local/bin")
    Write-Utf8 (Join-Path $TestHome ".local/bin/company.cmd") "user-cli`n"
    Expect-Failure { Invoke-Global $fixture $TestHome }
    Assert-Text (Join-Path $TestHome ".local/bin/company.cmd") "user-cli"
    if (Test-Path -LiteralPath (Join-Path $TestHome ".claude")) { Fail "target mutated before late CLI collision" }

    # Exact pre-manifest layout is adopted.
    $fixture = Join-Path $TestRoot "adopt source"; $TestHome = Join-Path $TestRoot "adopt home"
    New-Fixture $fixture; $null = New-Item -ItemType Directory -Path $TestHome
    Invoke-Global $fixture $TestHome
    Remove-Item -LiteralPath (Join-Path $TestHome ".claude/.claude-inc-manifest-v1")
    Invoke-Global $fixture $TestHome
    if (-not (Test-Path -LiteralPath (Join-Path $TestHome ".claude/.claude-inc-manifest-v1"))) { Fail "legacy layout was not adopted" }

    # Reparse point inside a managed skill fails closed.
    $fixture = Join-Path $TestRoot "reparse source"; $TestHome = Join-Path $TestRoot "reparse home"
    New-Fixture $fixture
    $external = Join-Path $TestHome "external"; $skill = Join-Path $TestHome ".claude/skills/alpha"
    $null = New-Item -ItemType Directory -Force -Path $external, $skill
    Write-Utf8 (Join-Path $external "data.txt") "outside`n"
    $junction = Join-Path $skill "linked"
    $null = New-Item -ItemType Junction -Path $junction -Target $external
    Expect-Failure { Invoke-Global $fixture $TestHome -NoBin }
    if (-not ((Get-Item -LiteralPath $junction).Attributes -band [IO.FileAttributes]::ReparsePoint)) { Fail "reparse point was changed" }

    # Project scope and -NoBin do not write global CLI or root CLAUDE.md.
    $fixture = Join-Path $TestRoot "project source"; $TestHome = Join-Path $TestRoot "project home"; $project = Join-Path $TestRoot "project with spaces"
    New-Fixture $fixture; $null = New-Item -ItemType Directory -Force -Path $TestHome, $project
    $oldHome = $env:HOME
    $env:HOME = $TestHome
    Push-Location $project
    try { & (Join-Path $fixture "install.ps1") -Project -NoBin | Out-Null } finally { Pop-Location; $env:HOME = $oldHome }
    Assert-Text (Join-Path $project ".claude/skills/alpha/data.txt") "alpha-v1"
    Assert-Text (Join-Path $project ".claude/commands/company.md") "command-v1"
    if (Test-Path -LiteralPath (Join-Path $TestHome ".local/bin/company.cmd")) { Fail "-NoBin installed a CLI" }
    if (Test-Path -LiteralPath (Join-Path $project "CLAUDE.md")) { Fail "installer unexpectedly copied root CLAUDE.md" }

    $fixture = Join-Path $TestRoot "project cli source"; $TestHome = Join-Path $TestRoot "project cli home"; $project = Join-Path $TestRoot "project cli workspace"
    New-Fixture $fixture; $null = New-Item -ItemType Directory -Force -Path $TestHome, $project
    $cliStageMarker = Join-Path $TestRoot "project-cli-stage.txt"
    $hook = Join-Path $TestRoot "project-cli-stage-hook.ps1"
    Write-Utf8 $hook @'
param($Point, $Kind, $Name, $Destination, $Backup)
if ($Point -eq "after-cli-stage") {
    $stage = [IO.Path]::GetFullPath($Backup)
    $expectedBin = [IO.Path]::GetFullPath($env:CLAUDE_INC_TEST_EXPECTED_BIN).TrimEnd([IO.Path]::DirectorySeparatorChar)
    $forbiddenTarget = [IO.Path]::GetFullPath($env:CLAUDE_INC_TEST_FORBIDDEN_TARGET).TrimEnd([IO.Path]::DirectorySeparatorChar) + [IO.Path]::DirectorySeparatorChar
    if ([IO.Path]::GetFullPath((Split-Path -Parent $stage)).TrimEnd([IO.Path]::DirectorySeparatorChar) -cne $expectedBin) { throw "CLI stage is not under BinDir" }
    if ($stage.StartsWith($forbiddenTarget, [StringComparison]::OrdinalIgnoreCase)) { throw "CLI stage is under Target" }
    if (-not (Test-Path -LiteralPath $stage -PathType Leaf)) { throw "CLI stage does not exist" }
    [IO.File]::WriteAllText($env:CLAUDE_INC_TEST_STAGE_MARKER, $stage, [Text.UTF8Encoding]::new($false))
}
'@
    $oldHome = $env:HOME; $env:HOME = $TestHome
    $env:CLAUDE_INC_TEST_HOOK = $hook
    $env:CLAUDE_INC_TEST_EXPECTED_BIN = Join-Path $TestHome ".local/bin"
    $env:CLAUDE_INC_TEST_FORBIDDEN_TARGET = Join-Path $project ".claude"
    $env:CLAUDE_INC_TEST_STAGE_MARKER = $cliStageMarker
    Push-Location $project
    try { & (Join-Path $fixture "install.ps1") -Project | Out-Null } finally {
        Pop-Location; $env:HOME = $oldHome
        Remove-Item Env:CLAUDE_INC_TEST_HOOK, Env:CLAUDE_INC_TEST_EXPECTED_BIN, Env:CLAUDE_INC_TEST_FORBIDDEN_TARGET, Env:CLAUDE_INC_TEST_STAGE_MARKER -ErrorAction SilentlyContinue
    }
    if (-not (Test-Path -LiteralPath $cliStageMarker -PathType Leaf)) { Fail "CLI stage location was not observed" }
    $observedCliStage = [IO.File]::ReadAllText($cliStageMarker)
    if (Test-Path -LiteralPath $observedCliStage) { Fail "CLI stage temporary remained after success" }
    if (@(Get-ChildItem -LiteralPath (Join-Path $TestHome ".local/bin") -Force -Filter ".claude-inc-company-stage-*.tmp").Count) { Fail "CLI directory retained a stage temporary" }
    $projectManifest = [IO.File]::ReadAllText((Join-Path $project ".claude/.claude-inc-manifest-v1"))
    if ($projectManifest.Contains("cli`t")) { Fail "project manifest claimed the global CLI" }
    if (-not (Test-Path -LiteralPath (Join-Path $TestHome ".claude/.claude-inc-cli-manifest-v1"))) { Fail "project install did not create global CLI ownership" }

    # A command collision is checked after skills and agents but before any copy.
    $fixture = Join-Path $TestRoot "command source"; $TestHome = Join-Path $TestRoot "command home"
    New-Fixture $fixture; $null = New-Item -ItemType Directory -Force -Path (Join-Path $TestHome ".claude/commands")
    Write-Utf8 (Join-Path $TestHome ".claude/commands/company.md") "user-command`n"
    Expect-Failure { Invoke-Global $fixture $TestHome -NoBin }
    Assert-Text (Join-Path $TestHome ".claude/commands/company.md") "user-command"
    if (Test-Path -LiteralPath (Join-Path $TestHome ".claude/skills/alpha")) { Fail "partial install before command collision" }

    # Malicious manifest names are rejected before any managed destination changes.
    $fixture = Join-Path $TestRoot "malicious manifest source"; $TestHome = Join-Path $TestRoot "malicious manifest home"; New-Fixture $fixture; $null = New-Item -ItemType Directory -Force -Path $TestHome
    Invoke-Global $fixture $TestHome -NoBin
    $manifestPath = Join-Path $TestHome ".claude/.claude-inc-manifest-v1"
    Write-Utf8 $manifestPath "claude-inc-manifest-v1`nskill`t.`tdir`t$('0' * 64)`ncommand`t../company.md`tfile`t$('0' * 64)`n"
    Expect-Failure { Invoke-Global $fixture $TestHome -NoBin }
    Assert-Text (Join-Path $TestHome ".claude/skills/alpha/data.txt") "alpha-v1"
    Assert-Text $manifestPath ("claude-inc-manifest-v1`nskill`t.`tdir`t" + ('0' * 64) + "`ncommand`t../company.md`tfile`t" + ('0' * 64))

    # An incomplete local runtime payload fails before target mutation.
    $fixture = Join-Path $TestRoot "incomplete source"; $TestHome = Join-Path $TestRoot "incomplete home"; New-Fixture $fixture; Remove-Item -LiteralPath (Join-Path $fixture "onboarding/ONBOARDING.md"); $null = New-Item -ItemType Directory -Force -Path $TestHome
    Expect-Failure { Invoke-Global $fixture $TestHome -NoBin }
    if (Test-Path -LiteralPath (Join-Path $TestHome ".claude")) { Fail "incomplete source mutated target" }

    # An already-held lock blocks before target mutation.
    $fixture = Join-Path $TestRoot "lock source"; $TestHome = Join-Path $TestRoot "lock home"; New-Fixture $fixture
    $lock = Join-Path $TestHome ".claude.claude-inc-install.lock"; $null = New-Item -ItemType Directory -Force -Path $lock
    Expect-Failure { Invoke-Global $fixture $TestHome -NoBin }
    if (Test-Path -LiteralPath (Join-Path $TestHome ".claude")) { Fail "lock refusal mutated the target" }
    Remove-Item -LiteralPath $lock -Recurse -Force

    # A TOCTOU mutation after preflight is detected immediately before apply.
    $fixture = Join-Path $TestRoot "toctou source"; $TestHome = Join-Path $TestRoot "toctou home"; New-Fixture $fixture; $null = New-Item -ItemType Directory -Force -Path $TestHome
    $hook = Join-Path $TestRoot "toctou-hook.ps1"
    Write-Utf8 $hook @'
param($Point, $Kind, $Name, $Destination, $Backup)
if ($Point -eq "before-entry" -and $Kind -eq "skill") {
    New-Item -ItemType Directory -Force -Path $Destination | Out-Null
    [IO.File]::WriteAllText((Join-Path $Destination "user.txt"), "race", [Text.UTF8Encoding]::new($false))
}
'@
    $env:CLAUDE_INC_TEST_HOOK = $hook
    try { Expect-Failure { Invoke-Global $fixture $TestHome -NoBin } } finally { Remove-Item Env:CLAUDE_INC_TEST_HOOK -ErrorAction SilentlyContinue }
    Assert-Text (Join-Path $TestHome ".claude/skills/alpha/user.txt") "race"

    # Desired state is built from the manifest snapshot and any later manifest mutation aborts.
    $fixture = Join-Path $TestRoot "manifest race source"; $TestHome = Join-Path $TestRoot "manifest race home"; New-Fixture $fixture; $null = New-Item -ItemType Directory -Force -Path $TestHome
    Invoke-Global $fixture $TestHome -NoBin; Write-Utf8 (Join-Path $fixture "skills/alpha/data.txt") "alpha-v2`n"
    $hook = Join-Path $TestRoot "manifest-race-hook.ps1"
    Write-Utf8 $hook @'
param($Point, $Kind, $Name, $Destination, $Backup)
if ($Point -eq "after-stage") { [IO.File]::WriteAllText((Join-Path $Destination ".claude-inc-manifest-v1"), "externally changed`n", [Text.UTF8Encoding]::new($false)) }
'@
    $env:CLAUDE_INC_TEST_HOOK = $hook
    try { Expect-Failure { Invoke-Global $fixture $TestHome -NoBin } } finally { Remove-Item Env:CLAUDE_INC_TEST_HOOK -ErrorAction SilentlyContinue }
    Assert-Text (Join-Path $TestHome ".claude/skills/alpha/data.txt") "alpha-v1"
    Assert-Text (Join-Path $TestHome ".claude/.claude-inc-manifest-v1") "externally changed"

    # A destination created after backup is never replaced or used as a Move-Item container.
    $fixture = Join-Path $TestRoot "post-backup race source"; $TestHome = Join-Path $TestRoot "post-backup race home"; New-Fixture $fixture; $null = New-Item -ItemType Directory -Force -Path $TestHome
    Invoke-Global $fixture $TestHome -NoBin; Write-Utf8 (Join-Path $fixture "skills/alpha/data.txt") "alpha-v2`n"
    $hook = Join-Path $TestRoot "post-backup-race-hook.ps1"
    Write-Utf8 $hook @'
param($Point, $Kind, $Name, $Destination, $Backup)
if ($Point -eq "after-backup" -and $Kind -eq "skill" -and $Name -eq "alpha") {
    New-Item -ItemType Directory -Path $Destination | Out-Null
    [IO.File]::WriteAllText((Join-Path $Destination "external.txt"), "external", [Text.UTF8Encoding]::new($false))
}
'@
    $env:CLAUDE_INC_TEST_HOOK = $hook
    try { Expect-Failure { Invoke-Global $fixture $TestHome -NoBin } } finally { Remove-Item Env:CLAUDE_INC_TEST_HOOK -ErrorAction SilentlyContinue }
    Assert-Text (Join-Path $TestHome ".claude/skills/alpha/external.txt") "external"
    $raceRecovery = @(Get-ChildItem -LiteralPath (Join-Path $TestHome ".claude") -Directory -Filter ".claude-inc-rollback-*")
    if ($raceRecovery.Count -ne 1) { Fail "post-backup race did not retain recovery data" }
    Assert-Text (Join-Path $raceRecovery[0].FullName "skill/alpha/data.txt") "alpha-v1"

    # Failure after backup restores every destination and removes temporary manifests.
    $fixture = Join-Path $TestRoot "apply failure source"; $TestHome = Join-Path $TestRoot "apply failure home"; New-Fixture $fixture; $null = New-Item -ItemType Directory -Force -Path $TestHome
    Invoke-Global $fixture $TestHome -NoBin; Write-Utf8 (Join-Path $fixture "skills/alpha/data.txt") "alpha-v2`n"
    $hook = Join-Path $TestRoot "apply-failure-hook.ps1"
    Write-Utf8 $hook @'
param($Point, $Kind, $Name, $Destination, $Backup)
if ($Point -eq "after-backup" -and $Kind -eq "skill" -and $Name -eq "alpha") { throw "simulated apply failure" }
'@
    $env:CLAUDE_INC_TEST_HOOK = $hook
    try { Expect-Failure { Invoke-Global $fixture $TestHome -NoBin } } finally { Remove-Item Env:CLAUDE_INC_TEST_HOOK -ErrorAction SilentlyContinue }
    Assert-Text (Join-Path $TestHome ".claude/skills/alpha/data.txt") "alpha-v1"
    if (@(Get-ChildItem -LiteralPath (Join-Path $TestHome ".claude") -Force | Where-Object { $_.Name -like '*.tmp.*' -or $_.Name -like '.claude-inc-rollback-*' }).Count) { Fail "successful rollback left temporary data" }

    # A restoration failure preserves its verified backup, journal, and lock.
    $fixture = Join-Path $TestRoot "restore failure source"; $TestHome = Join-Path $TestRoot "restore failure home"; New-Fixture $fixture; $null = New-Item -ItemType Directory -Force -Path $TestHome
    Invoke-Global $fixture $TestHome -NoBin; Write-Utf8 (Join-Path $fixture "skills/alpha/data.txt") "alpha-v2`n"
    $hook = Join-Path $TestRoot "restore-failure-hook.ps1"
    Write-Utf8 $hook @'
param($Point, $Kind, $Name, $Destination, $Backup)
if ($Kind -eq "skill" -and $Name -eq "alpha" -and ($Point -eq "after-backup" -or $Point -eq "before-restore")) { throw "simulated restoration failure" }
'@
    $env:CLAUDE_INC_TEST_HOOK = $hook
    try { Expect-Failure { Invoke-Global $fixture $TestHome -NoBin } } finally { Remove-Item Env:CLAUDE_INC_TEST_HOOK -ErrorAction SilentlyContinue }
    $recovery = @(Get-ChildItem -LiteralPath (Join-Path $TestHome ".claude") -Directory -Filter ".claude-inc-rollback-*")
    if ($recovery.Count -ne 1 -or -not (Test-Path -LiteralPath (Join-Path $recovery[0].FullName "skill/alpha/data.txt"))) { Fail "failed restoration did not preserve its backup" }
    if (-not (Test-Path -LiteralPath (Join-Path $recovery[0].FullName "journal.jsonl"))) { Fail "failed restoration did not preserve its journal" }
    if (-not (Test-Path -LiteralPath (Join-Path $TestHome ".claude.claude-inc-install.lock"))) { Fail "failed restoration did not retain its lock" }
    Remove-Item -LiteralPath $recovery[0].FullName, (Join-Path $TestHome ".claude.claude-inc-install.lock") -Recurse -Force
    if (Test-Path -LiteralPath (Join-Path $TestHome ".claude/skills/alpha")) { Remove-Item -LiteralPath (Join-Path $TestHome ".claude/skills/alpha") -Recurse -Force }

    # Upstream removal prunes an intact entry and blocks a modified entry.
    $fixture = Join-Path $TestRoot "remove source"; $TestHome = Join-Path $TestRoot "remove home"; New-Fixture $fixture; $null = New-Item -ItemType Directory -Force -Path $TestHome
    Invoke-Global $fixture $TestHome -NoBin; Remove-Item -LiteralPath (Join-Path $fixture "skills/alpha") -Recurse -Force; Invoke-Global $fixture $TestHome -NoBin
    if (Test-Path -LiteralPath (Join-Path $TestHome ".claude/skills/alpha")) { Fail "intact upstream removal was not pruned" }
    $fixture = Join-Path $TestRoot "remove modified source"; $TestHome = Join-Path $TestRoot "remove modified home"; New-Fixture $fixture; $null = New-Item -ItemType Directory -Force -Path $TestHome
    Invoke-Global $fixture $TestHome -NoBin; Write-Utf8 (Join-Path $TestHome ".claude/skills/alpha/data.txt") "user-skill`n"; Remove-Item -LiteralPath (Join-Path $fixture "skills/alpha") -Recurse -Force
    Expect-Failure { Invoke-Global $fixture $TestHome -NoBin }; Assert-Text (Join-Path $TestHome ".claude/skills/alpha/data.txt") "user-skill"

    # A cleanup error does not prevent lock release after a committed installation.
    $fixture = Join-Path $TestRoot "cleanup source"; $TestHome = Join-Path $TestRoot "cleanup home"; New-Fixture $fixture; $null = New-Item -ItemType Directory -Force -Path $TestHome
    $hook = Join-Path $TestRoot "cleanup-hook.ps1"
    Write-Utf8 $hook @'
param($Point, $Kind, $Name, $Destination, $Backup)
if ($Point -eq "before-cleanup-stage") { throw "simulated cleanup failure" }
'@
    $env:CLAUDE_INC_TEST_HOOK = $hook
    try { Expect-Failure { Invoke-Global $fixture $TestHome -NoBin } } finally { Remove-Item Env:CLAUDE_INC_TEST_HOOK -ErrorAction SilentlyContinue }
    Assert-Text (Join-Path $TestHome ".claude/skills/alpha/data.txt") "alpha-v1"
    if (Test-Path -LiteralPath (Join-Path $TestHome ".claude.claude-inc-install.lock")) { Fail "cleanup error left target lock after commit" }
    Get-ChildItem -LiteralPath (Join-Path $TestHome ".claude") -Directory -Filter ".claude-inc-stage-*" | Remove-Item -Recurse -Force

    # Percent signs are escaped in the Windows wrapper and cannot expand as variables.
    $fixture = Join-Path $TestRoot "percent %NAME% source"; $TestHome = Join-Path $TestRoot "percent home"; New-Fixture $fixture; $null = New-Item -ItemType Directory -Force -Path $TestHome
    $oldName = $env:NAME; $env:NAME = "EXPANDED"
    try { Invoke-Global $fixture $TestHome; $version = & (Join-Path $TestHome ".local/bin/company.cmd") version } finally { $env:NAME = $oldName }
    if ($LASTEXITCODE -ne 0 -or $version -ne "company v1.2.0") { Fail "percent-safe wrapper did not launch the intended source" }

    # A blocked remote upgrade never pulls or mutates the active legacy cache or wrapper.
    $origin = Join-Path $TestRoot "remote origin"; $activeCache = Join-Path $TestRoot "active cache"; $TestHome = Join-Path $TestRoot "remote home"
    New-Fixture $origin
    & git -C $origin init | Out-Null; & git -C $origin config user.email "tests@example.com"; & git -C $origin config user.name "Installer Tests"; & git -C $origin config commit.gpgsign false
    & git -C $origin add -f .; & git -C $origin commit -m "v1" | Out-Null
    $remoteScript = [scriptblock]::Create([IO.File]::ReadAllText((Join-Path $RepoRoot "install.ps1")))

    # The dedicated cache lock serializes remote no-bin installs on distinct targets.
    $lockedCache = Join-Path $TestRoot "locked cache"; $lockedHome = Join-Path $TestRoot "locked cache home"
    $null = New-Item -ItemType Directory -Force -Path $lockedHome, "$lockedCache.claude-inc-cache.lock"
    $oldHome = $env:HOME; $oldRepo = $env:CLAUDE_INC_REPO_URL; $oldCache = $env:CLAUDE_INC_HOME
    $env:HOME = $lockedHome; $env:CLAUDE_INC_REPO_URL = $origin; $env:CLAUDE_INC_HOME = $lockedCache
    try { Expect-Failure { & $remoteScript -NoBin } } finally { $env:HOME = $oldHome; $env:CLAUDE_INC_REPO_URL = $oldRepo; $env:CLAUDE_INC_HOME = $oldCache }
    if (Test-Path -LiteralPath (Join-Path $lockedHome ".claude")) { Fail "cache lock contention mutated target" }
    if (@(Get-ChildItem -LiteralPath $TestRoot -Directory -Filter "locked cache.candidate.*").Count) { Fail "cache lock contention cloned a candidate" }
    Remove-Item -LiteralPath "$lockedCache.claude-inc-cache.lock" -Recurse -Force

    # An incomplete remote candidate leaves an existing cache and target untouched.
    $missingOrigin = Join-Path $TestRoot "missing runtime origin"; $existingCache = Join-Path $TestRoot "existing cache"; $missingHome = Join-Path $TestRoot "missing runtime home"
    New-Fixture $missingOrigin; Remove-Item -LiteralPath (Join-Path $missingOrigin "onboarding/ONBOARDING.md")
    & git -C $missingOrigin init | Out-Null; & git -C $missingOrigin config user.email "tests@example.com"; & git -C $missingOrigin config user.name "Installer Tests"; & git -C $missingOrigin config commit.gpgsign false
    & git -C $missingOrigin add -f .; & git -C $missingOrigin commit -m "incomplete" | Out-Null
    & git clone $origin $existingCache | Out-Null; $existingBefore = Get-TestFileFingerprint (Join-Path $existingCache "skills/alpha/data.txt"); $null = New-Item -ItemType Directory -Force -Path $missingHome
    $oldHome = $env:HOME; $oldRepo = $env:CLAUDE_INC_REPO_URL; $oldCache = $env:CLAUDE_INC_HOME
    $env:HOME = $missingHome; $env:CLAUDE_INC_REPO_URL = $missingOrigin; $env:CLAUDE_INC_HOME = $existingCache
    try { Expect-Failure { & $remoteScript -NoBin } } finally { $env:HOME = $oldHome; $env:CLAUDE_INC_REPO_URL = $oldRepo; $env:CLAUDE_INC_HOME = $oldCache }
    if ((Get-TestFileFingerprint (Join-Path $existingCache "skills/alpha/data.txt")) -cne $existingBefore) { Fail "incomplete candidate changed existing cache" }
    if (Test-Path -LiteralPath (Join-Path $missingHome ".claude")) { Fail "incomplete candidate mutated target" }
    if (@(Get-ChildItem -LiteralPath $TestRoot -Directory -Filter "existing cache.candidate.*").Count) { Fail "incomplete candidate was not removed" }

    & git clone $origin $activeCache | Out-Null
    $null = New-Item -ItemType Directory -Force -Path $TestHome
    Invoke-Global $activeCache $TestHome
    $activeBefore = Get-TestFileFingerprint (Join-Path $activeCache "skills/alpha/data.txt")
    $wrapperBefore = [IO.File]::ReadAllText((Join-Path $TestHome ".local/bin/company.cmd"))
    Write-Utf8 (Join-Path $origin "skills/alpha/data.txt") "alpha-v2`n"; & git -C $origin add -f .; & git -C $origin commit -m "v2" | Out-Null
    Write-Utf8 (Join-Path $TestHome ".claude/commands/company.md") "user-command`n"
    $oldHome = $env:HOME; $oldRepo = $env:CLAUDE_INC_REPO_URL; $oldCache = $env:CLAUDE_INC_HOME
    $env:HOME = $TestHome; $env:CLAUDE_INC_REPO_URL = $origin; $env:CLAUDE_INC_HOME = $activeCache
    try { Expect-Failure { & $remoteScript } } finally { $env:HOME = $oldHome; $env:CLAUDE_INC_REPO_URL = $oldRepo; $env:CLAUDE_INC_HOME = $oldCache }
    if ((Get-TestFileFingerprint (Join-Path $activeCache "skills/alpha/data.txt")) -cne $activeBefore) { Fail "blocked remote upgrade changed active cache" }
    if ([IO.File]::ReadAllText((Join-Path $TestHome ".local/bin/company.cmd")) -cne $wrapperBefore) { Fail "blocked remote upgrade changed CLI wrapper" }
    Assert-Text (Join-Path $TestHome ".claude/skills/alpha/data.txt") "alpha-v1"
    Assert-Text (Join-Path $TestHome ".claude/commands/company.md") "user-command"
    if (Test-Path -LiteralPath "$activeCache.checkouts") { Fail "blocked remote upgrade promoted an immutable checkout" }
    if (@(Get-ChildItem -LiteralPath (Split-Path -Parent $activeCache) -Directory -Filter "$(Split-Path -Leaf $activeCache).candidate.*").Count) { Fail "blocked remote upgrade left a candidate checkout" }

    Write-Output "PowerShell installer safety tests passed"
} finally {
    if (Test-Path -LiteralPath $TestRoot) { Remove-Item -LiteralPath $TestRoot -Recurse -Force }
}
