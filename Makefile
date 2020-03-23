# TODO Currently only for Make running under cygwin on windows
# Need to add support for more platforms

EXE_NAME = frycook.exe
SRC = frycook.py

# Copies the first dependency to the target.
define copy_file
	mkdir -p $(@D)
	cp $< $@
endef

.PHONY: all clean exe

all: dist/frycook.zip

clean:
	rm -rf dist
	rm -rf build
	rm -rf __pycache__
	rm frycook.spec

exe: dist/$(EXE_NAME)

dist/$(EXE_NAME): $(SRC) icon.ico
	pyinstaller --add-data 'icon.ico;.' -w -i icon.ico --onefile frycook.py

dist/frycook/LICENSE: LICENSE
	$(copy_file)

dist/frycook/$(EXE_NAME): dist/$(EXE_NAME)
	$(copy_file)

dist/frycook/README.md: README.md
	$(copy_file)

dist/frycook.zip: \
  dist/frycook/LICENSE \
  dist/frycook/$(EXE_NAME) \
  dist/frycook/README.md
	rm -f $@
	(cd dist && zip -r - frycook) > $@
