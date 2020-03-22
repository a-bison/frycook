#!/bin/env python3

from PIL import Image, ImageEnhance
import wx

from pathlib import Path


class Fryer:
    def fry(self, path):
        save_directory = path.parent
        save_location = save_directory / ("deepfried_" + path.stem +
                                          path.suffix)

        print("convert " + str(path))
        print("save to " + str(save_location))

        img = Image.open(path)

        img = img.convert("RGB")
        img = ImageEnhance.Color(img).enhance(8.0)

        img.save(save_location, "JPEG", quality=1)

    def is_file_supported(self, path):
        return path.suffix in [".png", ".jpg", ".jpeg"]


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


class MainWindow(wx.Frame):
    def __init__(self, fryer):
        wx.Frame.__init__(self, None, title="Frycook", size=(500, 200))
        self.SetIcon(wx.Icon("icon.ico"))

        self.convert_panel = ConvertPanel(self, fryer)


def main():
    app = wx.App(False)

    fryer = Fryer()

    frame = MainWindow(fryer)
    frame.Show(True)

    app.MainLoop()


if __name__ == "__main__":
    main()
