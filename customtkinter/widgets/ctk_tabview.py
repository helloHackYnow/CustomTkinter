from typing import Union, Tuple, Dict, List

from ..theme_manager import ThemeManager
from .ctk_frame import CTkFrame
from .widget_base_class import CTkBaseClass
from .ctk_segmented_button import CTkSegmentedButton
from .ctk_canvas import CTkCanvas
from ..draw_engine import DrawEngine


class CTkTabview(CTkBaseClass):
    """
    Tabview...
    For detailed information check out the documentation.
    """

    _top_spacing = 10  # px on top of the buttons
    _top_button_overhang = 8  # px
    _button_height = 10

    def __init__(self,
                 master: any = None,
                 width: int = 300,
                 height: int = 250,
                 corner_radius: Union[int, str] = "default_theme",
                 border_width: Union[int, str] = "default_theme",

                 bg_color: Union[str, Tuple[str, str], None] = None,
                 fg_color: Union[str, Tuple[str, str], None] = "default_theme",
                 border_color: Union[str, Tuple[str, str]] = "default_theme",

                 segmented_button_fg_color: Union[str, Tuple[str, str], None] = "default_theme",
                 segmented_button_selected_color: Union[str, Tuple[str, str]] = "default_theme",
                 segmented_button_selected_hover_color: Union[str, Tuple[str, str]] = "default_theme",
                 segmented_button_unselected_color: Union[str, Tuple[str, str]] = "default_theme",
                 segmented_button_unselected_hover_color: Union[str, Tuple[str, str]] = "default_theme",

                 text_color: Union[str, Tuple[str, str]] = "default_theme",
                 text_color_disabled: Union[str, Tuple[str, str]] = "default_theme",

                 **kwargs):

        # transfer some functionality to CTkFrame
        super().__init__(master=master, bg_color=bg_color, width=width, height=height, **kwargs)

        # color
        self._border_color = ThemeManager.theme["color"]["frame_border"] if border_color == "default_theme" else border_color

        # determine fg_color of frame
        if fg_color == "default_theme":
            if isinstance(self.master, (CTkFrame, CTkTabview)):
                if self.master.cget("fg_color") == ThemeManager.theme["color"]["frame_low"]:
                    self._fg_color = ThemeManager.theme["color"]["frame_high"]
                else:
                    self._fg_color = ThemeManager.theme["color"]["frame_low"]
            else:
                self._fg_color = ThemeManager.theme["color"]["frame_low"]
        else:
            self._fg_color = fg_color

        # shape
        self._corner_radius = ThemeManager.theme["shape"]["frame_corner_radius"] if corner_radius == "default_theme" else corner_radius
        self._border_width = ThemeManager.theme["shape"]["frame_border_width"] if border_width == "default_theme" else border_width

        self._canvas = CTkCanvas(master=self,
                                 bg=ThemeManager.single_color(self._bg_color, self._appearance_mode),
                                 highlightthickness=0,
                                 width=self._apply_widget_scaling(self._current_width - self._top_spacing - self._top_button_overhang),
                                 height=self._apply_widget_scaling(self._current_height))
        self._draw_engine = DrawEngine(self._canvas)

        self._segmented_button = CTkSegmentedButton(self,
                                                    values=[],
                                                    height=self._button_height,
                                                    fg_color=segmented_button_fg_color,
                                                    selected_color=segmented_button_selected_color,
                                                    selected_hover_color=segmented_button_selected_hover_color,
                                                    unselected_color=segmented_button_unselected_color,
                                                    unselected_hover_color=segmented_button_unselected_hover_color,
                                                    text_color=text_color,
                                                    text_color_disabled=text_color_disabled,
                                                    corner_radius=corner_radius,
                                                    border_width=self._apply_widget_scaling(3))
        self._configure_segmented_button_background_corners()
        self._configure_grid()
        self._set_grid_canvas()

        self._tab_dict: Dict[str, CTkFrame] = {}
        self._name_list: List[str] = []  # list of unique tab names in order of tabs
        self._current_name: str = ""

        super().bind('<Configure>', self._update_dimensions_event)

    def winfo_children(self) -> List[any]:
        """
        winfo_children of CTkTabview without canvas and segmented button widgets,
        because it's not a child but part of the CTkTabview itself
        """

        child_widgets = super().winfo_children()
        try:
            child_widgets.remove(self._canvas)
            child_widgets.remove(self._segmented_button)
            return child_widgets
        except ValueError:
            return child_widgets

    def _set_scaling(self, *args, **kwargs):
        super()._set_scaling(*args, **kwargs)

        self._canvas.configure(width=self._apply_widget_scaling(self._desired_width),
                               height=self._apply_widget_scaling(self._desired_height - self._top_spacing - self._top_button_overhang))
        self._draw()

    def _set_dimensions(self, width=None, height=None):
        super()._set_dimensions(width, height)

        self._canvas.configure(width=self._apply_widget_scaling(self._desired_width),
                               height=self._apply_widget_scaling(self._desired_height - self._top_spacing - self._top_button_overhang))
        self._draw()

    def _configure_segmented_button_background_corners(self):
        """ needs to be called for changes in fg_color, bg_color """

        if self._fg_color is not None:
            self._segmented_button.configure(background_corner_colors=(self._bg_color, self._bg_color, self._fg_color, self._fg_color))
        else:
            self._segmented_button.configure(background_corner_colors=(self._bg_color, self._bg_color, self._bg_color, self._bg_color))

    def _configure_tab_background_corners_by_name(self, name: str):
        """ needs to be called for changes in fg_color, bg_color, border_width """

        if self._border_width == 0:
            if self._fg_color is not None:
                self._tab_dict[name].configure(background_corner_colors=(self._fg_color, self._fg_color, self._bg_color, self._bg_color))
            else:
                self._tab_dict[name].configure(background_corner_colors=(self._bg_color, self._bg_color, self._bg_color, self._bg_color))
        else:
            self._tab_dict[name].configure(background_corner_colors=None)

    def _configure_grid(self):
        """ create 3 x 4 grid system """

        self.grid_rowconfigure(0, weight=0, minsize=self._apply_widget_scaling(self._top_spacing))
        self.grid_rowconfigure(1, weight=0, minsize=self._apply_widget_scaling(self._top_button_overhang))
        self.grid_rowconfigure(2, weight=0, minsize=self._apply_widget_scaling(self._button_height - self._top_button_overhang))
        self.grid_rowconfigure(3, weight=1)

        self.grid_columnconfigure(0, weight=1)

    def _set_grid_canvas(self):
        self._canvas.grid(row=2, rowspan=2, column=0, columnspan=1, sticky="nsew")

    def _set_grid_segmented_button(self):
        """ needs to be called for changes in corner_radius """
        self._segmented_button.grid(row=1, rowspan=2, column=0, columnspan=1, padx=self._apply_widget_scaling(self._corner_radius), sticky="ns")

    def _set_grid_tab_by_name(self, name: str):
        """ needs to be called for changes in corner_radius, border_width """
        if self._border_width == 0:
            self._tab_dict[name].grid(row=3, column=0, sticky="nsew")
        else:
            self._tab_dict[name].grid(row=3, column=0, sticky="nsew",
                                      padx=self._apply_widget_scaling(max(self._corner_radius, self._border_width)),
                                      pady=self._apply_widget_scaling(max(self._corner_radius, self._border_width)))

    def _create_tab(self) -> CTkFrame:
        new_tab = CTkFrame(self,
                           fg_color=self._fg_color,
                           border_width=0,
                           corner_radius=self._corner_radius)
        return new_tab

    def _draw(self, no_color_updates: bool = False):
        if not self._canvas.winfo_exists():
            return

        requires_recoloring = self._draw_engine.draw_rounded_rect_with_border(self._apply_widget_scaling(self._current_width),
                                                                              self._apply_widget_scaling(self._current_height - self._top_spacing - self._top_button_overhang),
                                                                              self._apply_widget_scaling(self._corner_radius),
                                                                              self._apply_widget_scaling(self._border_width))

        if no_color_updates is False or requires_recoloring:
            if self._fg_color is None:
                self._canvas.itemconfig("inner_parts",
                                        fill=ThemeManager.single_color(self._bg_color, self._appearance_mode),
                                        outline=ThemeManager.single_color(self._bg_color, self._appearance_mode))
            else:
                self._canvas.itemconfig("inner_parts",
                                        fill=ThemeManager.single_color(self._fg_color, self._appearance_mode),
                                        outline=ThemeManager.single_color(self._fg_color, self._appearance_mode))

            self._canvas.itemconfig("border_parts",
                                    fill=ThemeManager.single_color(self._border_color, self._appearance_mode),
                                    outline=ThemeManager.single_color(self._border_color, self._appearance_mode))
            self._canvas.configure(bg=ThemeManager.single_color(self._bg_color, self._appearance_mode))

    def tab(self, name: str) -> CTkFrame:
        """ returns reference to the tab with given name """

        if name in self._tab_dict:
            return self._tab_dict[name]
        else:
            raise ValueError(f"CTkTabview has no tab named '{name}'")

    def insert(self, index: int, name: str):
        """ creates new tab with given name at position index """

        if name not in self._tab_dict:
            # if no tab exists, set grid for segmented button
            if len(self._tab_dict) == 0:
                self._set_grid_segmented_button()

            self._name_list.insert(index, name)
            self._tab_dict[name] = self._create_tab()
            self._segmented_button.insert(index, name)
        else:
            raise ValueError(f"CTkTabview already has tab named '{name}'")

    def add(self, name: str):
        """ appends new tab with given name """
        self.insert(len(self._tab_dict), name)

    def delete(self, name: str):
        """ deletes tab with given name """
        return