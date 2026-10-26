<#
.SYNOPSIS
    安装个人 Agent Skills。用户级用链接，项目级用拷贝。

.DESCRIPTION
    不带 -Project 时，在 ~/.agents/skills 建立指向本仓库的符号链接（Windows 上为 Junction）。
    带 -Project 时，把技能目录复制到该仓库的 .agents/skills/<技能名>/。
    实现在 scripts/install.mjs，本脚本只转发参数。

.PARAMETER List
    查看技能及当前安装状态。

.PARAMETER Install
    安装一个或多个技能（逗号分隔或数组）。all 表示全部。

.PARAMETER Uninstall
    卸载一个或多个技能。all 表示全部。

.PARAMETER Project
    可选。指定项目根目录后改为拷贝安装。不指定则安装到用户级。

.EXAMPLE
    .\manage-skills.ps1 -List
    .\manage-skills.ps1 -Install all
    .\manage-skills.ps1 -Install clarify-decisions,tdd
    .\manage-skills.ps1 -Install tdd -Project "D:\wiki\project\spec-anchor"
    .\manage-skills.ps1 -Uninstall tdd -Project "D:\wiki\project\spec-anchor"
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

$Installer = Join-Path $PSScriptRoot "scripts\install.mjs"
if (-not (Get-Command node -ErrorAction SilentlyContinue)) {
    Write-Error "未找到 node。需要 Node.js 18 或更高版本。"
    exit 1
}

$nodeArgs = @($Installer)
if ($PSCmdlet.ParameterSetName -eq "List") {
    $nodeArgs += "--list"
}
if ($Project) {
    $nodeArgs += @("--project", $Project)
} elseif ($PSCmdlet.ParameterSetName -ne "List") {
    $nodeArgs += "--user"
}
if ($PSCmdlet.ParameterSetName -eq "Install") {
    $nodeArgs += @("--install", (($Install | ForEach-Object { $_.Trim() }) -join ","))
}
if ($PSCmdlet.ParameterSetName -eq "Uninstall") {
    $nodeArgs += "--uninstall"
    $nodeArgs += @("--install", (($Uninstall | ForEach-Object { $_.Trim() }) -join ","))
}

& node @nodeArgs
exit $LASTEXITCODE
