# Creates a "Job Search Ledger" shortcut on your desktop that runs launch.bat without a console flash.
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
$shell = New-Object -ComObject WScript.Shell
$lnk = $shell.CreateShortcut([Environment]::GetFolderPath("Desktop") + "\Job Search Ledger.lnk")
$lnk.TargetPath = Join-Path $here "launch.bat"
$lnk.WorkingDirectory = $here
$lnk.WindowStyle = 7
$icon = Join-Path $here "assets\ledger.ico"
if (Test-Path $icon) { $lnk.IconLocation = $icon }
$lnk.Save()
Write-Host "Shortcut created on the desktop."
