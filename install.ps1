[CmdletBinding()]
param(
    [switch]$Project,
    [switch]$NoBin,
    [switch]$Onboard
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$RepoUrl = "https://github.com/alebgl77/claude-inc"
$UserHome = if (-not [string]::IsNullOrWhiteSpace($env:HOME)) {
    [IO.Path]::GetFullPath($env:HOME)
} elseif ($HOME) {
    [IO.Path]::GetFullPath($HOME)
} else {
    throw "Unable to determine the user home directory."
}
$CloneDir = if (-not [string]::IsNullOrWhiteSpace($env:CLAUDE_INC_HOME)) {
    [IO.Path]::GetFullPath($env:CLAUDE_INC_HOME)
} else {
    Join-Path $UserHome ".claude-inc"
}

function Write-Status([string]$Message) {
    Write-Host "claude-inc $Message"
}

function Get-Application([string]$Name) {
    Get-Command -Name $Name -CommandType Application -ErrorAction SilentlyContinue |
        Select-Object -First 1
}

function Invoke-Git([string[]]$Arguments) {
    $git = Get-Application "git"
    if (-not $git) {
        throw "Git is required when install.ps1 is not running from a local checkout."
    }
    & $git.Source @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "Git failed with exit code $LASTEXITCODE."
    }
}

$LocalSource = -not [string]::IsNullOrWhiteSpace($PSScriptRoot) -and
    (Test-Path -LiteralPath (Join-Path $PSScriptRoot "skills") -PathType Container) -and
    (Test-Path -LiteralPath (Join-Path $PSScriptRoot "agents") -PathType Container)

if ($LocalSource) {
    $SourceRoot = [IO.Path]::GetFullPath($PSScriptRoot)
    Write-Status "installing from local checkout: $SourceRoot"
} else {
    $GitDir = Join-Path $CloneDir ".git"
    if (Test-Path -LiteralPath $GitDir -PathType Container) {
        Write-Status "updating $CloneDir"
        Invoke-Git @("-C", $CloneDir, "pull", "--ff-only")
    } else {
        if (Test-Path -LiteralPath $CloneDir) {
            throw "Cache path exists but is not a git checkout: $CloneDir"
        }
        Write-Status "cloning $RepoUrl -> $CloneDir"
        Invoke-Git @("clone", "--depth", "1", $RepoUrl, $CloneDir)
    }
    $SourceRoot = $CloneDir
}

$SkillsSource = Join-Path $SourceRoot "skills"
$AgentsSource = Join-Path $SourceRoot "agents"
if (-not (Test-Path -LiteralPath $SkillsSource -PathType Container) -or
    -not (Test-Path -LiteralPath $AgentsSource -PathType Container)) {
    throw "Source checkout is incomplete: expected skills/ and agents/ in $SourceRoot"
}

$BashPath = $null
$CompanyScript = Join-Path $SourceRoot "bin/company"
if ((-not $NoBin) -or $Onboard) {
    $CompanyScriptExists = Test-Path -LiteralPath $CompanyScript -PathType Leaf
    if (-not $CompanyScriptExists -and -not $NoBin) {
        throw "Company CLI not found in source: $CompanyScript"
    }
    if ($CompanyScriptExists) {
        $bashes = @(Get-Command -Name "bash" -CommandType Application -All -ErrorAction SilentlyContinue |
            ForEach-Object { $_.Source })
        $git = Get-Application "git"
        if ($git) {
            $gitBash = [IO.Path]::GetFullPath((Join-Path (Split-Path -Parent $git.Source) "..\bin\bash.exe"))
            if (Test-Path -LiteralPath $gitBash -PathType Leaf) {
                $bashes += $gitBash
            }
        }
        foreach ($bash in @($bashes | Select-Object -Unique)) {
            $probe = & $bash -l $CompanyScript version 2>$null
            if ($LASTEXITCODE -eq 0 -and $probe -eq "company v1.2.0") {
                $BashPath = $bash
                break
            }
        }
    }
    if ((-not $NoBin) -and -not $BashPath) {
        throw "The company CLI requires a working Bash. Install Git for Windows, or rerun with -NoBin."
    }
}

