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
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
AllowNoIcons=yes
OutputDir=dist
OutputBaseFilename=APNA_Computer_RMS_Setup
SetupIconFile=app_icon.ico
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
PrivilegesRequiredOverridesAllowed=dialog
UninstallDisplayIcon={app}\{#MyAppExeName}
DisableProgramGroupPage=yes

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
; Main Executable and Internals
Source: "build\app_binaries\APNA_Computer_RMS_Portable.exe"; DestDir: "{app}"; DestName: "APNA_Computer_RMS.exe"; Flags: ignoreversion
Source: "build\app_binaries\_internal\*"; DestDir: "{app}\_internal"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "app_config.json"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\Documentation\LOGIN_DETAILS.txt"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\Documentation\SYSTEM_RULEBOOK_AND_TROUBLESHOOTING.md"; DestDir: "{app}"; Flags: ignoreversion
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
