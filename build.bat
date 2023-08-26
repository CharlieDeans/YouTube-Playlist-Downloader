pip install -r requirements_for_build.txt
del get_videos.exe
mkdir BUILD
copy get_videos.py BUILD\get_videos_build.py
cd BUILD
pyinstaller --onefile get_videos_build.py
copy dist\get_videos_build.exe ..\get_videos.exe
cd ..
rmdir /s /q BUILD