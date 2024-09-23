[Setup]
AppName=SILA
AppVersion=1.0
DefaultDirName={commonpf}\SILA
DefaultGroupName=SILA
OutputBaseFilename=SILA_Setup
SetupIconFile=C:\Users\negro\Desktop\SILA\icon.ico
Compression=lzma2
SolidCompression=yes

[Files]
Source: "C:\Users\negro\Desktop\SILA\SILA.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\Users\negro\Desktop\SILA\nircmd.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\Users\negro\Desktop\SILA\nircmdc.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\Users\negro\Desktop\SILA\NirCmd.chm"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\Users\negro\Desktop\SILA\icon.png"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\Users\negro\Desktop\SILA\terms.txt"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\Users\negro\Desktop\SILA\build\*"; DestDir: "{app}\build"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\SILA"; Filename: "{app}\SILA.exe"; Tasks: create_shortcut
Name: "{commondesktop}\SILA"; Filename: "{app}\SILA.exe"; Tasks: create_shortcut

[Tasks]
Name: "create_shortcut"; Description: "Crear acceso directo en el escritorio"; GroupDescription: "Opciones de acceso directo"; Flags: exclusive
Name: "run_program"; Description: "Ejecutar SILA después de la instalación"; GroupDescription: "Opciones de ejecución"; Flags: exclusive

[Code]
function PrepareToInstall(var Cancel: Boolean): String;
begin
  // Aquí podrías verificar si es necesario aceptar términos y condiciones
  // Por ahora, vamos a omitir esa funcionalidad para simplificar
  Result := ''; // No hay errores
end;