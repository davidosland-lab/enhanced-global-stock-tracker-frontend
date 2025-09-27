; Stock Predictor Pro - NSIS Installer Script
; Creates Windows installer for the application

;--------------------------------
; Includes

!include "MUI2.nsh"
!include "LogicLib.nsh"
!include "WinVer.nsh"
!include "x64.nsh"

;--------------------------------
; General

; Name and file
Name "Stock Predictor Pro"
OutFile "StockPredictorPro_Setup_v1.0.0.exe"

; Default installation folder
InstallDir "$PROGRAMFILES64\StockPredictorPro"

; Get installation folder from registry if available
InstallDirRegKey HKLM "Software\StockPredictorPro" "InstallDir"

; Request admin privileges
RequestExecutionLevel admin

; Show details
ShowInstDetails show
ShowUnInstDetails show

;--------------------------------
; Version Information

VIProductVersion "1.0.0.0"
VIAddVersionKey "ProductName" "Stock Predictor Pro"
VIAddVersionKey "CompanyName" "Stock Predictor Team"
VIAddVersionKey "LegalCopyright" "Copyright © 2024"
VIAddVersionKey "FileDescription" "AI-Powered Stock Prediction System"
VIAddVersionKey "FileVersion" "1.0.0"

;--------------------------------
; Interface Settings

!define MUI_ABORTWARNING
!define MUI_ICON "assets\icon.ico"
!define MUI_UNICON "assets\icon.ico"
!define MUI_HEADERIMAGE
!define MUI_HEADERIMAGE_BITMAP "assets\header.bmp"
!define MUI_WELCOMEFINISHPAGE_BITMAP "assets\welcome.bmp"

;--------------------------------
; Pages

; Welcome page
!insertmacro MUI_PAGE_WELCOME

; License page
!insertmacro MUI_PAGE_LICENSE "LICENSE"

; Components page
!insertmacro MUI_PAGE_COMPONENTS

; Directory page
!insertmacro MUI_PAGE_DIRECTORY

; Install files page
!insertmacro MUI_PAGE_INSTFILES

; Finish page
!define MUI_FINISHPAGE_RUN "$INSTDIR\StockPredictorPro.exe"
!define MUI_FINISHPAGE_RUN_TEXT "Launch Stock Predictor Pro"
!define MUI_FINISHPAGE_SHOWREADME "$INSTDIR\README.md"
!insertmacro MUI_PAGE_FINISH

; Uninstaller pages
!insertmacro MUI_UNPAGE_WELCOME
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_UNPAGE_FINISH

;--------------------------------
; Languages

!insertmacro MUI_LANGUAGE "English"

;--------------------------------
; Installer Sections

Section "Stock Predictor Pro (Required)" SecCore
    SectionIn RO
    
    ; Set output path to installation directory
    SetOutPath "$INSTDIR"
    
    ; Check Windows version
    ${If} ${IsWin10}
    ${OrIf} ${IsWin11}
        ; Continue installation
    ${Else}
        MessageBox MB_OK|MB_ICONEXCLAMATION "Stock Predictor Pro requires Windows 10 or Windows 11."
        Abort
    ${EndIf}
    
    ; Check for Python
    ReadRegStr $0 HKLM "SOFTWARE\Python\PythonCore\3.9\InstallPath" ""
    ${If} $0 == ""
        ReadRegStr $0 HKLM "SOFTWARE\Python\PythonCore\3.10\InstallPath" ""
        ${If} $0 == ""
            ReadRegStr $0 HKLM "SOFTWARE\Python\PythonCore\3.11\InstallPath" ""
            ${If} $0 == ""
                MessageBox MB_YESNO "Python 3.9+ is required but not found. Download and install Python?" IDYES InstallPython IDNO SkipPython
                InstallPython:
                    ExecShell "open" "https://www.python.org/downloads/"
                    MessageBox MB_OK "Please install Python 3.9+ and run this installer again."
                    Abort
                SkipPython:
                    ; Continue anyway
            ${EndIf}
        ${EndIf}
    ${EndIf}
    
    ; Copy application files
    File /r "dist\*.*"
    
    ; Create application directories
    CreateDirectory "$INSTDIR\models"
    CreateDirectory "$INSTDIR\data"
    CreateDirectory "$INSTDIR\logs"
    CreateDirectory "$INSTDIR\config"
    
    ; Write installation info to registry
    WriteRegStr HKLM "Software\StockPredictorPro" "InstallDir" "$INSTDIR"
    WriteRegStr HKLM "Software\StockPredictorPro" "Version" "1.0.0"
    
    ; Create uninstaller
    WriteUninstaller "$INSTDIR\Uninstall.exe"
    
    ; Register uninstaller with Windows
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\StockPredictorPro" \
                     "DisplayName" "Stock Predictor Pro"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\StockPredictorPro" \
                     "UninstallString" "$INSTDIR\Uninstall.exe"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\StockPredictorPro" \
                     "DisplayIcon" "$INSTDIR\StockPredictorPro.exe"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\StockPredictorPro" \
                     "Publisher" "Stock Predictor Team"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\StockPredictorPro" \
                     "DisplayVersion" "1.0.0"
    WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\StockPredictorPro" \
                      "NoModify" 1
    WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\StockPredictorPro" \
                      "NoRepair" 1
    
