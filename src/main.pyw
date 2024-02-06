# builtins
import datetime
import os
import tkinter as tk
from tkinter import ttk

# this is neccessary even though in the code I use tk.filedialog, if not imported specifically error is thrown
from tkinter import filedialog
from tkinter import messagebox
import threading
import time
import numpy
import controller
from os import startfile
from functools import partial

# non builtins
try:
    from PIL import Image, ImageTk
except ImportError:
    tk.Tk().withdraw()
    messagebox.showerror(
        "error",
        "Can't import PIL module. Please install PIL package. Program will exit",
    )

try:
    import cv2
except ImportError:
    tk.Tk().withdraw()
    messagebox.showerror(
        "error",
        "Can't import cv2 module. Please install cv2 package. Program will exit",
    )

from ttkthemes import ThemedTk

import ttk_styles
import colours


class GUI:
    def __init__(self) -> None:
        self.controller = controller.Controller()

        self.stop_thread = False
        self.pause = False

        # init window
        self.root = ThemedTk(theme="equilux")
        self.root.title("Motion Detector")
        self.root.minsize(width=650, height=400)
        self.root.geometry("800x500")
        self.root.state("zoomed")
        # self.root.attributes("-fullscreen", True)
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_columnconfigure(2, weight=1)
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_rowconfigure(1, weight=1)

        # style
        self.style = ttk_styles.Styles(self.root)
        self.style.use_dark_theme()

        # create widgets
        self.create_menubar()
        self.create_image_label()

        self.create_modifiers_frame()
        self.create_motion_frame()
        self.create_camera_modifiers_frame()

        self.update_frame_label_frame_thread_controller()
        self.first_frame_loaded = False
        
        self.root.bind("<Configure>", self.resize)

        self.root.mainloop()

    def resize(self, event):
        return
        self.root.update_idletasks()
        
    
    def quit(self):
        # stops threads otherwise they throw errors trying to execute
        # processes when TCL objects are destroyed
        self.controller.stop_thread = True
        self.stop_thread = True

        # if quit first, then root freezes for a couple of seconds before
        # closing
        self.root.destroy()
        quit()

    def create_menubar(self):
        self.menubar = tk.Menu(self.root, background="blue", fg="white")
        self.populate_menubar()
        self.root.config(menu=self.menubar)

    def populate_menubar(self):
        ###########
        # File menu
        ###########
        file_menu = tk.Menu(self.menubar, tearoff=0, background="#434B4C", fg="white")

        file_menu.add_command(
            label="Exit", command=lambda: self.quit(), accelerator="Alt+F4"
        )

        #################
        # Source Settings
        #################
        self.source_menu = tk.Menu(
            self.menubar, tearoff=0, background="#434B4C", fg="white"
        )

        self.source_menu.add_command(
            label="Open Video File",
            command=lambda: self.change_frame_source(change_to="video"),
            accelerator="Ctrl+O",
        )
        self.source_menu.add_command(
            label="Switch to Camera Mode",
            command=lambda: self.change_frame_source(change_to="camera"),
            accelerator="Ctrl+I",
            state="disabled",  # program will start in camera mode
        )

        ###############
        # Frame settings
        ###############
        # Rect settings
        frame_settings_menu = tk.Menu(
            self.menubar, tearoff=0, background="#434B4C", fg="white"
        )
        rect_size = tk.Menu(
            frame_settings_menu, tearoff=0, background="#434B4C", fg="white"
        )
        for x in [100, 500, 1000, 2500, 5000, "custom"]:
            rect_size.add_command(
                label=x,
                command=partial(self.rect_area_changed, x),
            )
        # menu is created before settings, so self variable has to be created
        # here
        self.rect_draw_checkbox = tk.BooleanVar(value=True)
        frame_settings_menu.add_checkbutton(
            label="Enable Rect Drawing",
            command=lambda: self.rect_draw_changed(),
            variable=self.rect_draw_checkbox,
            onvalue=True,
            offvalue=False,
            accelerator="Ctrl+Shift+D",
        )
        frame_settings_menu.add_cascade(label="Minimum Rect Area", menu=rect_size)

        frame_settings_menu.add_separator()

        # Frame Settings
        self.flip = tk.BooleanVar(value=True)
        frame_settings_menu.add_checkbutton(
            label="Flip Frame",
            command=lambda: self.flip.set(not self.flip.get()),
            variable=self.flip,
            onvalue=True,
            offvalue=False,
            accelerator="Ctrl+Shift+F",
        )

        ##############
        # Add Cascades
        ##############
        self.menubar.add_cascade(label="File", menu=file_menu)
        self.menubar.add_cascade(label="Source Settings", menu=self.source_menu)
        self.menubar.add_cascade(label="Frame Settings", menu=frame_settings_menu)

        ###########
        # Add Binds
        ###########
        # File Menu

        # Source Menu
        self.root.bind(
            "<Control-o>", lambda _: self.change_frame_source(change_to="video")
        )
        self.root.bind(
            "<Control-i>", lambda _: self.change_frame_source(change_to="camera")
        )

        # Frame Settings Menu
        self.root.bind(
            "<Control-Shift-D>",
            lambda _: self.rect_draw_changed(not self.rect_draw_checkbox.get()),
        )
        self.root.bind(
            "<Control-Shift-F>", lambda _: self.flip.set(not self.flip.get())
        )
        # self.root.bind("<KeyPress>", lambda e: print(e))

    def create_image_label(self):
        self.image_label = ttk.Label(self.root, image=None)
        self.image_label.grid(row=0, column=1, sticky="NSEW")

    def create_modifiers_frame(self):
        self.modifiers_frame = ttk.Labelframe(self.root, text="Frame Settings")
        self.modifiers_frame.grid(row=0, column=0, sticky="NSEW", rowspan=2)

        self.create_modifiers()

    def create_motion_frame(self):
        self.motion_frame = ttk.Labelframe(self.root, text="Recent Motions")
        self.motion_frame.grid(row=0, column=2, sticky="NSEW", rowspan=2)

        self.recent_motions = []
        self.motions_labels = []

        self.open_output_file_button()

        self.update_motions_display_thread_controller()

    def create_camera_modifiers_frame(self):
        self.camera_modifiers_frame = ttk.Labelframe(self.root, text="Source Settings")
        self.camera_modifiers_frame.grid(row=1, column=1, sticky="NSEW", ipady=10)

        self.create_camera_modifiers()

    def create_camera_modifiers(self):
        self.previous_camera_button = ttk.Button(
            self.camera_modifiers_frame,
            text="<-- Previous Camera",
            command=partial(self.changed_camera, "prev"),
        )
        self.previous_camera_button.grid(row=0, column=0, padx=(10, 0))

        self.switch_frame_source_button = ttk.Button(
            self.camera_modifiers_frame,
            text="Pick File",
            command=lambda: self.change_frame_source(
                change_to="video"
                if self.switch_frame_source_button["text"] == "Pick File"
                else "camera"
            ),
        )
        self.switch_frame_source_button.grid(row=0, column=1)

        self.disable_source_button = ttk.Button(
            self.camera_modifiers_frame,
            text="Disable Source",
            command=lambda: self.change_disabled_source(
                "disabled"
                if self.disable_source_button["text"] == "Disable Source"
                else "enabled"
            ),
        )
        self.disable_source_button.grid(row=0, column=2)

        self.pause_button = ttk.Button(
            self.camera_modifiers_frame,
            text="Pause",
            command=lambda: self.paused_changed(),
        )
        self.pause_button.grid(row=0, column=3)

        self.next_camera_button = ttk.Button(
            self.camera_modifiers_frame,
            text="Next Camera -->",
            command=partial(self.changed_camera, "next"),
        )
        self.next_camera_button.grid(row=0, column=4, padx=(0, 10))

        for i in range(0, 4):
            self.camera_modifiers_frame.grid_columnconfigure(i, weight=1)

    def paused_changed(self):
        self.pause_button.config(state="disabled")
        if self.pause_button["text"] == "Pause":
            self.pause_button.config(text="Play")
            self.controller.pause = True
            self.pause = True

        else:
            self.pause_button.config(text="Pause")
            self.controller.pause = False
            self.pause = False
        self.pause_button.config(state="normal")

    def change_disabled_source(self, change_to):
        if change_to == "disabled":
            self.change_frame_source(
                change_to="blank",
            )
            self.disable_source_button.config(text="Enable Source")
        else:
            self.disable_source_button.config(text="Disable Source")
            self.change_frame_source(change_to="camera")

    def load_video_file(self):
        filetypes = (
            ("video files", "*.mp4"),
            ("movie files", "*.mov"),
        )
        return tk.filedialog.askopenfilename(
            initialdir=os.path.join(os.path.join(os.environ["USERPROFILE"]), "Desktop"),
            title="Select a File",
            filetypes=(filetypes),
        )

    def change_frame_source(self, change_to):
        self.switch_frame_source_button.config(state="disabled")

        if change_to == "blank":
            self.controller.source = "blank"
            self.controller.changed_source("blank")
            self.source_menu.entryconfig("Switch to Camera Mode", state="normal")
            self.switch_frame_source_button.config(state="normal")

        if change_to == "video":
            source = self.load_video_file()
            if source != "":
                self.controller.vid_source = source
                self.controller.source = "video"
                self.controller.changed_source("video")
                self.switch_frame_source_button.config(text="Switch to Camera Mode")
                self.source_menu.entryconfig("Switch to Camera Mode", state="normal")

        elif change_to == "camera":
            # This if statement is to handle when user uses keyboard shortcut
            # to call "Switch to Camera Mode" when already in camera mode
            if (
                self.source_menu.entrycget(
                    self.source_menu.index("Switch to Camera Mode"), "state"
                )
                == "disabled"
            ):
                self.switch_frame_source_button.config(state="normal")
                return

            self.controller.source = "camera"
            self.controller.changed_source("camera")
            self.disable_source_button.config(state="normal")
            self.switch_frame_source_button.config(text="Pick File")
            self.source_menu.entryconfig("Switch to Camera Mode", state="disabled")

        self.switch_frame_source_button.config(state="normal")

    def changed_camera(self, change):
        if change == "prev":
            btn = self.previous_camera_button
            btn.config(state="disabled")
            change = 1
        elif change == "next":
            btn = self.next_camera_button
            btn.config(state="disabled")
            change = -1

        self.controller.change_camera(change)
        btn.after(100, lambda: btn.config(state="normal"))

    def rect_draw_changed(self, val=None):
        if val is not None:
            self.rect_draw_checkbox.set(val)
            self.rect_draw_changed()
        if self.rect_draw_checkbox.get() == True:
            self.controller.show_rect = True
        else:
            self.controller.show_rect = False

    def custom_val_rect_area_changed(self, val):
        if val == "custom":
            ttk_styles.CustomInputWindow(
                command=self.custom_val_rect_area_changed,
                title="Custom Val",
                input_message="Please enter a value for rect area (10-5000 inclusive)",
                type="integer",
                number_low_boundary=10,
                number_high_boundary=5000,
            )
        else:
            self.rect_area_scale.set(val)

    def rect_area_changed(self, val=None):
        if val is None:
            rect_area = self.rect_area.get()
        elif val == "custom":
            ttk_styles.CustomInputWindow(
                command=self.rect_area_changed,
                title="Custom Val",
                input_message="Please enter a value for rect area (10-5000 inclusive)",
                type="integer",
                number_low_boundary=10,
                number_high_boundary=5000,
            )
            return
        else:
            rect_area = val
            self.rect_area_scale.set(val)
        self.controller.rect_area = rect_area

    def sensitivity_changed(self):
        threshold = 100 - self.motion_sensitivity.get()
        self.controller.threshold = threshold

    def frame_type_changed(self):
        self.controller.frame_type = self.frame_type.get()

    def create_modifiers(self):
        # Whether or not to draw rects around moving objects
        rect_draw_checkbox = ttk.Checkbutton(
            self.modifiers_frame,
            text="Enable Rect Drawing",
            command=lambda: self.rect_draw_changed(),
            variable=self.rect_draw_checkbox,
            onvalue=True,
            offvalue=False,
        )
        rect_draw_checkbox.state(["selected"])
        rect_draw_checkbox.grid(row=2, column=0)

        # How big the minimum area of a moving object rect has to be to be drawn
        ttk.Separator(self.modifiers_frame, orient="horizontal").grid(
            row=3, column=0, sticky="EW", pady=3
        )
        self.rect_area = tk.IntVar()
        ttk.Label(self.modifiers_frame, text="Minimum Rect Area").grid(row=4, column=0)

        self.rect_area_scale = ttk_styles.CustomHorizontalScale(
            root=self.modifiers_frame,
            variable=self.rect_area,
            from_=10,
            to=5000,
            command=lambda _: self.rect_area_changed(),
        )

        self.rect_area_scale.set(500)
        self.rect_area_scale.grid(row=5, column=0)

        # Threshold for defining image as "different" - higher threshold is
        # lower motion sensitivity
        ttk.Separator(self.modifiers_frame, orient="horizontal").grid(
            row=6, column=0, sticky="EW", pady=3
        )
        self.motion_sensitivity = tk.IntVar()
        ttk.Label(self.modifiers_frame, text="Motion Sensitivity").grid(row=7, column=0)
        sensitivity_scale = ttk_styles.CustomHorizontalScale(
            self.modifiers_frame,
            from_=1,
            to=99,
            variable=self.motion_sensitivity,
            command=lambda _: self.sensitivity_changed(),
        )
        sensitivity_scale.set(80)
        sensitivity_scale.grid(row=8, column=0)

        # Flip image
        ttk.Separator(self.modifiers_frame, orient="horizontal").grid(
            row=9, column=0, sticky="EW", pady=3
        )
        self.flip_image = ttk.Checkbutton(
            self.modifiers_frame,
            text="Flip Frame",
            variable=self.flip,
            onvalue=True,
            offvalue=False,
        )
        self.flip_image.grid(row=10, column=0)

        # Frame types
        ttk.Separator(self.modifiers_frame, orient="horizontal").grid(
            row=11, column=0, sticky="EW", pady=3
        )
        self.frame_type = tk.StringVar(value="normal")
        frame_type_options = ["normal", "greyscale"]

        self.frame_type_combobox = ttk.Combobox(
            self.modifiers_frame,
            textvariable=self.frame_type,
            values=frame_type_options,
        )
        self.frame_type_combobox["state"] = "readonly"
        self.frame_type_combobox.bind(
            "<<ComboboxSelected>>", lambda *_: self.frame_type_changed()
        )
        self.frame_type_combobox.grid(row=12, column=0)

    def destroy_motion_labels(self):
        for i, label in enumerate(self.motions_labels):
            label.destroy()
            self.motions_labels.pop(i)

    def create_motion_labels(self):
        # split into 2 for loops so that labels are put on screen at closer
        # intervals for a smoother experience
        for timestamp in self.recent_motions:
            label = ttk.Label(self.motion_frame, text=timestamp)
            self.motions_labels.append(label)
        for label in self.motions_labels:
            label.pack()

    def update_motions_display(self):
        while True:
            if self.stop_thread:
                break
            if self.pause:
                # if not here in every thread, causes app to grind to halt
                # during pause
                time.sleep(0.25)
                continue

            self.set_recent_motions()
            self.destroy_motion_labels()
            self.create_motion_labels()

            # if grabbing motion from controller class is done every 0.25s,
            # then 12 will be grabbed in 3s so none are missed, but update speed
            # is less than having to do a widget update every 0.25s which was
            # glitchy
            time.sleep(3)

    def set_recent_motions(self):
        self.recent_motions = self.controller.get_motion()

    def open_output_file(self):
        startfile(self.controller.output_file_name)

    def open_output_file_button(self):
        open_output_file_button = ttk.Button(
            self.motion_frame,
            text="Open Output File",
            command=lambda: self.open_output_file(),
        )
        open_output_file_button.pack(side="bottom", pady=(0, 10))

    def update_motions_display_thread_controller(self):
        self.update_motions_display_thread = threading.Thread(
            target=self.update_motions_display
        )
        self.update_motions_display_thread.daemon = True
        self.update_motions_display_thread.start()

    def update_frame_label_frame(self):
        while True:
            start_process_time = time.time()
            if self.stop_thread:
                break
            if self.pause:
                time.sleep(
                    0.25
                )  # if not here in every thread, causes app to grind to halt during pause
                continue
            frame = self.controller.get_frame()
            if frame is None:
                continue
            else:
                height, width, *_ = frame.shape
                # if not self.first_frame_loaded:
                #     self.height = height
                #     self.width = width
                #     self.first_frame_loaded = True

                # if height != self.height or width != self.width:
                label_width, label_height = self.image_label.winfo_height(), self.image_label.winfo_width()
                if height != label_height or width != label_width:
                    # take off 3 from self.height,width so that frame borders
                    # are shown clearly with no overlap
                    if label_height > 3 and label_width > 3:
                        frame = cv2.resize(frame, (label_height - 3, label_width - 3))
                if self.flip.get():
                    # flips frame vertically
                    frame = numpy.fliplr(frame)
                frame = Image.fromarray(frame)
                frame = ImageTk.PhotoImage(image=frame)

                # Put it in the display window
                self.image_label.configure(image=frame)
                # https://web.archive.org/web/20201111190625id_/http://effbot.org/pyfaq/why-do-my-tkinter-images-not-appear.htm
                # So if there isn't a reference to the .image, then
                # tkinter will discard it and a white image will be shown instead
                self.image_label.image = frame
                
                
                end_process_time = time.time()
                difference = end_process_time - start_process_time
                # fps = 60
                if difference < 1 / 60:
                    # If the time spent processing the frame (difference) is less than the time that each frame should
                    # be displayed for (to fit with fps) then add a wait until the frame duration is finished
                    time.sleep(((1 / 60) - difference))

    def update_frame_label_frame_thread_controller(self):
        self.update_frame_label_frame_thread = threading.Thread(
            target=self.update_frame_label_frame
        )
        self.update_frame_label_frame_thread.daemon = True
        self.update_frame_label_frame_thread.start()


if __name__ == "__main__":
    GUI()
