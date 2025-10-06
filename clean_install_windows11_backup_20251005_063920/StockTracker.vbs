' Stock Tracker Silent Launcher
' This VBScript launches the batch file without showing the command window initially
' Save this on your Desktop for a cleaner startup experience

Set WshShell = CreateObject("WScript.Shell")

' Show startup message
MsgBox "Starting Complete Stock Tracker..." & vbCrLf & vbCrLf & _
       "The browser will open automatically at:" & vbCrLf & _
       "http://localhost:8002", vbInformation, "Stock Tracker"

' Change to the correct directory and run the Python script
WshShell.CurrentDirectory = "C:\StockTrack\Complete_Stock_Tracker_Windows11"

' Run the backend (visible so you can see any errors)
WshShell.Run "cmd /k python backend.py", 1, False

' Wait 3 seconds then open browser
WScript.Sleep 3000
WshShell.Run "http://localhost:8002", 1, False