# TODO Currently only for Make running under cygwin on windows
# Need to add support for more platforms

FFMPEG_WIN64 = https://ffmpeg.zeranoe.com/builds/win64/static/ffmpeg-20190601-4158865-win64-static.zip

EXE_NAME = frycook.exe
SRC = frycook.py

# Copies the first dependency to the target.
define copy_file
	mkdir -p $(@D)
	cp $< $@
endef

.PHONY: all clean cleanall exe installdeps

all: dist/frycook.zip

clean:
	rm -rf dist
	rm -rf build
	rm -rf __pycache__
	rm -f frycook.spec

realclean: clean
	rm -rf dl
	rm -rf ffmpeg
	rm -f ffmpeg.stamp

# Install the dependencies for frycook
installdeps:
	pip install --progress-bar off pyinstaller
	pip install --progress-bar off ffmpeg-python
	pip install --progress-bar off pillow
	pip install --progress-bar off wxpython

# Downloads ffmpeg for windows. This is required for the script version
# to work. The packaging target will run this automatically.
ffmpeg.stamp:
	mkdir -p dl
	curl $(FFMPEG_WIN64) > dl/dl_ffmpeg64.zip
	(cd dl && unzip dl_ffmpeg64.zip)
	mv dl/ffmpeg* ffmpeg
	touch $@

exe: dist/$(EXE_NAME)

dist/$(EXE_NAME): $(SRC) icon.ico
	pyinstaller --add-data 'icon.ico;.' -w -i icon.ico --onefile frycook.py

# ffmpeg dist files
ffmpeg/README.txt ffmpeg/LICENSE.txt ffmpeg/bin/ffmpeg.exe: ffmpeg.stamp

dist/frycook/ffmpeg/README.txt: ffmpeg/README.txt
	$(copy_file)

dist/frycook/ffmpeg/LICENSE.txt: ffmpeg/LICENSE.txt
	$(copy_file)

dist/frycook/ffmpeg/bin/ffmpeg.exe: ffmpeg/bin/ffmpeg.exe
	$(copy_file)

# Own dist files
dist/frycook/LICENSE: LICENSE
	$(copy_file)

dist/frycook/$(EXE_NAME): dist/$(EXE_NAME)
	$(copy_file)

dist/frycook/README.md: README.md
	$(copy_file)

dist/frycook.zip: \
  dist/frycook/LICENSE \
  dist/frycook/$(EXE_NAME) \
  dist/frycook/README.md \
  dist/frycook/ffmpeg/README.txt \
  dist/frycook/ffmpeg/LICENSE.txt \
  dist/frycook/ffmpeg/bin/ffmpeg.exe
	rm -f $@
	(cd dist && zip -r - frycook) > $@
