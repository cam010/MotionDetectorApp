import os
from pathlib import Path
import tkinter
from tkinter.ttk import Style, Scale
from tkinter import messagebox
from PIL import Image, ImageTk
from typing import Literal
import colours
import ttkthemes


class LightThemeStyle:
    def __init__(self, root):
        self.root = root

        # init style
        self.style = Style(master=self.root)
        self.style.theme_create("custom_theme", parent="alt")
        self.style.theme_use("custom_theme")

        # Widget Images Directory
        parent_dir = Path(__file__).resolve().parents[1]
        self.widget_image_dir = os.path.join(
            parent_dir, "Assets", "Images", "Widget Images"
        )

        # load widget styles
        self.labelframe()
        self.label()
        self.checkbox()
        self.combobox()
        self.button()
        self.separator()
        self.custom_horizontal_scale()

    def labelframe(self):
        self.style.configure("TLabelframe", background="white", foreground="white")
        self.style.configure("TLabelframe.Label", background="white")

    def label(self):
        self.style.configure(
            "TLabel",
            background="white",
        )

    def checkbox(self):
        self.style.configure("TCheckbutton", background="white", focuscolor="white")

    def combobox(self):
        self.style.configure(
            "TCombobox",
            selectbackground="white",
            selectforeground="black",
            fieldbackground="white",
            background="white",
        )

    def button(self):
        self.style.configure("TButton", background="white")

    def separator(self):
        self.style.configure(
            "TSeparator",
        )

    def custom_horizontal_scale(self):
        # https://stackoverflow.com/a/59680262 <-- See this answer regarding custom ttk sliders
        self.image_trough = ImageTk.PhotoImage(
            Image.open(os.path.join(self.widget_image_dir, "trough.png")).resize(
                (25, 25)  # needs to be resized in future
            )
        )
        self.image_slider = ImageTk.PhotoImage(
            Image.open(os.path.join(self.widget_image_dir, "slider.png")).resize(
                (30, 30)  # needs to be resized in future
            )
        )
        self.style.element_create("custom.Scale.trough", "image", self.image_trough)
        self.style.configure(
            "custom.Scale.trough", image=self.image_trough
        )  # This needs to be here, similar to camera frame label as img not stored within tkinter properly

        self.style.element_create("custom.Scale.slider", "image", self.image_slider)
        self.style.configure("custom.Scale.slider", image=self.image_slider)

        self.style.layout(
            "custom.Horizontal.TScale",
            [
                ("custom.Scale.trough", {"sticky": "ew"}),
                (
                    "custom.Scale.slider",
                    {
                        "side": "left",
                        "sticky": "",
                        "children": [("custom.Horizontal.Scale.label", {"sticky": ""})],
                    },
                ),
            ],
        )


###########
# DARK THEME
############


class DarkThemeStyle:
    def __init__(self, root):
        self.root = root

        # init style
        self.style = Style(master=self.root)
        self.style.theme_create("dark_theme", parent="clam")
        self.style.theme_use("dark_theme")

        # Widget Images Directory
        parent_dir = Path(__file__).resolve().parents[1]
        self.widget_image_dir = os.path.join(
            parent_dir, "Assets", "Images", "Widget Images"
        )

        # load widget styles
        self.labelframe()
        self.label()
        self.checkbox()
        self.combobox()
        self.button()
        self.separator()
        self.custom_horizontal_scale()

    def labelframe(self):
        self.style.configure(
            "TLabelframe",
            background=colours.DARK_WIDGET_BACKGROUND,
            foreground=colours.DARK_TEXT_COLOUR,
            bordercolor=colours.DARK_WIDGET_ALT,
            relief="solid"
        )
        self.style.configure(
            "TLabelframe.Label",
            background=colours.DARK_WIDGET_BACKGROUND,
            foreground=colours.DARK_TEXT_COLOUR,
        )

    def label(self):
        self.style.configure(
            "TLabel",
            background=colours.DARK_WIDGET_BACKGROUND,
            foreground=colours.DARK_TEXT_COLOUR,
        )

    def checkbox(self):
        self.style.configure(
            "TCheckbutton",
            background=colours.DARK_WIDGET_BACKGROUND,
            focuscolor=colours.DARK_WIDGET_BACKGROUND,
            foreground=colours.DARK_WIDGET_ALT,
        )

    def combobox(self):
        self.style.configure(
            "TCombobox",
            selectbackground=colours.DARK_WIDGET_BACKGROUND,
            selectforeground="black",
            fieldbackground=colours.DARK_WIDGET_BACKGROUND,
            background=colours.DARK_WIDGET_BACKGROUND,
        )

    def button(self):
        self.style.configure(
            "TButton",
            background=colours.DARK_WIDGET_BACKGROUND,
            foreground=colours.DARK_TEXT_COLOUR,
        )

    def separator(self):
        self.style.configure(
            "TSeparator",
        )

    def custom_horizontal_scale(self):
        # https://stackoverflow.com/a/59680262 <-- See this answer regarding custom ttk sliders
        self.image_trough = ImageTk.PhotoImage(
            Image.open(os.path.join(self.widget_image_dir, "trough.png")).resize(
                (25, 25)  # needs to be resized in future
            )
        )
        self.image_slider = ImageTk.PhotoImage(
            Image.open(os.path.join(self.widget_image_dir, "slider.png")).resize(
                (30, 30)  # needs to be resized in future
            )
        )
        self.style.element_create("dark_theme.Scale.trough", "image", self.image_trough)
        self.style.configure(
            "dark_theme.Scale.trough", image=self.image_trough
        )  # This needs to be here, similar to camera frame label as img not stored within tkinter properly

        self.style.element_create("dark_theme.Scale.slider", "image", self.image_slider)
        self.style.configure("dark_theme.Scale.slider", image=self.image_slider)

        self.style.layout(
            "dark_theme.Horizontal.TScale",
            [
                ("dark_theme.Scale.trough", {"sticky": "ew"}),
                (
                    "dark_theme.Scale.slider",
                    {
                        "side": "left",
                        "sticky": "",
                        "children": [("dark_theme.Horizontal.Scale.label", {"sticky": ""})],
                    },
                ),
            ],
        )


