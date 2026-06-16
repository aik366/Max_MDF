Set WshShell = CreateObject("WScript.Shell")


WScript.Sleep 20000 'Sleeps for 20 seconds
WshShell.Run chr(34) & "bot_run.bat" & Chr(34), 0
Set WshShell = Nothing