#!/bin/env python3

from PIL import Image, ImageEnhance, ImageSequence
import io
import os
import sys
import wx

from pathlib import Path


if hasattr(sys, "_MEIPASS"):
    DATADIR = Path(sys._MEIPASS)
else:
    DATADIR = Path(os.path.dirname(os.path.realpath(__file__)))


class ImageFryerSettings:
    def __init__(self):
        self.jpeg_quality = 1
        self.saturation = 8


def get_fried_save_location(path, suffix):
    save_directory = path.parent
    save_location = save_directory / ("deepfried_" + path.suffix[1:] + "_" +
                                      path.stem + suffix)

    print("convert " + str(path))
    print("save to " + str(save_location))

    return save_location


# Fry a single PIL image and save it somewhere
def fry_single_image(img, save_location, *, saturation, jpeg_quality):
    img = img.convert("RGB")
    img = ImageEnhance.Color(img).enhance(saturation)

    img.save(save_location, "JPEG", quality=jpeg_quality)


class StillImageFryer:
    def __init__(self, settings):
        self.settings = settings

    def fry(self, path):
        s = self.settings
        save_location = get_fried_save_location(path, ".jpg")

        img = Image.open(path)
        fry_single_image(img, save_location,
                         saturation=s.saturation,
                         jpeg_quality=s.jpeg_quality)

    def is_file_supported(self, path):
        return path.suffix.lower() in [".png", ".jpg", ".jpeg", ".bmp"]


class GifFryer:
    def __init__(self, settings):
        self.settings = settings

    # Get gif info we should save with based on the original gif parameters
    def get_gif_args(self, gif_info):
        gif_save_args = {
            "optimize": False,
            "duration": gif_info["duration"],
            "loop": 0
        }

        gif_transparency = gif_info.get("transparency", None)
        if gif_transparency is not None:
            gif_save_args["transparency"] = gif_transparency

        return gif_save_args

    # Fry a single frame of the gif, based on our settings
    def fry_frame(self, img):
        frame_buf = io.BytesIO()
        s = self.settings

        fry_single_image(img, frame_buf,
                         saturation=s.saturation,
                         jpeg_quality=s.jpeg_quality)

        frame_buf.seek(0)
        return Image.open(frame_buf)

    def fry(self, path):
        save_location = get_fried_save_location(path, ".gif")

        img = Image.open(path)

        gif_save_args = self.get_gif_args(img.info)
        fried_frames = [self.fry_frame(i) for i in ImageSequence.Iterator(img)]

        fried_frames[0].save(save_location, "GIF", save_all=True,
                             append_images=fried_frames[1:], **gif_save_args)

    def is_file_supported(self, path):
        return path.suffix.lower() == ".gif"


class FryTarget(wx.FileDropTarget):
    def __init__(self, fryers):
        super().__init__()
        self.fryers = fryers

    def get_fryer(self, path):
        for fryer in self.fryers:
            if fryer.is_file_supported(path):
                return fryer

        return None

    def OnDropFiles(self, x, y, filenames):
        for filename in filenames:
            fryer = self.get_fryer(Path(filename))

            if not fryer:
                continue

            fryer.fry(Path(filename))

        return True


class ConvertPanel(wx.Panel):
    def __init__(self, parent, *fryers):
        super().__init__(parent)

        self.SetDropTarget(FryTarget(fryers))

        drop_text = wx.StaticText(self, label="Drag and Drop Files")
        drop_text_font = drop_text.GetFont()
        drop_text_font.SetPointSize(32)
        drop_text_font.SetFamily(wx.FONTFAMILY_MODERN)
        drop_text_font = drop_text_font.Bold()
        drop_text.SetFont(drop_text_font)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.AddStretchSpacer()
        sizer.Add(drop_text, 0, wx.CENTER)
        sizer.AddStretchSpacer()
        self.SetSizer(sizer)


