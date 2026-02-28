@echo off
setlocal

set ROOT_DIR=%~dp0..
pushd %ROOT_DIR%

docker compose down
if errorlevel 1 (
  popd
  exit /b 1
)

popd
exit /b 0