if ($Project) {
    $ProjectRoot = (Get-Location).ProviderPath
    if (-not $ProjectRoot) {
        throw "-Project requires a filesystem working directory."
    }
    $Target = Join-Path $ProjectRoot ".claude"
} else {
    $ProjectRoot = $null
    $Target = Join-Path $UserHome ".claude"
}

$TargetSkills = Join-Path $Target "skills"
$TargetAgents = Join-Path $Target "agents"
$null = New-Item -ItemType Directory -Force -Path $TargetSkills, $TargetAgents

$SkillDirs = @(Get-ChildItem -LiteralPath $SkillsSource -Directory)
foreach ($directory in $SkillDirs) {
    $destination = Join-Path $TargetSkills $directory.Name
    if (Test-Path -LiteralPath $destination) {
        Remove-Item -LiteralPath $destination -Recurse -Force
    }
    Copy-Item -LiteralPath $directory.FullName -Destination $destination -Recurse -Force
}

$AgentFiles = @(Get-ChildItem -LiteralPath $AgentsSource -File -Filter "*.md")
foreach ($file in $AgentFiles) {
    Copy-Item -LiteralPath $file.FullName -Destination (Join-Path $TargetAgents $file.Name) -Force
}

if ($Project) {
    $ProjectManual = Join-Path $ProjectRoot "CLAUDE.md"
    if (-not (Test-Path -LiteralPath $ProjectManual)) {
        Copy-Item -LiteralPath (Join-Path $SourceRoot "CLAUDE.md") -Destination $ProjectManual
        Write-Status "CEO manual installed as ./CLAUDE.md"
    }
}

if (-not $NoBin) {
    $BinDir = Join-Path $UserHome ".local/bin"
    $null = New-Item -ItemType Directory -Force -Path $BinDir
    $WrapperPath = Join-Path $BinDir "company.cmd"
    $Wrapper = "@echo off`r`n`"$BashPath`" -l `"$CompanyScript`" %*`r`n"
    [IO.File]::WriteAllText($WrapperPath, $Wrapper, [Text.UTF8Encoding]::new($false))
    $PathEntries = @($env:PATH -split [IO.Path]::PathSeparator)
    if ($PathEntries -notcontains $BinDir) {
        Write-Status "note: add $BinDir to your PATH to use 'company'"
    }
}

Write-Host ""
Write-Status "hired $($AgentFiles.Count) department heads and $($SkillDirs.Count) employees -> $Target"
Write-Host ""
Write-Host "  Next:"
if (-not $NoBin) {
    Write-Host "    company roster"
    Write-Host '    company brief "launch my product"'
}
Write-Host "    claude"

if ($Onboard) {
    $ScopeArgument = if ($Project) { "" } else { " --global" }
    if ($NoBin) {
        $DeferredCommand = if ($Project) {
            "Install the Claude Code plugin, then run: /onboard"
        } else {
            "Install the Claude Code plugin, then run: /onboard --global"
        }
    } elseif ($Project) {
        $DeferredCommand = "company onboard"
    } else {
        $DeferredCommand = "company onboard --global"
    }
    $EngineName = if (-not [string]::IsNullOrWhiteSpace($env:CLAUDE_INC_ENGINE)) {
        $env:CLAUDE_INC_ENGINE
    } else {
        "claude"
    }
    $Engine = Get-Application $EngineName
    $Interactive = [Environment]::UserInteractive -and
        -not [Console]::IsInputRedirected -and
        -not [Console]::IsOutputRedirected
    if ((-not $NoBin) -and $Interactive -and $BashPath -and $Engine) {
        $OnboardArguments = @("-l", $CompanyScript, "onboard")
        if (-not $Project) {
            $OnboardArguments += "--global"
        }
        & $BashPath @OnboardArguments
        if ($LASTEXITCODE -ne 0) {
            Write-Status "onboarding did not complete"
            Write-Output "Onboarding deferred. Next step: $DeferredCommand"
        }
    } else {
        Write-Output "Onboarding deferred. Next step: $DeferredCommand"
    }
}
