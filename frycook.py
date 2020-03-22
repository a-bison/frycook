#!/bin/env python3

from PIL import Image, ImageEnhance
import wx

from pathlib import Path


class FryerSettings:
    def __init__(self):
        self.jpeg_quality = 1
        self.saturation = 8


class Fryer:
    def __init__(self, settings):
        self.settings = settings

    def fry(self, path):
        s = self.settings

        save_directory = path.parent
        save_location = save_directory / ("deepfried_" + path.stem +
                                          path.suffix)

        print("convert " + str(path))
        print("save to " + str(save_location))

        img = Image.open(path)
        img = img.convert("RGB")

        img = ImageEnhance.Color(img).enhance(s.saturation)

        img.save(save_location, "JPEG", quality=s.jpeg_quality)

    def is_file_supported(self, path):
        return path.suffix.lower() in [".png", ".jpg", ".jpeg", ".bmp"]


class FryTarget(wx.FileDropTarget):
    def __init__(self, fryer):
        super().__init__()
        self.fryer = fryer

    def OnDropFiles(self, x, y, filenames):
        for filename in filenames:
            if self.fryer.is_file_supported(Path(filename)):
                self.fryer.fry(Path(filename))

        return True


class ConvertPanel(wx.Panel):
    def __init__(self, parent, fryer):
        super().__init__(parent)

        self.SetDropTarget(FryTarget(fryer))

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
    def __init__(self, fryer):
        style = wx.DEFAULT_FRAME_STYLE & ~(wx.RESIZE_BORDER | wx.MAXIMIZE_BOX)
        wx.Frame.__init__(self, None, title="Frycook", size=(500, 200),
                          style=style)
        self.SetIcon(wx.Icon("icon.ico"))

        p = wx.Panel(self)
        nb = wx.Notebook(p)

        self.convert_panel = ConvertPanel(nb, fryer)
        self.convert_settings_panel = ConvertSettingsPanel(nb, fryer)

        nb.AddPage(self.convert_panel, "Fryer")
        nb.AddPage(self.convert_settings_panel, "Settings")

        sizer = wx.BoxSizer()
        sizer.Add(nb, 1, wx.EXPAND)
        p.SetSizer(sizer)


def main():
    app = wx.App(False)

    fry_settings = FryerSettings()

    fryer = Fryer(fry_settings)

    frame = MainWindow(fryer)
    frame.Show(True)

    app.MainLoop()


if __name__ == "__main__":
    main()
