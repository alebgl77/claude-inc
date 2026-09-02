[CmdletBinding()]
param(
    [switch]$Project,
    [switch]$NoBin,
    [switch]$Onboard
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
$ManifestVersion = "claude-inc-manifest-v1"
$ManifestName = ".claude-inc-manifest-v1"
$CliManifestName = ".claude-inc-cli-manifest-v1"
$Utf8NoBom = New-Object Text.UTF8Encoding($false)

$RepoUrl = if ([string]::IsNullOrWhiteSpace($env:CLAUDE_INC_REPO_URL)) { "https://github.com/alebgl77/claude-inc" } else { $env:CLAUDE_INC_REPO_URL }
$UserHome = if (-not [string]::IsNullOrWhiteSpace($env:HOME)) { [IO.Path]::GetFullPath($env:HOME) }
    elseif ($HOME) { [IO.Path]::GetFullPath($HOME) } else { throw "Unable to determine the user home directory." }
$CloneDir = if ([string]::IsNullOrWhiteSpace($env:CLAUDE_INC_HOME)) { Join-Path $UserHome ".claude-inc" }
    else { [IO.Path]::GetFullPath($env:CLAUDE_INC_HOME) }

function Write-Status([string]$Message) { Write-Host "claude-inc $Message" }
function Get-Application([string]$Name) { Get-Command -Name $Name -CommandType Application -ErrorAction SilentlyContinue | Select-Object -First 1 }
function Invoke-Git([string[]]$Arguments) {
    $git = Get-Application "git"
    if (-not $git) { throw "Git is required when install.ps1 is not running from a local checkout." }
    & $git.Source @Arguments
    if ($LASTEXITCODE -ne 0) { throw "Git failed with exit code $LASTEXITCODE." }
}
function Assert-SafeField([string]$Value, [string]$Label) {
    if ($Value.IndexOf("`t") -ge 0 -or $Value.IndexOf("`r") -ge 0 -or $Value.IndexOf("`n") -ge 0) { throw "Unsupported tab or newline in ${Label}: $Value" }
}
function Get-BytesSha256([byte[]]$Bytes) {
    $sha = [Security.Cryptography.SHA256]::Create()
    try { $hash = $sha.ComputeHash($Bytes) } finally { $sha.Dispose() }
    ([BitConverter]::ToString($hash)).Replace("-", "").ToLowerInvariant()
}
function Get-FileFingerprint([string]$Path) {
    $item = Get-Item -LiteralPath $Path -Force -ErrorAction Stop
    if (($item.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0 -or $item.PSIsContainer) { throw "Expected a regular file without reparse points: $Path" }
    $stream = [IO.File]::Open($item.FullName, [IO.FileMode]::Open, [IO.FileAccess]::Read, [IO.FileShare]::Read)
    try {
        $sha = [Security.Cryptography.SHA256]::Create()
        try { $hash = $sha.ComputeHash($stream) } finally { $sha.Dispose() }
    } finally { $stream.Dispose() }
    ([BitConverter]::ToString($hash)).Replace("-", "").ToLowerInvariant()
}
function Get-DirectoryFingerprint([string]$Path) {
    $root = Get-Item -LiteralPath $Path -Force -ErrorAction Stop
    if (-not $root.PSIsContainer -or ($root.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) { throw "Expected a directory without reparse points: $Path" }
    $rootPath = $root.FullName.TrimEnd([IO.Path]::DirectorySeparatorChar, [IO.Path]::AltDirectorySeparatorChar)
    $pending = New-Object 'Collections.Generic.Stack[IO.DirectoryInfo]'; $pending.Push([IO.DirectoryInfo]$root)
    $lines = New-Object 'Collections.Generic.List[string]'
    while ($pending.Count -gt 0) {
        $directory = $pending.Pop()
        foreach ($item in @(Get-ChildItem -LiteralPath $directory.FullName -Force)) {
            if (($item.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) { throw "Reparse points are not allowed inside managed directories: $($item.FullName)" }
            $relative = $item.FullName.Substring($rootPath.Length).TrimStart([IO.Path]::DirectorySeparatorChar, [IO.Path]::AltDirectorySeparatorChar).Replace("\", "/")
            Assert-SafeField $relative "managed path"
            if ($item.PSIsContainer) { $lines.Add("D`t$relative"); $pending.Push([IO.DirectoryInfo]$item) }
            elseif ($item -is [IO.FileInfo]) { $lines.Add("F`t$relative`t$(Get-FileFingerprint $item.FullName)") }
            else { throw "Special files are not allowed inside managed directories: $($item.FullName)" }
        }
    }
    $ordered = $lines.ToArray(); [Array]::Sort($ordered, [StringComparer]::Ordinal)
    $canonical = if ($ordered.Count -eq 0) { "" } else { ($ordered -join "`n") + "`n" }
    Get-BytesSha256 $Utf8NoBom.GetBytes($canonical)
}
function Assert-SafeContainer([string]$Path, [string]$Label) {
    $item = Get-Item -LiteralPath $Path -Force -ErrorAction SilentlyContinue
    if ($item -and (-not $item.PSIsContainer -or ($item.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0)) { throw "$Label must be a directory without reparse points: $Path" }
}
function Assert-CanonicalManagedName([string]$Kind, [string]$Name) {
    Assert-SafeField $Name "managed name"
    $slugPattern = '^[a-z0-9]+(?:-[a-z0-9]+)*$'
    $valid = switch ($Kind) {
        "skill" { $Name -cmatch $slugPattern }
        "agent" { $Name -cmatch '^[a-z0-9]+(?:-[a-z0-9]+)*\.md$' }
        "command" { $Name -ceq "company.md" }
        "cli" { $Name -ceq "company.cmd" }
        default { $false }
    }
    if (-not $valid) { throw "Non-canonical managed name for ${Kind}: $Name" }
}
function Assert-RuntimePayload([string]$Root) {
    foreach ($directoryName in @("skills", "agents", "commands", "onboarding", "bin", ".claude-plugin")) {
        $path = Join-Path $Root $directoryName
        Assert-SafeContainer $path "$directoryName source"
        if (-not (Test-Path -LiteralPath $path -PathType Container)) { throw "Incomplete source payload, missing directory: $path" }
    }
    foreach ($relative in @("install.ps1", "bin/company", "commands/company.md", "onboarding/ONBOARDING.md", ".claude-plugin/plugin.json")) {
        $path = Join-Path $Root $relative
        try { $null = Get-FileFingerprint $path } catch { throw "Incomplete or unsafe source payload, required file missing: $path" }
    }
    $skillDirectories = @(Get-ChildItem -LiteralPath (Join-Path $Root "skills") -Directory)
    if ($skillDirectories.Count -eq 0) { throw "Incomplete source payload: no skills found in $Root/skills" }
    foreach ($directory in $skillDirectories) {
        Assert-CanonicalManagedName "skill" $directory.Name
        $null = Get-FileFingerprint (Join-Path $directory.FullName "SKILL.md")
    }
    $agentFiles = @(Get-ChildItem -LiteralPath (Join-Path $Root "agents") -File -Filter "*.md")
    if ($agentFiles.Count -eq 0) { throw "Incomplete source payload: no agents found in $Root/agents" }
    foreach ($file in $agentFiles) { Assert-CanonicalManagedName "agent" $file.Name; $null = Get-FileFingerprint $file.FullName }
}
function Assert-RuntimePayloadMatches([string]$Left, [string]$Right) {
    Assert-RuntimePayload $Left; Assert-RuntimePayload $Right
    foreach ($directoryName in @("skills", "agents", "commands", "onboarding")) {
        if ((Get-DirectoryFingerprint (Join-Path $Left $directoryName)) -cne (Get-DirectoryFingerprint (Join-Path $Right $directoryName))) { throw "Immutable checkout runtime directory was modified: $Left/$directoryName" }
    }
    foreach ($relative in @("bin/company", "install.ps1", ".claude-plugin/plugin.json")) {
        if ((Get-FileFingerprint (Join-Path $Left $relative)) -cne (Get-FileFingerprint (Join-Path $Right $relative))) { throw "Immutable checkout runtime file was modified: $Left/$relative" }
    }
}
function Remove-KnownPath([string]$Path) {
    if ([string]::IsNullOrWhiteSpace($Path)) { return }
    $item = Get-Item -LiteralPath $Path -Force -ErrorAction SilentlyContinue
    if ($item) { Remove-Item -LiteralPath $Path -Recurse -Force -ErrorAction Stop }
}
function Invoke-TestHook([string]$Point, [string]$Kind, [string]$Name, [string]$Destination, [string]$Backup) {
    if ([string]::IsNullOrWhiteSpace($env:CLAUDE_INC_TEST_HOOK)) { return }
    & $env:CLAUDE_INC_TEST_HOOK $Point $Kind $Name $Destination $Backup
    if ($LASTEXITCODE -ne 0) { throw "Test hook failed at $Point for $Kind/$Name" }
}

# Resolve a local checkout or clone a remote candidate without pulling the active cache.
$RemoteMode = $false; $RemoteCandidate = $null; $RemoteFinal = $null; $RemoteFinalWasNew = $false; $LegacyCompanyScript = $null
$CacheLock = "$CloneDir.claude-inc-cache.lock"; $CacheLockHeld = $false
$PrimaryFailure = $null; $CleanupFailures = New-Object 'Collections.Generic.List[string]'; $Committed = $false; $RecoverySucceeded = $true
try {
$LocalSource = -not [string]::IsNullOrWhiteSpace($PSScriptRoot) -and
    (Test-Path -LiteralPath (Join-Path $PSScriptRoot "install.ps1") -PathType Leaf)
if ($LocalSource) {
    $SourceRoot = [IO.Path]::GetFullPath($PSScriptRoot); Assert-RuntimePayload $SourceRoot; Write-Status "installing from local checkout: $SourceRoot"
} else {
    try { $null = New-Item -ItemType Directory -Path $CacheLock -ErrorAction Stop; $CacheLockHeld = $true }
    catch { throw "Another installation holds the remote cache lock: $CacheLock" }
    Invoke-TestHook "after-cache-lock" "cache" "cache" $CloneDir $CacheLock
    if ((Test-Path -LiteralPath $CloneDir) -and -not (Test-Path -LiteralPath (Join-Path $CloneDir ".git") -PathType Container)) { throw "Cache path exists but is not a git checkout: $CloneDir" }
    if (Test-Path -LiteralPath (Join-Path $CloneDir "bin/company") -PathType Leaf) { $LegacyCompanyScript = Join-Path $CloneDir "bin/company" }
    $RemoteMode = $true
    $RemoteCandidate = "$CloneDir.candidate.$([Guid]::NewGuid().ToString('N'))"
    Write-Status "cloning immutable candidate from $RepoUrl"
    try { Invoke-Git @("clone", "--depth", "1", $RepoUrl, $RemoteCandidate) }
    catch { if (Test-Path -LiteralPath $RemoteCandidate) { Remove-KnownPath $RemoteCandidate }; throw }
    $commit = (& (Get-Application "git").Source -C $RemoteCandidate rev-parse HEAD).Trim()
    if ($LASTEXITCODE -ne 0 -or $commit -notmatch '^[0-9a-fA-F]+$') { Remove-KnownPath $RemoteCandidate; throw "Cannot resolve a valid candidate commit." }
    $RemoteFinal = "$CloneDir.checkouts/$commit"
    $SourceRoot = $RemoteCandidate; Assert-RuntimePayload $SourceRoot
}

$SkillsSource = Join-Path $SourceRoot "skills"; $AgentsSource = Join-Path $SourceRoot "agents"; $CommandsSource = Join-Path $SourceRoot "commands"

# Discover Bash by probing the candidate. The installed wrapper points to the final immutable checkout.
$BashPath = $null; $CompanyScriptProbe = Join-Path $SourceRoot "bin/company"
if ((-not $NoBin) -or $Onboard) {
    if (-not (Test-Path -LiteralPath $CompanyScriptProbe -PathType Leaf) -and -not $NoBin) { throw "Company CLI not found in source: $CompanyScriptProbe" }
    if (Test-Path -LiteralPath $CompanyScriptProbe -PathType Leaf) {
        $companyItem = Get-Item -LiteralPath $CompanyScriptProbe -Force
        if (($companyItem.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) { throw "Company CLI source must not be a reparse point: $CompanyScriptProbe" }
        $bashes = @(Get-Command -Name "bash" -CommandType Application -All -ErrorAction SilentlyContinue | ForEach-Object { $_.Source })
        $git = Get-Application "git"
        if ($git) { $gitBash = [IO.Path]::GetFullPath((Join-Path (Split-Path -Parent $git.Source) "..\bin\bash.exe")); if (Test-Path -LiteralPath $gitBash -PathType Leaf) { $bashes += $gitBash } }
        foreach ($bash in @($bashes | Select-Object -Unique)) {
            $probe = & $bash -l $CompanyScriptProbe version 2>$null
            if ($LASTEXITCODE -eq 0 -and $probe -eq "company v1.2.0") { $BashPath = $bash; break }
        }
    }
    if ((-not $NoBin) -and -not $BashPath) { throw "The company CLI requires a working Bash. Install Git for Windows, or rerun with -NoBin." }
}

$CompanyScriptFinal = if ($RemoteMode) { Join-Path $RemoteFinal "bin/company" } else { $CompanyScriptProbe }
if ($Project) {
    $ProjectRoot = (Get-Location).ProviderPath; if (-not $ProjectRoot) { throw "-Project requires a filesystem working directory." }
    $Target = Join-Path $ProjectRoot ".claude"
} else { $Target = Join-Path $UserHome ".claude" }
$TargetSkills = Join-Path $Target "skills"; $TargetAgents = Join-Path $Target "agents"; $TargetCommands = Join-Path $Target "commands"
$BinDir = Join-Path $UserHome ".local/bin"; $WrapperPath = Join-Path $BinDir "company.cmd"
$ManifestPath = Join-Path $Target $ManifestName; $CliManifestPath = Join-Path (Join-Path $UserHome ".claude") $CliManifestName
$TargetLock = "$Target.claude-inc-install.lock"; $CliLock = Join-Path $UserHome ".claude-inc-cli-install.lock"
$TargetLockHeld = $false; $CliLockHeld = $false

$MainRecords = @{}; $CliRecords = @{}; $MainSnapshot = $null; $CliSnapshot = $null
$Plan = New-Object 'Collections.Generic.List[object]'; $Applied = New-Object 'Collections.Generic.List[object]'
$StageRoot = $null; $RollbackRoot = $null; $JournalPath = $null; $MainManifestTemp = $null; $CliManifestTemp = $null; $CliStageTemp = $null
$Committed = $false; $RecoverySucceeded = $true

function Get-Destination([string]$Kind, [string]$Name) {
    switch ($Kind) {
        "skill" { Join-Path $TargetSkills $Name }
        "agent" { Join-Path $TargetAgents $Name }
        "command" { Join-Path $TargetCommands $Name }
        "cli" { $WrapperPath }
        "meta-main" { $ManifestPath }
        "meta-cli" { $CliManifestPath }
        default { throw "Unknown managed kind: $Kind" }
    }
}
function Get-Backup([string]$Kind, [string]$Name) { Join-Path (Join-Path $RollbackRoot $Kind) $Name }
function Get-State([string]$Kind, [string]$Path) {
    $item = Get-Item -LiteralPath $Path -Force -ErrorAction SilentlyContinue
    if (-not $item) { return [pscustomobject]@{ Type = "absent"; Value = "-" } }
    if (($item.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) { throw "Reparse points are not allowed as managed destinations: $Path" }
    if ($item.PSIsContainer) { return [pscustomobject]@{ Type = "dir"; Value = Get-DirectoryFingerprint $Path } }
    if ($item -is [IO.FileInfo]) { return [pscustomobject]@{ Type = "file"; Value = Get-FileFingerprint $Path } }
    throw "Special files are not allowed as managed destinations: $Path"
}
function Test-State([string]$Kind, [string]$Path, [string]$Type, [string]$Value) {
    try { $state = Get-State $Kind $Path; return $state.Type -ceq $Type -and $state.Value -ceq $Value } catch { return $false }
}

function Read-Manifest([string]$Path, [hashtable]$Records, [string]$Scope) {
    $item = Get-Item -LiteralPath $Path -Force -ErrorAction SilentlyContinue
    if (-not $item) { return $null }
    if ($item.PSIsContainer -or ($item.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) { throw "Ownership manifest must be a regular file: $Path" }
    $bytes = [IO.File]::ReadAllBytes($Path); $snapshot = Get-BytesSha256 $bytes
    $lines = @([Text.RegularExpressions.Regex]::Split($Utf8NoBom.GetString($bytes), "`r`n|`n|`r"))
    if ($lines.Count -gt 1 -and $lines[$lines.Count - 1] -ceq "") { $lines = @($lines[0..($lines.Count - 2)]) }
    if ($lines.Count -lt 1 -or $lines[0] -cne $ManifestVersion) { throw "Invalid ownership manifest: $Path" }
    for ($index = 1; $index -lt $lines.Count; $index++) {
        $parts = $lines[$index].Split("`t"); if ($parts.Count -ne 4) { throw "Invalid ownership manifest row $($index + 1): $Path" }
        $kind, $name, $type, $value = $parts; Assert-SafeField $name "manifest name"; Assert-SafeField $value "manifest value"
        $allowedKinds = if ($Scope -eq "main") { @("skill", "agent", "command") } else { @("cli") }
        if ($kind -notin $allowedKinds) { throw "Invalid ownership manifest entry at row $($index + 1): $Path" }
        Assert-CanonicalManagedName $kind $name
        if (($kind -eq "skill" -and $type -ne "dir") -or ($kind -ne "skill" -and $type -ne "file") -or $value -notmatch '^[0-9a-fA-F]{64}$') { throw "Invalid ownership manifest type or fingerprint at row $($index + 1): $Path" }
        $key = "$kind`t$name"; if ($Records.ContainsKey($key)) { throw "Duplicate ownership manifest entry: $kind/$name" }
        $Records[$key] = [pscustomobject]@{ Kind = $kind; Name = $name; Type = $type; Value = $value.ToLowerInvariant() }
    }
    if ((Get-FileFingerprint $Path) -cne $snapshot) { throw "Ownership manifest changed while it was being snapshotted: $Path" }
    $snapshot
}
function Write-ManifestTemp([hashtable]$Records, [string]$Path) {
    $lines = New-Object 'Collections.Generic.List[string]'; $lines.Add($ManifestVersion)
    foreach ($key in @($Records.Keys | Sort-Object)) { $record = $Records[$key]; $lines.Add("$($record.Kind)`t$($record.Name)`t$($record.Type)`t$($record.Value)") }
    [IO.File]::WriteAllText($Path, (($lines.ToArray() -join "`n") + "`n"), $Utf8NoBom)
}
function Add-PlanEntry([string]$Kind, [string]$Name, [string]$DesiredType, [string]$DesiredValue, [string]$SourcePath, [string]$Content, [string]$LegacyValue) {
    Assert-CanonicalManagedName $Kind $Name
    $destination = Get-Destination $Kind $Name; $state = Get-State $Kind $destination
    $records = if ($Kind -eq "cli") { $CliRecords } else { $MainRecords }; $key = "$Kind`t$Name"
    if ($records.ContainsKey($key)) {
        $old = $records[$key]
        if ($state.Type -eq "absent") { throw "Managed $Kind '$Name' is missing; restore it or remove its manifest entry before retrying." }
        if ($state.Type -cne $old.Type -or $state.Value -cne $old.Value) { throw "Managed $Kind '$Name' was modified; no files were changed: $destination" }
    } elseif ($state.Type -ne "absent") {
        $legacyMatch = -not [string]::IsNullOrEmpty($LegacyValue) -and $state.Type -eq "file" -and $state.Value -ceq $LegacyValue
        if (-not $legacyMatch -and ($state.Type -cne $DesiredType -or $state.Value -cne $DesiredValue)) { throw "Unmanaged collision for $Kind '$Name'; no files were changed: $destination" }
    }
    $Plan.Add([pscustomobject]@{ Kind=$Kind; Name=$Name; DesiredType=$DesiredType; DesiredValue=$DesiredValue; SourcePath=$SourcePath; Content=$Content; Destination=$destination; PriorType=$state.Type; PriorValue=$state.Value; StagePath=$null })
    $records[$key] = [pscustomobject]@{ Kind=$Kind; Name=$Name; Type=$DesiredType; Value=$DesiredValue }
}

function Assert-ManifestSnapshotsUnchanged {
    $currentMain = Get-Item -LiteralPath $ManifestPath -Force -ErrorAction SilentlyContinue
    if ($null -eq $MainSnapshot) { if ($currentMain) { throw "Ownership manifest appeared during installation; retry." } }
    elseif (-not $currentMain -or (Get-FileFingerprint $ManifestPath) -cne $MainSnapshot) { throw "Ownership manifest changed during installation; retry." }
    if (-not $NoBin) {
        $currentCli = Get-Item -LiteralPath $CliManifestPath -Force -ErrorAction SilentlyContinue
        if ($null -eq $CliSnapshot) { if ($currentCli) { throw "CLI ownership manifest appeared during installation; retry." } }
        elseif (-not $currentCli -or (Get-FileFingerprint $CliManifestPath) -cne $CliSnapshot) { throw "CLI ownership manifest changed during installation; retry." }
    }
}
function Assert-SnapshotsUnchanged {
    Assert-ManifestSnapshotsUnchanged
    foreach ($entry in $Plan) { if (-not (Test-State $entry.Kind $entry.Destination $entry.PriorType $entry.PriorValue)) { throw "Destination changed during installation; retry: $($entry.Destination)" } }
}

function Invoke-PreparedEntry([object]$Entry) {
    $backup = Get-Backup $Entry.Kind $Entry.Name
    Invoke-TestHook "before-entry" $Entry.Kind $Entry.Name $Entry.Destination $backup
    if (-not (Test-State $Entry.Kind $Entry.Destination $Entry.PriorType $Entry.PriorValue)) { throw "Destination changed immediately before apply; no overwrite performed: $($Entry.Destination)" }
    $hadOld = $Entry.PriorType -ne "absent"
    $null = New-Item -ItemType Directory -Force -Path (Split-Path -Parent $Entry.Destination), (Split-Path -Parent $backup)
    $operation = [pscustomobject]@{ Kind=$Entry.Kind; Name=$Entry.Name; Destination=$Entry.Destination; Backup=$backup; HadOld=$hadOld; PriorType=$Entry.PriorType; PriorValue=$Entry.PriorValue; DesiredType=$Entry.DesiredType; DesiredValue=$Entry.DesiredValue }
    $Applied.Add($operation)
    [IO.File]::AppendAllText($JournalPath, (($operation | ConvertTo-Json -Compress) + "`n"), $Utf8NoBom)
    Invoke-TestHook "after-journal" $Entry.Kind $Entry.Name $Entry.Destination $backup
    if ($hadOld) {
        Move-Item -LiteralPath $Entry.Destination -Destination $backup
        if (-not (Test-State $Entry.Kind $backup $Entry.PriorType $Entry.PriorValue)) { throw "Backup verification failed immediately after move; recovery data retained at $backup" }
    }
    Invoke-TestHook "after-backup" $Entry.Kind $Entry.Name $Entry.Destination $backup
    if ($Entry.DesiredType -ne "absent") {
        try {
            if ($Entry.DesiredType -eq "dir") { [IO.Directory]::Move($Entry.StagePath, $Entry.Destination) }
            else { [IO.File]::Move($Entry.StagePath, $Entry.Destination) }
        } catch { throw "Destination appeared after backup; no overwrite performed: $($Entry.Destination)" }
        if (-not (Test-State $Entry.Kind $Entry.Destination $Entry.DesiredType $Entry.DesiredValue)) { throw "Claimed destination failed verification; recovery data retained: $($Entry.Destination)" }
    }
    Invoke-TestHook "after-entry" $Entry.Kind $Entry.Name $Entry.Destination $backup
}

function Restore-AppliedEntries {
    $failed = $false
    for ($index = $Applied.Count - 1; $index -ge 0; $index--) {
        $operation = $Applied[$index]
        try {
            Invoke-TestHook "before-restore" $operation.Kind $operation.Name $operation.Destination $operation.Backup
            $backupExists = $null -ne (Get-Item -LiteralPath $operation.Backup -Force -ErrorAction SilentlyContinue)
            $destinationExists = $null -ne (Get-Item -LiteralPath $operation.Destination -Force -ErrorAction SilentlyContinue)
            if ($operation.HadOld) {
                if ($backupExists) {
                    if (-not (Test-State $operation.Kind $operation.Backup $operation.PriorType $operation.PriorValue)) { throw "Recovery backup failed verification: $($operation.Backup)" }
                    if ($destinationExists) {
                        if (-not (Test-State $operation.Kind $operation.Destination $operation.DesiredType $operation.DesiredValue)) { throw "Recovery refused to overwrite unexpected content: $($operation.Destination)" }
                        Remove-KnownPath $operation.Destination
                    }
                    Move-Item -LiteralPath $operation.Backup -Destination $operation.Destination
                    if (-not (Test-State $operation.Kind $operation.Destination $operation.PriorType $operation.PriorValue)) { throw "Restored destination failed verification: $($operation.Destination)" }
                } elseif (-not (Test-State $operation.Kind $operation.Destination $operation.PriorType $operation.PriorValue)) { throw "Required recovery backup is missing: $($operation.Backup)" }
            } elseif ($backupExists) { throw "Unexpected recovery backup: $($operation.Backup)" }
            elseif ($destinationExists) {
                if (-not (Test-State $operation.Kind $operation.Destination $operation.DesiredType $operation.DesiredValue)) { throw "Recovery refused to remove unexpected content: $($operation.Destination)" }
                Remove-KnownPath $operation.Destination
            }
        } catch {
            $failed = $true; Write-Error "$($_.Exception.Message). Recovery data retained at $RollbackRoot" -ErrorAction Continue
        }
    }
    return -not $failed
}

try {
    # Locks are acquired before snapshots. The CLI lock is global even for project installs.
    try { $null = New-Item -ItemType Directory -Path $TargetLock -ErrorAction Stop; $TargetLockHeld = $true }
    catch { throw "Another installation holds the target lock: $TargetLock" }
    if (-not $NoBin -and $CliLock -cne $TargetLock) {
        try { $null = New-Item -ItemType Directory -Path $CliLock -ErrorAction Stop; $CliLockHeld = $true }
        catch { throw "Another installation holds the global CLI lock: $CliLock" }
    }

    Assert-SafeContainer $Target "Install target"; Assert-SafeContainer $TargetSkills "Skills target"; Assert-SafeContainer $TargetAgents "Agents target"; Assert-SafeContainer $TargetCommands "Commands target"
    if (-not $NoBin) { Assert-SafeContainer (Join-Path $UserHome ".local") "CLI parent"; Assert-SafeContainer $BinDir "CLI directory"; Assert-SafeContainer (Join-Path $UserHome ".claude") "Global CLI ownership directory" }
    $MainSnapshot = Read-Manifest $ManifestPath $MainRecords "main"
    if (-not $NoBin) { $CliSnapshot = Read-Manifest $CliManifestPath $CliRecords "cli" }

    $SkillDirs = @(Get-ChildItem -LiteralPath $SkillsSource -Directory)
    foreach ($directory in $SkillDirs) {
        if (($directory.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) { throw "Skill source must not be a reparse point: $($directory.FullName)" }
        Add-PlanEntry "skill" $directory.Name "dir" (Get-DirectoryFingerprint $directory.FullName) $directory.FullName $null $null
    }
    $AgentFiles = @(Get-ChildItem -LiteralPath $AgentsSource -File -Filter "*.md")
    foreach ($file in $AgentFiles) { Add-PlanEntry "agent" $file.Name "file" (Get-FileFingerprint $file.FullName) $file.FullName $null $null }
    $commandSource = Join-Path $CommandsSource "company.md"
    Add-PlanEntry "command" "company.md" "file" (Get-FileFingerprint $commandSource) $commandSource $null $null

    if (-not $NoBin) {
        $escapedBash = $BashPath.Replace("%", "%%"); $escapedCompany = $CompanyScriptFinal.Replace("%", "%%")
        $wrapperContent = "@echo off`r`n`"$escapedBash`" -l `"$escapedCompany`" %*`r`n"
        $wrapperHash = Get-BytesSha256 $Utf8NoBom.GetBytes($wrapperContent)
        $legacyHash = $null
        if ($LegacyCompanyScript) {
            $legacyEscaped = $LegacyCompanyScript.Replace("%", "%%")
            $legacyWrapper = "@echo off`r`n`"$escapedBash`" -l `"$legacyEscaped`" %*`r`n"
            $legacyHash = Get-BytesSha256 $Utf8NoBom.GetBytes($legacyWrapper)
        }
        Add-PlanEntry "cli" "company.cmd" "file" $wrapperHash $null $wrapperContent $legacyHash
    }

    # Upstream removals are safe only while the old managed bytes remain untouched.
    foreach ($key in @($MainRecords.Keys)) {
        $record = $MainRecords[$key]
        if (-not @($Plan | Where-Object { $_.Kind -ceq $record.Kind -and $_.Name -ceq $record.Name }).Count) {
            $destination = Get-Destination $record.Kind $record.Name; $state = Get-State $record.Kind $destination
            if ($state.Type -cne $record.Type -or $state.Value -cne $record.Value) { throw "Upstream removed $($record.Kind) '$($record.Name)', but its installed copy was modified; no files were changed: $destination" }
            $Plan.Add([pscustomobject]@{ Kind=$record.Kind; Name=$record.Name; DesiredType="absent"; DesiredValue="-"; SourcePath=$null; Content=$null; Destination=$destination; PriorType=$state.Type; PriorValue=$state.Value; StagePath=$null })
            $MainRecords.Remove($key)
        }
    }

    Assert-SnapshotsUnchanged
    $null = New-Item -ItemType Directory -Force -Path $Target
    $StageRoot = Join-Path $Target (".claude-inc-stage-" + [Guid]::NewGuid().ToString("N")); $RollbackRoot = Join-Path $Target (".claude-inc-rollback-" + [Guid]::NewGuid().ToString("N"))
    $null = New-Item -ItemType Directory -Path $StageRoot, $RollbackRoot
    $JournalPath = Join-Path $RollbackRoot "journal.jsonl"; [IO.File]::WriteAllText($JournalPath, "", $Utf8NoBom)
    foreach ($entry in $Plan) {
        if ($entry.DesiredType -eq "absent") { continue }
        if ($entry.Kind -eq "cli") {
            $null = New-Item -ItemType Directory -Force -Path $BinDir
            Assert-SafeContainer $BinDir "CLI directory"
            $stagePath = Join-Path $BinDir (".claude-inc-company-stage-" + [Guid]::NewGuid().ToString("N") + ".tmp")
            $CliStageTemp = $stagePath
            $bytes = $Utf8NoBom.GetBytes($entry.Content)
            $stream = [IO.File]::Open($stagePath, [IO.FileMode]::CreateNew, [IO.FileAccess]::Write, [IO.FileShare]::None)
            try { $stream.Write($bytes, 0, $bytes.Length); $stream.Flush($true) } finally { $stream.Dispose() }
            if ((Get-FileFingerprint $stagePath) -cne $entry.DesiredValue) { throw "Staged CLI verification failed" }
            Invoke-TestHook "after-cli-stage" $entry.Kind $entry.Name $entry.Destination $stagePath
        } else {
            $stagePath = Join-Path (Join-Path $StageRoot $entry.Kind) $entry.Name
            $null = New-Item -ItemType Directory -Force -Path (Split-Path -Parent $stagePath)
            if ($entry.Kind -eq "skill") { Copy-Item -LiteralPath $entry.SourcePath -Destination $stagePath -Recurse; if ((Get-DirectoryFingerprint $stagePath) -cne $entry.DesiredValue) { throw "Staged skill verification failed: $($entry.Name)" } }
            else { Copy-Item -LiteralPath $entry.SourcePath -Destination $stagePath; if ((Get-FileFingerprint $stagePath) -cne $entry.DesiredValue) { throw "Staged file verification failed: $($entry.Name)" } }
        }
        $entry.StagePath = $stagePath
    }
    Invoke-TestHook "after-stage" "none" "none" $Target $RollbackRoot
    Assert-SnapshotsUnchanged

    if ($RemoteMode) {
        if (Test-Path -LiteralPath $RemoteFinal) {
            Assert-SafeContainer $RemoteFinal "Immutable checkout"
            Assert-RuntimePayloadMatches $RemoteFinal $RemoteCandidate
            Remove-KnownPath $RemoteCandidate; $RemoteCandidate = $null
        } else {
            $null = New-Item -ItemType Directory -Force -Path (Split-Path -Parent $RemoteFinal)
            [IO.Directory]::Move($RemoteCandidate, $RemoteFinal); $RemoteCandidate = $null; $RemoteFinalWasNew = $true
        }
        $SourceRoot = $RemoteFinal
    }

    foreach ($entry in $Plan) { Invoke-PreparedEntry $entry }

    # Both manifests participate in the same journal and are committed last.
    Assert-ManifestSnapshotsUnchanged
    $MainManifestTemp = Join-Path $Target ($ManifestName + ".tmp." + [Guid]::NewGuid().ToString("N")); Write-ManifestTemp $MainRecords $MainManifestTemp
    $mainEntry = [pscustomobject]@{ Kind="meta-main"; Name="manifest"; DesiredType="file"; DesiredValue=Get-FileFingerprint $MainManifestTemp; Destination=$ManifestPath; PriorType=$(if ($null -eq $MainSnapshot) { "absent" } else { "file" }); PriorValue=$(if ($null -eq $MainSnapshot) { "-" } else { $MainSnapshot }); StagePath=$MainManifestTemp }
    Invoke-PreparedEntry $mainEntry; $MainManifestTemp = $null
    if (-not $NoBin) {
        $null = New-Item -ItemType Directory -Force -Path (Split-Path -Parent $CliManifestPath)
        $CliManifestTemp = Join-Path (Split-Path -Parent $CliManifestPath) ($CliManifestName + ".tmp." + [Guid]::NewGuid().ToString("N")); Write-ManifestTemp $CliRecords $CliManifestTemp
        $cliEntry = [pscustomobject]@{ Kind="meta-cli"; Name="manifest"; DesiredType="file"; DesiredValue=Get-FileFingerprint $CliManifestTemp; Destination=$CliManifestPath; PriorType=$(if ($null -eq $CliSnapshot) { "absent" } else { "file" }); PriorValue=$(if ($null -eq $CliSnapshot) { "-" } else { $CliSnapshot }); StagePath=$CliManifestTemp }
        Invoke-PreparedEntry $cliEntry; $CliManifestTemp = $null
    }
    $Committed = $true
} catch {
    $originalError = $_
    $PrimaryFailure = $_
    if ($Applied.Count -gt 0) { $RecoverySucceeded = Restore-AppliedEntries }
    if (-not $RecoverySucceeded) { throw "$($originalError.Exception.Message) Automatic recovery was incomplete. Inspect $RollbackRoot and its journal before removing retained locks." }
    throw
} finally {
    try { if ($StageRoot -and (Test-Path -LiteralPath $StageRoot)) { Invoke-TestHook "before-cleanup-stage" "cleanup" "stage" $StageRoot $RollbackRoot; Remove-KnownPath $StageRoot } } catch { $CleanupFailures.Add("stage cleanup: $($_.Exception.Message)") }
    try { if ($CliStageTemp -and (Test-Path -LiteralPath $CliStageTemp)) { Remove-KnownPath $CliStageTemp } } catch { $CleanupFailures.Add("CLI stage cleanup: $($_.Exception.Message)") }
    try { if ($MainManifestTemp -and (Test-Path -LiteralPath $MainManifestTemp)) { Remove-KnownPath $MainManifestTemp } } catch { $CleanupFailures.Add("main manifest temporary cleanup: $($_.Exception.Message)") }
    try { if ($CliManifestTemp -and (Test-Path -LiteralPath $CliManifestTemp)) { Remove-KnownPath $CliManifestTemp } } catch { $CleanupFailures.Add("CLI manifest temporary cleanup: $($_.Exception.Message)") }
    try { if ($RemoteCandidate -and (Test-Path -LiteralPath $RemoteCandidate)) { Remove-KnownPath $RemoteCandidate; $RemoteCandidate = $null } } catch { $CleanupFailures.Add("remote candidate cleanup: $($_.Exception.Message)") }
    try { if (-not $Committed -and $RemoteFinalWasNew -and $RecoverySucceeded -and (Test-Path -LiteralPath $RemoteFinal)) { Remove-KnownPath $RemoteFinal } } catch { $CleanupFailures.Add("immutable checkout rollback cleanup: $($_.Exception.Message)") }
    try { if (($Committed -or $RecoverySucceeded) -and $RollbackRoot -and (Test-Path -LiteralPath $RollbackRoot)) { Remove-KnownPath $RollbackRoot } } catch { $CleanupFailures.Add("rollback cleanup: $($_.Exception.Message)") }
    if ($Committed -or $RecoverySucceeded) {
        try { if ($CliLockHeld -and (Test-Path -LiteralPath $CliLock)) { Remove-KnownPath $CliLock; $CliLockHeld = $false } } catch { $CleanupFailures.Add("CLI lock cleanup: $($_.Exception.Message)") }
        try { if ($TargetLockHeld -and (Test-Path -LiteralPath $TargetLock)) { Remove-KnownPath $TargetLock; $TargetLockHeld = $false } } catch { $CleanupFailures.Add("target lock cleanup: $($_.Exception.Message)") }
        try { if ($CacheLockHeld -and (Test-Path -LiteralPath $CacheLock)) { Remove-KnownPath $CacheLock; $CacheLockHeld = $false } } catch { $CleanupFailures.Add("cache lock cleanup: $($_.Exception.Message)") }
    } else {
        Write-Error "Recovery data and installation locks retained: $RollbackRoot, $TargetLock, $CliLock, $CacheLock" -ErrorAction Continue
    }
}

if ($CleanupFailures.Count -gt 0) { throw "Installation cleanup was incomplete: $($CleanupFailures -join '; ')" }

if (-not $NoBin) {
    $PathEntries = @($env:PATH -split [IO.Path]::PathSeparator)
    if ($PathEntries -notcontains $BinDir) { Write-Status "note: add $BinDir to your PATH to use 'company'" }
}
Write-Host ""; Write-Status "hired $($AgentFiles.Count) department heads and $($SkillDirs.Count) employees -> $Target"; Write-Host ""; Write-Host "  Next:"
if (-not $NoBin) { Write-Host "    company roster"; Write-Host '    company brief "launch my product"' }
Write-Host "    claude"

if ($Onboard) {
    if ($NoBin) { $DeferredCommand = if ($Project) { "Install the Claude Code plugin, then run: /onboard" } else { "Install the Claude Code plugin, then run: /onboard --global" } }
    elseif ($Project) { $DeferredCommand = "company onboard" } else { $DeferredCommand = "company onboard --global" }
    $EngineName = if ([string]::IsNullOrWhiteSpace($env:CLAUDE_INC_ENGINE)) { "claude" } else { $env:CLAUDE_INC_ENGINE }
    $Engine = Get-Application $EngineName
    $Interactive = [Environment]::UserInteractive -and -not [Console]::IsInputRedirected -and -not [Console]::IsOutputRedirected
    if ((-not $NoBin) -and $Interactive -and $BashPath -and $Engine) {
        $OnboardArguments = @("-l", (Join-Path $SourceRoot "bin/company"), "onboard"); if (-not $Project) { $OnboardArguments += "--global" }
        & $BashPath @OnboardArguments
        if ($LASTEXITCODE -ne 0) { Write-Status "onboarding did not complete"; Write-Output "Onboarding deferred. Next step: $DeferredCommand" }
    } else { Write-Output "Onboarding deferred. Next step: $DeferredCommand" }
}
} catch {
    if ($null -eq $PrimaryFailure) { $PrimaryFailure = $_ }
    throw
} finally {
    try { if ($RemoteCandidate -and (Test-Path -LiteralPath $RemoteCandidate)) { Remove-KnownPath $RemoteCandidate; $RemoteCandidate = $null } } catch { $CleanupFailures.Add("outer remote candidate cleanup: $($_.Exception.Message)") }
    try { if ($CacheLockHeld -and ($Committed -or $RecoverySucceeded) -and (Test-Path -LiteralPath $CacheLock)) { Remove-KnownPath $CacheLock; $CacheLockHeld = $false } } catch { $CleanupFailures.Add("outer cache lock cleanup: $($_.Exception.Message)") }
    if ($CleanupFailures.Count -gt 0 -and $null -ne $PrimaryFailure) {
        Write-Error "Primary failure preserved: $($PrimaryFailure.Exception.Message). Additional cleanup failures: $($CleanupFailures -join '; ')" -ErrorAction Continue
    } elseif ($CleanupFailures.Count -gt 0) {
        throw "Installation cleanup was incomplete: $($CleanupFailures -join '; ')"
    }
}
