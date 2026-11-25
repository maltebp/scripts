$path = 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Themes\Personalize'
$newValue = 1 - (Get-ItemPropertyValue $path AppsUseLightTheme)
Set-ItemProperty $path AppsUseLightTheme $newValue
Set-ItemProperty $path SystemUsesLightTheme $newValue

Add-Type -Namespace Win32 -Name NativeMethods -MemberDefinition @'
[DllImport("user32.dll", CharSet = CharSet.Unicode)]
public static extern IntPtr SendMessageTimeout(IntPtr hWnd, uint msg, UIntPtr wParam, string lParam, uint flags, uint timeout, out UIntPtr result);
'@
# HWND_BROADCAST = 0xFFFF, WM_SETTINGCHANGE = 0x1A, SMTO_ABORTIFHUNG = 2
[Win32.NativeMethods]::SendMessageTimeout([IntPtr]0xFFFF, 0x1A, [UIntPtr]::Zero, 'ImmersiveColorSet', 2, 5000, [ref][UIntPtr]::Zero) | Out-Null