class Styles:
    def __init__(self, root):#
        pass
        # DarkThemeStyle(root)
        # LightThemeStyle(root)
        # self.style = Style()

    def use_dark_theme(self):
        pass
        # self.style.theme_use("dark_theme")

    def use_light_theme(self):
        pass
        # self.style.theme_use("light_theme")


################
# CUSTOM WIDGETS
################


class CustomHorizontalScale(Scale):
    # https://stackoverflow.com/a/59680262 <-- See this answer regarding custom ttk sliders
    def __init__(self, root, **kw):
        self.variable = kw.pop("variable")
        super().__init__(root, variable=self.variable, orient="horizontal", **kw)
        self.style = Style(root)
        self._style_name = "{}.dark_theme.Horizontal.TScale".format(self)
        self["style"] = self._style_name

    def set(self, val):
        super().set(val)


class CustomInputWindow(tkinter.Toplevel):
    """Creates a Toplevel asking user for input. Input can be float, int or str.\n
    Checks input. Checks can include string length and number boundaries.\n
    When an input is entered which meets checks it calls command with the input as
    argument in entered type"""

    def __init__(
        self,
        command,
        title: str,
        input_message: str,
        type: Literal["integer", "float", "string"],
        number_low_boundary: float = None,
        number_high_boundary: float = None,
        string_max_len: int = None,
        custom_geometry: str = None,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)

        # Exception handler
        tkinter.Tk.report_callback_exception = self.report_callback_exception

        # make params class-wide
        self.command = command
        self.number_low_boundary = number_low_boundary
        self.number_high_boundary = number_high_boundary
        self.string_max_len = string_max_len
        self.type = type

        # init window
        self.title(title)
        self.attributes("-topmost", True)
        if custom_geometry is not None:
            self.geometry(custom_geometry)

        # Create label
        label = tkinter.Label(self, text=input_message)
        label.grid(row=0, column=0)

        # Create input
        match self.type:
            case "integer":
                self.input_var = tkinter.IntVar()
            case "float":
                self.input_var = tkinter.DoubleVar()
            case "string":
                self.input_var = tkinter.StringVar()

        self.input_entry = tkinter.Entry(self, textvariable=self.input_var)
        self.input_entry.grid(row=1, column=0)

        # Create submit button
        self.submit_button = tkinter.Button(
            self, text="Submit", command=lambda: self.submit()
        )
        self.submit_button.grid(row=2, column=0)
        self.bind("<Return>", lambda event: self.submit_button.invoke())

    def submit(self):
        try:
            val = self.input_var.get()
        except:
            raise Exception("Please enter a {} value".format(self.type))
        if val is not None:
            is_within_bounds = self.check_within_bounds(val)
            if not is_within_bounds[0]:
                message = "Input contains the following errors:"
                for m in is_within_bounds[1:]:
                    message += "\n- {}".format(m)
                raise Exception(message)
            else:
                self.command(val)
                self.destroy()

        else:
            self.show_error("Please enter a value")

    def check_within_bounds(self, val):
        if self.type == "integer" or self.type == "float":
            if val < self.number_low_boundary or val > self.number_high_boundary:
                return [False, "number not in boundaries"]
            else:
                return [True]

        elif self.type == "string" and self.string_max_len != None:
            if len(val) > self.string_max_len:
                return [False, "string too long"]
            else:
                return [True]

    def report_callback_exception(self, exc, val, tb):
        messagebox.showerror("Input Error", val)
