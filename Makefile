# TODO Currently only for Make running under cygwin on windows
# Need to add support for more platforms

all: dist/frycook.exe

clean:
	rm -rf dist
	rm -rf build
	rm -rf __pycache__
	rm frycook.spec

dist/frycook.exe:
	rm -rf dist
	pyinstaller --add-data 'icon.ico;.' -w -i icon.ico --onefile frycook.py