class ConvertSettingsPanel(wx.Panel):
    def __init__(self, parent, fryer):
        super().__init__(parent)

        self.settings = fryer.settings

        # Set up settings widgets
        jpeg_quality_title = wx.StaticText(
            self,
            label="JPEG Compression"
        )
        jpeg_quality_slider = wx.Slider(
            self,
            value=self.settings.jpeg_quality,
            minValue=1,
            maxValue=95,
            style=wx.SL_LABELS,
            size=(150, -1)
        )
        jpeg_quality_slider.Bind(wx.EVT_SCROLL, self.OnJpegSlider)
        jpeg_quality_desc = wx.StaticText(
            self,
            label="JPEG compression quality. Lower numbers are crustier.",
            size=(200, -1)
        )
        jpeg_quality_desc.Wrap(200)

        sat_title = wx.StaticText(
            self,
            label="Saturation"
        )
        sat_amount = wx.Slider(
            self,
            value=self.settings.saturation,
            minValue=1,
            maxValue=100,
            style=wx.SL_LABELS,
            size=(150, -1)
        )
        sat_amount.Bind(wx.EVT_SCROLL, self.OnSatSlider)
        sat_desc = wx.StaticText(
            self,
            label=("Amount to multiply saturation by. This causes the " +
                   "neon colors commonly found in deep fried images. Set " +
                   "to 1 to disable."),
            size=(200, -1)
        )
        sat_desc.Wrap(200)

        # Set up layout
        gridsizer = wx.FlexGridSizer(2, 3, 1, 10)
        gridsizer.SetFlexibleDirection(wx.HORIZONTAL)
        gridsizer.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_ALL)
        gridsizer.AddGrowableCol(0, 1)
        gridsizer.AddGrowableCol(2, 1)

        gridsizer.Add(jpeg_quality_title, 1, wx.ALIGN_RIGHT | wx.ALL)
        gridsizer.Add(jpeg_quality_slider)
        gridsizer.Add(jpeg_quality_desc, 1, wx.ALIGN_LEFT | wx.ALL)

        gridsizer.Add(sat_title, 1, wx.ALIGN_RIGHT | wx.ALL)
        gridsizer.Add(sat_amount)
        gridsizer.Add(sat_desc, 1, wx.ALIGN_LEFT | wx.ALL)

        self.SetSizer(gridsizer)

    def OnJpegSlider(self, event):
        self.settings.jpeg_quality = event.GetPosition()

    def OnSatSlider(self, event):
        self.settings.saturation = event.GetPosition()


class MainWindow(wx.Frame):
    def __init__(self, img_fryer, gif_fryer):
        style = wx.DEFAULT_FRAME_STYLE & ~(wx.RESIZE_BORDER | wx.MAXIMIZE_BOX)
        wx.Frame.__init__(self, None, title="Frycook", size=(500, 200),
                          style=style)
        self.SetIcon(wx.Icon(str(DATADIR / "icon.ico")))

        p = wx.Panel(self)
        nb = wx.Notebook(p)

        self.convert_panel = ConvertPanel(nb, img_fryer, gif_fryer)

        # Settings are shared between img and gif fryer, so we only pass
        # in img_fryer
        self.convert_settings_panel = ConvertSettingsPanel(nb, img_fryer)

        nb.AddPage(self.convert_panel, "Fryer")
        nb.AddPage(self.convert_settings_panel, "Image/.gif Settings")

        sizer = wx.BoxSizer()
        sizer.Add(nb, 1, wx.EXPAND)
        p.SetSizer(sizer)


def main():
    app = wx.App(False)

    fry_settings = ImageFryerSettings()

    img_fryer = StillImageFryer(fry_settings)
    gif_fryer = GifFryer(fry_settings)

    frame = MainWindow(img_fryer=img_fryer,
                       gif_fryer=gif_fryer)
    frame.Show(True)

    app.MainLoop()


if __name__ == "__main__":
    main()