SectionEnd

Section "Desktop Shortcut" SecDesktop
    CreateShortCut "$DESKTOP\Stock Predictor Pro.lnk" "$INSTDIR\StockPredictorPro.exe"
SectionEnd

Section "Start Menu Shortcuts" SecStartMenu
    CreateDirectory "$SMPROGRAMS\Stock Predictor Pro"
    CreateShortCut "$SMPROGRAMS\Stock Predictor Pro\Stock Predictor Pro.lnk" "$INSTDIR\StockPredictorPro.exe"
    CreateShortCut "$SMPROGRAMS\Stock Predictor Pro\README.lnk" "$INSTDIR\README.md"
    CreateShortCut "$SMPROGRAMS\Stock Predictor Pro\Uninstall.lnk" "$INSTDIR\Uninstall.exe"
SectionEnd

Section "Python Dependencies" SecDeps
    ; Install Python dependencies
    DetailPrint "Installing Python dependencies..."
    ExecWait '"$INSTDIR\install_deps.bat"' $0
    ${If} $0 != 0
        MessageBox MB_OK|MB_ICONEXCLAMATION "Some dependencies failed to install. Please run install_deps.bat manually."
    ${EndIf}
SectionEnd

Section "Sample Data" SecData
    ; Copy sample data files
    SetOutPath "$INSTDIR\data"
    File /r "sample_data\*.*"
SectionEnd

Section "Pre-trained Models" SecModels
    ; Copy pre-trained models
    SetOutPath "$INSTDIR\models"
    File /r "pretrained_models\*.*"
SectionEnd

;--------------------------------
; Section Descriptions

!insertmacro MUI_FUNCTION_DESCRIPTION_BEGIN
    !insertmacro MUI_DESCRIPTION_TEXT ${SecCore} "Core application files (required)"
    !insertmacro MUI_DESCRIPTION_TEXT ${SecDesktop} "Create desktop shortcut"
    !insertmacro MUI_DESCRIPTION_TEXT ${SecStartMenu} "Create Start Menu shortcuts"
    !insertmacro MUI_DESCRIPTION_TEXT ${SecDeps} "Install Python dependencies automatically"
    !insertmacro MUI_DESCRIPTION_TEXT ${SecData} "Sample market data for testing"
    !insertmacro MUI_DESCRIPTION_TEXT ${SecModels} "Pre-trained AI models for immediate use"
!insertmacro MUI_FUNCTION_DESCRIPTION_END

;--------------------------------
; Uninstaller Section

Section "Uninstall"
    
    ; Delete application files
    Delete "$INSTDIR\StockPredictorPro.exe"
    Delete "$INSTDIR\Uninstall.exe"
    Delete "$INSTDIR\README.md"
    Delete "$INSTDIR\LICENSE"
    Delete "$INSTDIR\requirements.txt"
    Delete "$INSTDIR\config.json"
    
    ; Delete directories
    RMDir /r "$INSTDIR\models"
    RMDir /r "$INSTDIR\data"
    RMDir /r "$INSTDIR\logs"
    RMDir /r "$INSTDIR\config"
    RMDir /r "$INSTDIR\__pycache__"
    
    ; Remove installation directory
    RMDir "$INSTDIR"
    
    ; Delete shortcuts
    Delete "$DESKTOP\Stock Predictor Pro.lnk"
    Delete "$SMPROGRAMS\Stock Predictor Pro\*.lnk"
    RMDir "$SMPROGRAMS\Stock Predictor Pro"
    
    ; Delete registry keys
    DeleteRegKey HKLM "Software\StockPredictorPro"
    DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\StockPredictorPro"
    
    ; Ask about user data
    MessageBox MB_YESNO "Delete user data and settings from %APPDATA%\StockPredictorPro?" IDNO SkipUserData
        RMDir /r "$APPDATA\StockPredictorPro"
    SkipUserData:
    
SectionEnd