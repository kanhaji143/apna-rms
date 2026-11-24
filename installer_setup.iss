; Script generated for APNA Computer RMS
; Professional Inno Setup Installer Script (Industry Standard)

#define MyAppName "APNA Computer RMS"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "APNA Computer Institute"
#define MyAppURL "https://github.com/kanhaji143/apna-rms"
#define MyAppExeName "APNA_Computer_RMS.exe"

[Setup]
; Basic Application Details
AppId={{5D8E6F3A-8B12-4C90-A6E5-3A9D1C2E8F47}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
AppComments=Helpline: 8504985149 | Email: krishnaskb143@gmail.com | Developed by Krishna ji
AppContact=8504985149
AppCopyright=Copyright (C) 2026 APNA Computer (Helpline: 8504985149). All rights reserved.
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
AllowNoIcons=yes
OutputDir=dist
OutputBaseFilename=APNA_Computer_RMS_Setup
SetupIconFile=app_icon.ico
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
PrivilegesRequiredOverridesAllowed=commandline dialog
UninstallDisplayIcon={app}\{#MyAppExeName}
DisableProgramGroupPage=yes
CloseApplications=yes
CloseApplicationsFilter=*.exe

; Windows File Properties -> Details Tab Metadata
VersionInfoVersion=1.0.0.0
VersionInfoTextVersion=1.0.0.0
VersionInfoProductVersion=1.0.0.0
VersionInfoProductTextVersion=1.0.0.0
VersionInfoCompany=APNA Computer (Helpline: 8504985149)
VersionInfoDescription=APNA Computer RMS Setup - Institute Management Software (Helpline: 8504985149)
VersionInfoCopyright=Copyright (C) 2026 APNA Computer (Helpline: 8504985149). All rights reserved.
VersionInfoProductName=APNA Computer RMS
VersionInfoOriginalFileName=APNA_Computer_RMS_Setup.exe

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"

[Files]
; Main Executable and Internals
Source: "build\app_binaries\APNA_Computer_RMS_Portable.exe"; DestDir: "{app}"; DestName: "APNA_Computer_RMS.exe"; Flags: ignoreversion
Source: "build\app_binaries\_internal\*"; DestDir: "{app}\_internal"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "app_config.json"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\Documentation\LOGIN_DETAILS.txt"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\Documentation\SYSTEM_RULEBOOK_AND_TROUBLESHOOTING.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\Documentation\SYSTEM_RULEBOOK_AND_TROUBLESHOOTING.pdf"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\Documentation\ANTIVIRUS_AND_CLIENT_DEPLOYMENT_GUIDE.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\Documentation\APNA_Computer_RMS_Training_Manual.pdf"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\Documentation\APNA_Computer_RMS_Sales_Pitch_Guide.pdf"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\Documentation\APNA_Computer_RMS_Development_Chat_History.pdf"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\{#MyAppExeName}"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon; IconFilename: "{app}\{#MyAppExeName}"

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent
