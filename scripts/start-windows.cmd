@echo off
setlocal

set ROOT_DIR=%~dp0..
pushd %ROOT_DIR%

docker compose up --build -d
if errorlevel 1 (
  popd
  exit /b 1
)

popd
exit /b 0
