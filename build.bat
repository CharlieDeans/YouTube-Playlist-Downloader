pip install -r requirements_for_build.txt
mkdir BUILD
copy get_videos.py BUILD\get_videos_build.txt

@REM THIS IS NOT MY CODE, THIS CODE WAS PROVIDED IN AN ANSWER BY USER "aschipfl" ON STACKOVERFLOW
@REM https://stackoverflow.com/questions/59173695/insert-text-at-a-particular-line-number-in-a-text-file-using-batch-script
setlocal EnableExtensions DisableDelayedExpansion

set "_FILE=get_videos_build.txt" & rem // (text file to insert a line of text into)
set "_TEXT=os.system('pip install selenium==4.11.2 webdriver-manager==4.0.0 pytube==15.0.0 moviepy==1.0.3')" & rem // (text of the inserted line)
set /A "_NUM=15"   & rem // (number of the line where the new line is inserted)
set "_REPLAC=#"   & rem // (set to anything to replace the target line, or to nothing to keep it)
set "_TMPF=%TEMP%\%~n0_%RANDOM%.tmp" & rem // (path and name of temporary file)

rem // Write result into temporary file:
> "%_TMPF%" (
    rem // Loop through all lines of the text file, each with a preceding line number:
    for /F "delims=" %%L in ('findstr /N "^" "%_FILE%"') do (
        rem // Store current line including preceding line number to a variable:
        set "LINE=%%L"
        rem // Set the current line number to another variable:
        set /A "LNUM=%%L"
        rem // Toggle delayed expansion to avoid trouble with `!`:
        setlocal EnableDelayedExpansion
        rem // Compare current line number with predefined one:
        if !LMUN! equ %_NUM% (
            rem // Line numbers match, so return extra line of text:
            echo(!_TEXT!
            rem // Return original line (without preceding line number) only if it is not to be replaced:
            if not defined _REPLAC echo(!LINE:*:=!
        ) else (
            rem // Line numbers do not match, so return original line (without preceding line number) anyway:
            echo(!LINE:*:=!
        )
        endlocal
    )
)
rem // Move temporary file onto original one:
move /Y "%_TMPF%" "%_FILE%"

cd BUILD
copy get_videos_build.txt get_videos_build.py
del get_videos_build.txt
pyinstaller --onefile get_videos_build.py
copy dist\get_videos_build.exe ..\get_videos.exe
cd ..
del get_videos_build.txt
rmdir /s /q BUILD

endlocal
exit /B