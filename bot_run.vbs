Set WshShell = CreateObject("WScript.Shell")

WshShell.Run "taskkill /f /im python.exe"

WScript.Sleep 3000 'Sleeps for 10 seconds
WshShell.Run chr(34) & "bot_run.bat" & Chr(34), 0
Set WshShell = Nothing