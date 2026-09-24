<#
.SYNOPSIS
    管理个人 Agent Skills 的 Windows Junction（目录联接）挂载脚本。

.DESCRIPTION
    支持按需在全局 (~/.agents/skills) 或指定项目内热挂载、卸载和状态查看。
    修改 skills 仓库代码后实时生效，无需重复复制或构建。

.PARAMETER List
    查看所有技能及当前挂载状态。

.PARAMETER Install
    按需挂载一个或多个技能（逗号分隔或传递数组），如: -Install grilling,to-spec 或 -Install all

.PARAMETER Uninstall
    卸载一个或多个技能挂载，如: -Uninstall grilling 或 -Uninstall all

.PARAMETER Project
    可选。指定项目根目录；若不指定则默认挂载到全局 (~/.agents/skills)。

.EXAMPLE
    .\manage-skills.ps1 -List
    .\manage-skills.ps1 -Install grilling,to-spec,prototype
    .\manage-skills.ps1 -Install all
    .\manage-skills.ps1 -Uninstall prototype
    .\manage-skills.ps1 -Install prototype -Project "D:\wiki\project\spec-anchor"
#>

[CmdletBinding(DefaultParameterSetName = "List")]
param (
    [Parameter(ParameterSetName = "List")]
    [switch]$List,

    [Parameter(ParameterSetName = "Install", Mandatory = $true)]
    [string[]]$Install,

    [Parameter(ParameterSetName = "Uninstall", Mandatory = $true)]
    [string[]]$Uninstall,

    [Parameter(ParameterSetName = "Install")]
    [Parameter(ParameterSetName = "Uninstall")]
    [Parameter(ParameterSetName = "List")]
    [string]$Project
)

$RepoRoot = $PSScriptRoot
$SkillsSourceDir = Join-Path $RepoRoot "skills"

# 确定目标挂载基准目录
if ($Project) {
    $TargetBase = Join-Path (Resolve-Path $Project) ".agents\skills"
} else {
    $TargetBase = Join-Path $env:USERPROFILE ".agents\skills"
}

# 发现当前仓库中的所有技能
$AvailableSkills = @{}
Get-ChildItem -Path $SkillsSourceDir -Recurse -Filter "SKILL.md" | ForEach-Object {
    $skillName = $_.Directory.Name
    $AvailableSkills[$skillName] = $_.Directory.FullName
}

function Ensure-TargetDir {
    if (-not (Test-Path $TargetBase)) {
        New-Item -ItemType Directory -Path $TargetBase -Force | Out-Null
    }
}

function Show-Status {
    Write-Host "`n=== Agent Skills 挂载状态 ===" -ForegroundColor Cyan
    Write-Host "目标目录: $TargetBase" -ForegroundColor Gray
    Write-Host ("-" * 60) -ForegroundColor Gray

    $installedCount = 0
    foreach ($name in ($AvailableSkills.Keys | Sort-Object)) {
        $targetPath = Join-Path $TargetBase $name
        $isLinked = $false
        $linkTarget = ""

        if (Test-Path $targetPath) {
            $item = Get-Item $targetPath -Force
            if ($item.Attributes -band [System.IO.FileAttributes]::ReparsePoint) {
                $isLinked = $true
                $linkTarget = $item.Target
                $installedCount++
            }
        }

        if ($isLinked) {
            Write-Host " [已挂载] " -ForegroundColor Green -NoNewline
            Write-Host "$name" -ForegroundColor Yellow -NoNewline
            Write-Host " -> $linkTarget" -ForegroundColor DarkGray
        } else {
            Write-Host " [未挂载] " -ForegroundColor DarkGray -NoNewline
            Write-Host "$name" -ForegroundColor White
        }
    }
    Write-Host ("-" * 60) -ForegroundColor Gray
    Write-Host "共收纳 $($AvailableSkills.Count) 个技能，当前已挂载 $installedCount 个。`n" -ForegroundColor Cyan
}

function Install-Skill([string]$Name) {
    if (-not $AvailableSkills.ContainsKey($Name)) {
        Write-Warning "未找到名为 [$Name] 的技能，请检查拼写。"
        return
    }

    Ensure-TargetDir
    $source = $AvailableSkills[$Name]
    $dest = Join-Path $TargetBase $Name

    if (Test-Path $dest) {
        $item = Get-Item $dest -Force
        if ($item.Attributes -band [System.IO.FileAttributes]::ReparsePoint) {
            Write-Host "[$Name] 已经处于挂载状态，跳过。" -ForegroundColor Yellow
            return
        } else {
            Write-Error "目标位置 [$dest] 已存在同名普通目录/文件，为避免数据丢失，未进行覆盖。"
            return
        }
    }

    New-Item -ItemType Junction -Path $dest -Target $source | Out-Null
    Write-Host "✓ 成功挂载技能: " -ForegroundColor Green -NoNewline
    Write-Host "$Name" -ForegroundColor Yellow -NoNewline
    Write-Host " -> $dest" -ForegroundColor DarkGray
}

function Uninstall-Skill([string]$Name) {
    $dest = Join-Path $TargetBase $Name
    if (-not (Test-Path $dest)) {
        Write-Host "[$Name] 当前未挂载，无需操作。" -ForegroundColor DarkGray
        return
    }

    $item = Get-Item $dest -Force
    if ($item.Attributes -band [System.IO.FileAttributes]::ReparsePoint) {
        $item.Delete()
        Write-Host "✓ 成功卸载挂载点: [$Name]" -ForegroundColor Green
    } else {
        Write-Error "目标位置 [$dest] 不是 Junction 软链接，请手动确认，脚本拒绝执行物理删除。"
    }
}

# --- 执行入口 ---
if ($PSCmdlet.ParameterSetName -eq "List" -or $List) {
    Show-Status
}
elseif ($PSCmdlet.ParameterSetName -eq "Install") {
    $names = @()
    foreach ($item in $Install) {
        $names += $item.Split(',') | ForEach-Object { $_.Trim() }
    }
    if ($names -contains "all") {
        $names = $AvailableSkills.Keys
    }
    foreach ($n in $names) {
        if ($n) { Install-Skill -Name $n }
    }
    Show-Status
}
elseif ($PSCmdlet.ParameterSetName -eq "Uninstall") {
    $names = @()
    foreach ($item in $Uninstall) {
        $names += $item.Split(',') | ForEach-Object { $_.Trim() }
    }
    if ($names -contains "all") {
        $names = $AvailableSkills.Keys
    }
    foreach ($n in $names) {
        if ($n) { Uninstall-Skill -Name $n }
    }
    Show-Status
}
