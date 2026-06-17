#!/usr/bin/env pwsh
# build_wasm.ps1 - Build the forge_simulation WebAssembly engine
#
# Prerequisites:
#   1. Rust toolchain: https://rustup.rs
#   2. WASM target:    rustup target add wasm32-unknown-unknown
#   3. wasm-pack:      cargo install wasm-pack
#
# Usage:
#   ./build_wasm.ps1              # release build
#   ./build_wasm.ps1 --dev        # development build (unoptimized)

param(
    [switch]$Dev
)

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$ProjectRoot = Split-Path -Parent $ScriptDir
$WasmEngineDir = Join-Path $ProjectRoot "wasm_engine"
$WasmPkgDir = Join-Path $ProjectRoot "wasm_pkg"

Write-Host "=== Project Forge 2D - WASM Engine Build ===" -ForegroundColor Cyan

# Verify prerequisites
foreach ($tool in @("rustc", "cargo", "wasm-pack")) {
    $cmd = Get-Command $tool -ErrorAction SilentlyContinue
    if (-not $cmd) {
        Write-Error "Required tool '$tool' not found. See prerequisites above."
        exit 1
    }
    Write-Host "  ✓ $tool found: $(& $tool --version 2>&1 | Select-Object -First 1)" -ForegroundColor Green
}

# Build
Set-Location $WasmEngineDir

if ($Dev) {
    Write-Host "`n[BUILD] Development mode (no optimizations)..." -ForegroundColor Yellow
    wasm-pack build --target web --dev --out-dir $WasmPkgDir
} else {
    Write-Host "`n[BUILD] Release mode (optimized for size)..." -ForegroundColor Yellow
    wasm-pack build --target web --release --out-dir $WasmPkgDir
}

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n=== Build Successful ===" -ForegroundColor Green
    Write-Host "Output: $WasmPkgDir" -ForegroundColor Green
    Write-Host ""
    Write-Host "To integrate in game.js, add before the <script> tags:" -ForegroundColor Cyan
    Write-Host '  <script type="module">' -ForegroundColor White
    Write-Host "    import init, { simulate, reset_rng } from './wasm_pkg/forge_simulation.js';" -ForegroundColor White
    Write-Host "    await init();" -ForegroundColor White
    Write-Host "    // replace simulate() calls with the WASM version" -ForegroundColor White
    Write-Host '  </script>' -ForegroundColor White
} else {
    Write-Error "Build failed with exit code $LASTEXITCODE"
    exit $LASTEXITCODE
}
