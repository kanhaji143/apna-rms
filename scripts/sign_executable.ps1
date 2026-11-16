# scripts/sign_executable.ps1
# Generates a persistent Code Signing Certificate for APNA Computer Institute
# and digitally signs APNA_Computer_RMS_Setup.exe and exports the public certificate

$certSubject = "CN=APNA Computer Institute, O=APNA Computer, OU=Software Development, C=IN"
$existing = Get-ChildItem -Path Cert:\CurrentUser\My | Where-Object { $_.Subject -like "*APNA Computer Institute*" } | Select-Object -First 1

if (-not $existing) {
    Write-Host "Creating new Code Signing Certificate..."
    $cert = New-SelfSignedCertificate -Type CodeSigningCert `
        -Subject $certSubject `
        -CertStoreLocation "Cert:\CurrentUser\My" `
        -NotAfter (Get-Date).AddYears(10) `
        -FriendlyName "APNA Computer Institute Authenticode Certificate" `
        -KeyUsage DigitalSignature `
        -TextExtension @("2.5.29.37={text}1.3.6.1.5.5.7.3.3")
} else {
    Write-Host "Using existing certificate: $($existing.Thumbprint)"
    $cert = $existing
}

# Digitally sign the Setup executable
$targetExe = "dist\APNA_Computer_RMS_Setup.exe"
if (Test-Path $targetExe) {
    Write-Host "Signing $targetExe with Authenticode signature..."
    $sig = Set-AuthenticodeSignature -FilePath $targetExe -Certificate $cert -HashAlgorithm SHA256
    Write-Host "Status: $($sig.Status)"
    Write-Host "StatusMessage: $($sig.StatusMessage)"
} else {
    Write-Host "Warning: $targetExe not found!"
}

# Verify Signature
$check = Get-AuthenticodeSignature -FilePath $targetExe
Write-Host "Verification Subject: $($check.SignerCertificate.Subject)"
Write-Host "Verification Thumbprint: $($check.SignerCertificate.Thumbprint)"
