from trame.app import asynchronous
from trame.decorators import TrameApp, change
from trame.widgets import html, vuetify2 as v2

from quickview.ui.collapsible import CollapsableSection

from quickview.view_manager import ViewManager
from quickview.pipeline import EAMVisSource

import asyncio


@TrameApp()
class SliceSelection(CollapsableSection):
    def __init__(self, source: EAMVisSource, view_manager: ViewManager):
        super().__init__("Slice Selection", "show_slice")

        self.source = source
        self.views = view_manager

        style = dict(dense=True, hide_details=True)
        with self.content:
            with v2.VRow(
                classes="text-center align-center justify-center text-subtitle-1 pt-3 px-3"
            ):
                with v2.VCol(classes="text-left py-0"):
                    html.Div("Layer Midpoints")
                with v2.VCol(classes="py-0", cols=1):
                    with v2.VBtn(
                        icon=True,
                        flat=True,
                        **style,
                        click=(self.on_click_advance_middle, "[-1]"),
                    ):
                        v2.VIcon("mdi-chevron-left")
                with v2.VCol(classes="py-0", cols=1):
                    with v2.VBtn(
                        icon=True,
                        flat=True,
                        **style,
                        click=(self.on_click_advance_middle, "[1]"),
                    ):
                        v2.VIcon("mdi-chevron-right")
                with v2.VCol(classes="mr-4 py-0", cols=1):
                    v2.VCheckbox(
                        v_model=("play_lev", False),
                        off_icon="mdi-play-circle",
                        on_icon="mdi-stop",
                        classes="ma-0 pa-0",
                        **style,
                    )

            with v2.VRow(
                classes="text-center align-center justify-center text-subtitle-1 pb-3 px-3"
            ):
                with v2.VCol(cols=8, classes="py-0 pl-3"):
                    v2.VSlider(
                        v_model=("vlev", 0),
                        min=0,
                        max=("lev.length - 1",),
                        classes="py-0 pl-3",
                        **style,
                    )
                with v2.VCol(cols=4, classes="text-left py-0"):
                    html.Div(
                        "{{parseFloat(lev[vlev]).toFixed(2) + ' (k=' + String(vlev) + ')'}}"
                    )
            v2.VDivider()

            with v2.VRow(
                classes="text-center align-center justify-center text-subtitle-1 pt-3 px-3"
            ):
                with v2.VCol(classes="text-left py-0"):
                    html.Div("Layer Interfaces")
                with v2.VCol(classes="py-0", cols=1):
                    with v2.VBtn(
                        icon=True,
                        flat=True,
                        **style,
                        click=(self.on_click_advance_interface, "[-1]"),
                    ):
                        v2.VIcon("mdi-chevron-left")
                with v2.VCol(classes="py-0", cols=1):
                    with v2.VBtn(
                        icon=True,
                        flat=True,
                        **style,
                        click=(self.on_click_advance_interface, "[1]"),
                    ):
                        v2.VIcon("mdi-chevron-right")
                with v2.VCol(classes="mr-4 py-0", cols=1):
                    v2.VCheckbox(
                        v_model=("play_ilev", False),
                        off_icon="mdi-play-circle",
                        on_icon="mdi-stop",
                        classes="ma-0 pa-0",
                        **style,
                    )

            with v2.VRow(
                classes="text-center align-center justify-center text-subtitle-1 pb-3 px-3"
            ):
                with v2.VCol(cols=8, classes="py-0"):
                    v2.VSlider(
                        v_model=("vilev", 0),
                        min=0,
                        max=("ilev.length - 1",),
                        classes="py-0 pl-3",
                        **style,
                    )
                with v2.VCol(cols=4, classes="text-left py-0"):
                    html.Div(
                        "{{parseFloat(ilev[vilev]).toFixed(2) + ' (k=' + String(vilev) + ')'}}"
                    )
            v2.VDivider()

            with v2.VRow(
                classes="text-center align-center justify-center text-subtitle-1 pt-3 px-3"
            ):
                with v2.VCol(classes="text-left py-0"):
                    html.Div("Time")
                with v2.VCol(classes="py-0", cols=1):
                    with v2.VBtn(
                        icon=True,
                        flat=True,
                        **style,
                        click=(self.on_click_advance_time, "[-1]"),
                    ):
                        v2.VIcon("mdi-chevron-left")
                with v2.VCol(classes="py-0", cols=1):
                    with v2.VBtn(
                        icon=True,
                        flat=True,
                        **style,
                        click=(self.on_click_advance_time, "[1]"),
                    ):
                        v2.VIcon("mdi-chevron-right")
                with v2.VCol(classes="mr-4 py-0", cols=1):
                    v2.VCheckbox(
                        v_model=("play_time", False),
                        off_icon="mdi-play-circle",
                        on_icon="mdi-stop",
                        classes="ma-0 pa-0",
                        **style,
                    )

            with v2.VRow(
                classes="text-center align-center justify-center text-subtitle-1 pb-3 px-3"
            ):
                with v2.VCol(cols=8, classes="py-0"):
                    v2.VSlider(
                        v_model=("tstamp", 0),
                        min=0,
                        max=("timesteps.length - 1",),
                        classes="py-0 pl-3",
                        **style,
                    )
                with v2.VCol(cols=4, classes="text-left py-0"):
                    html.Div(
                        "{{parseFloat(timesteps[tstamp]).toFixed(2) + ' (t=' + String(tstamp) + ')'}}"
                    )
            v2.VDivider()

            with v2.VRow(classes="text-center align-center text-subtitle-1 pt-3 pa-2"):
                with v2.VCol(cols=3, classes="py-0"):
                    v2.VTextField(
                        v_model=("cliplong[0]",),
                        classes="py-0",
                        **style,
                    )
                with v2.VCol(cols=6, classes="py-0"):
                    html.Div("Longitude")
                with v2.VCol(cols=3, classes="py-0"):
                    v2.VTextField(
                        v_model=("cliplong[1]",),
                        classes="py-0",
                        **style,
                    )
            v2.VRangeSlider(
                v_model=("cliplong", [self.source.extents[0], self.source.extents[1]]),
                min=-180,
                max=180,
                **style,
                flat=True,
                variant="solo",
                classes="pt-2 px-6",
            )
            v2.VDivider()

            v2.VDivider(classes="mx-2")
            with v2.VRow(classes="text-center align-center text-subtitle-1 pt-3 pa-2"):
                with v2.VCol(cols=3, classes="py-0"):
                    v2.VTextField(
                        v_model=("cliplat[0]",),
                        classes="py-0",
                        **style,
                    )
                with v2.VCol(cols=6, classes="py-0"):
                    html.Div("Latitude")
                with v2.VCol(cols=3, classes="py-0"):
                    v2.VTextField(
                        v_model=("cliplat[1]",),
                        classes="py-0",
                        **style,
                    )
            v2.VRangeSlider(
                v_model=("cliplat", [self.source.extents[2], self.source.extents[3]]),
                min=-90,
                max=90,
                **style,
                flat=True,
                variant="solo",
                classes="pt-2 px-6",
            )

    @change("vlev", "vilev", "tstamp", "cliplat", "cliplong")
    def update_pipeline_interactive(self, **kwargs):
        lev = self.state.vlev
        ilev = self.state.vilev
        tstamp = self.state.tstamp
        long = self.state.cliplong
        lat = self.state.cliplat
        self.source.UpdateLev(lev, ilev)
        self.source.UpdateTimeStep(tstamp)
        self.source.ApplyClipping(long, lat)
        self.source.UpdatePipeline()
        self.views.step_update_existing_views()
        self.views.reset_views()

    def on_click_advance_middle(self, diff):
        current = self.state.vlev
        update = current + diff
        # if update >= 0 and update <= len(self.state.lev) - 1:
        self.state.vlev = update % len(self.state.lev)

    @change("play_lev")
    @asynchronous.task
    async def play_lev(self, **kwargs):
        state = self.state
        while state.play_lev:
            state.play_ilev = False
            state.play_time = False
            with state:
                self.on_click_advance_middle(1)
                await asyncio.sleep(0.1)

    def on_click_advance_interface(self, diff):
        current = self.state.vilev
        update = current + diff
        # if update >= 0 and update <= len(self.state.ilev) - 1:
        self.state.vilev = update % len(self.state.ilev)

    @change("play_ilev")
    @asynchronous.task
    async def play_ilev(self, **kwargs):
        state = self.state
        while state.play_ilev:
            state.play_lev = False
            state.play_time = False
            with state:
                self.on_click_advance_interface(1)
                await asyncio.sleep(0.1)

    def on_click_advance_time(self, diff):
        current = self.state.tstamp
        update = current + diff
        # if update >= 0 and update <= len(self.state.timesteps) - 1:
        self.state.tstamp = update % len(self.state.timesteps)

    @change("play_time")
    @asynchronous.task
    async def play_time(self, **kwargs):
        state = self.state
        while state.play_time:
            state.play_lev = False
            state.play_ilev = False
            with state:
                self.on_click_advance_time(1)
                await asyncio.sleep(0.1)
