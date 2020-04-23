@ECHO OFF
SET PATH=%PATH%;C:\Program Files\Python38;C:\Program Files\Python38\scripts

FOR /F "tokens=* USEBACKQ" %%F IN (`python get_version.py`) do (
    SET VERSION=%%F
)

if "%1" == "" goto help

if "%1" == "help" (
    :help
    echo.Please use `make ^<target^>` where ^<target^> is one of
    echo.   init        to get things going
    echo.   test        run the test suite
    echo.   clean       clean everything up
    goto end
)

if "%1" == "init" (
    :init
    echo.Initializing...
    call :pip_install_tools
    call :pip_install_dev
    call :pip_install
    call :pipenv_install
)

if "%1" == "clean" (
    :clean
    echo.Cleaning...
    call :pipenv_clean
    call :pip_install
)

if "%1" == "pipenv_clean" (
    :pipenv_clean
    pipenv --rm
    echo.Virtual environment removed
    goto end
)

if "%1" == "pipenv_install" (
    :pipenv_install
    pipenv install --dev --skip-lock
    echo.Virtual environment installed
    goto end
)


if "%1" == "pip_install_tools" (
    :pip_install_tools
    python -m pip install --quiet --upgrade --requirement requirements-pkg.txt
    echo.Packaging requirements installed
    goto end
)

if "%1" == "pip_install_dev" (
    :pip_install_dev
    python -m pip install --quiet --upgrade --requirement requirements-dev.txt
    echo.Developement requirements installed
    goto end
)

if "%1" == "pip_install" (
    :pip_install
    python -m pip install --quiet --upgrade --requirement requirements.txt
    echo.Package requirements installed
    goto end
)

if "%1" == "test" (
    :test
    pipenv run pytest -vv --showlocals --exitfirst --last-failed --pdb axonius_api_client/tests
    goto end
)

:end
