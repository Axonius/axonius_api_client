@ECHO OFF

FOR /F "tokens=* USEBACKQ" %%F IN (`python get_version.py`) do (
    SET VERSION=%%F
)
FOR /F "tokens=* USEBACKQ" %%F IN (`pyenv version`) do (
    SET PYTHON_VERSION=%%F
)
SET CMD=%1
echo.Hello, version=%VERSION%, cmd=%CMD%, python version=%PYTHON_VERSION%

if "%CMD%" == "" goto :HELP
if "%CMD%" == "help" goto :HELP
if "%CMD%" == "init" goto :INIT
if "%CMD%" == "clean" goto :CLEAN
if "%CMD%" == "pipenv_remove" goto :PIPENV_REMOVE
if "%CMD%" == "pipenv_install" goto :PIPENV_INSTALL
if "%CMD%" == "pip_install_dev" goto :PIP_INSTALL_DEV
if "%CMD%" == "pip_install" goto :PIP_INSTALL
if "%CMD%" == "test" goto :TEST

:FILES_CLEAN_CMD
echo.Removing files
rmdir /s /q artifacts
echo.Removed files
goto :END

:PIPENV_REMOVE_CMD
echo.Removing Virtual environment
call pipenv --rm
echo.Virtual environment removed
goto :END

:PIPENV_INSTALL_CMD
echo.Installing Virtual environment
call pipenv install --dev --skip-lock
echo.Virtual environment installed
goto :END

:PIP_INSTALL_CMD
echo.Installing requirements
call python -m pip install --upgrade --requirement requirements.txt
echo.Requirements installed
goto :END

:PIP_INSTALL_DEV_CMD
echo.Installing developement requirements
call python -m pip install --upgrade --requirement requirements-pkg.txt
call python -m pip install --upgrade --requirement requirements-dev.txt
call python -m pip install --upgrade --requirement requirements-build.txt
call python -m pip install --upgrade --requirement requirements-lint.txt
echo.Developement requirements installed
goto :END

:TEST_CMD
echo.Starting tests
call pytest
echo.Tests finished
goto :END

:CLEAN_CMD
echo.Cleaning...
call :PIPENV_REMOVE_CMD
call :FILES_CLEAN_CMD
echo.Cleaning done
goto :END

:INIT
echo.Initializing...
call :PIP_INSTALL_CMD
call :PIP_INSTALL_DEV_CMD
call :PIPENV_INSTALL_CMD
echo.Initialized
goto :BYE

:HELP
echo.Please use `make ^<target^>` where ^<target^> is one of
echo.   init        to get things going
echo.   test        run the test suite
echo.   clean       clean everything up
goto :BYE

:CLEAN
call :CLEAN_CMD
goto :BYE

:FILES_CLEAN
call :FILES_CLEAN_CMD
goto :BYE

:PIPENV_REMOVE
call :PIPENV_REMOVE_CMD
goto :BYE

:PIPENV_INSTALL
call :PIPENV_INSTALL_CMD
goto :BYE

:PIP_INSTALL
call :PIP_INSTALL_CMD
goto :BYE

:PIP_INSTALL_DEV
call :PIP_INSTALL_DEV_CMD
goto :BYE

:TEST
call :TEST_CMD
goto :BYE

:BYE
echo.Goodbye, version=%VERSION%, cmd=%CMD%, python version=%PYTHON_VERSION%
goto :END

:END
