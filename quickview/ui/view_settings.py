from trame.widgets import vuetify2 as v2, html
from trame.decorators import TrameApp

from quickview.utilities import EventType


@TrameApp()
class ViewProperties(v2.VMenu):
    def __init__(self, apply=None, update=None, reset=None, **kwargs):
        super().__init__(
            transition="slide-y-transition",
            close_on_content_click=False,
            persistent=True,
            no_click_animation=True,
            **kwargs,
        )
        with self:
            with v2.Template(v_slot_activator="{ on, attrs }"):
                with v2.VBtn(
                    icon=True,
                    outlined=True,
                    classes="pa-1",
                    style="background: white;",
                    v_bind="attrs",
                    v_on="on",
                ):
                    v2.VIcon("mdi-cog")
            style = dict(dense=True, hide_details=True)
            with v2.VCard(
                classes="overflow-hidden pa-2",
                rounded="lg",
            ):
                with v2.VCardText(classes="pa-2"):
                    v2.VSelect(
                        label="Color Map",
                        v_model=("varcolor[idx]",),
                        items=("colormaps",),
                        outlined=True,
                        change=(
                            apply,
                            f"[idx, {EventType.COL.value}, $event]",
                        ),
                        **style,
                    )
                    html.Div("Color Map Options", classes="pt-2")
                    with v2.VRow():
                        with v2.VCol():
                            v2.VCheckbox(
                                label="Log Scale",
                                v_model=("uselogscale[idx]",),
                                change=(
                                    apply,
                                    f"[idx, {EventType.LOG.value}, $event]",
                                ),
                                **style,
                            )
                        with v2.VCol():
                            v2.VCheckbox(
                                label="Revert Colors",
                                v_model=("invert[idx]",),
                                change=(
                                    apply,
                                    f"[idx, {EventType.INV.value}, $event]",
                                ),
                                **style,
                            )
                    html.Div("Value Range", classes="pt-2")
                    with v2.VRow():
                        with v2.VCol():
                            v2.VTextField(
                                v_model=("varmin[idx]",),
                                label="min",
                                outlined=True,
                                change=(
                                    update,
                                    "[idx, 'min', $event]",
                                ),
                                style="height=50px",
                                **style,
                            )
                        with v2.VCol():
                            v2.VTextField(
                                v_model=("varmax[idx]",),
                                label="max",
                                outlined=True,
                                change=(
                                    update,
                                    "[idx, 'max', $event]",
                                ),
                                style="height=50px",
                                **style,
                            )
                    with html.Div(classes="pt-2 align-center text-center"):
                        v2.VBtn(
                            "Reset Colors to Data Range",
                            outlined=True,
                            style="background-color: gray; color: white;",
                            click=(
                                reset,
                                "[idx]",
                            ),
                        )


@TrameApp()
class ViewControls(v2.VCard):
    def __init__(self, zoom=None, move=None, **kwargs):
        super().__init__(
            classes="overflow-hidden pa-0 ma-2",
            rounded="lg",
            **kwargs,
        )
        with self:
            """
            with v2.Template(v_slot_activator="{ on, attrs }"):
                with v2.VBtn(
                    icon=True,
                    outlined=True,
                    classes="pa-1",
                    style="background: white;",
                    v_bind="attrs",
                    v_on="on",
                ):
                    v2.VIcon("mdi-camera")
            style = dict(dense=True, hide_details=True)
            """
            style = dict(
                icon=True,
                flat=True,
                outlined=False,
                density="compact",
                hide_details=True,
                height="30px",
                width="30px",
            )
            with v2.VCardText(classes="pa-0", style="opacity: 80%"):
                with v2.VTooltip(bottom=True):
                    with html.Template(v_slot_activator="{ on, attrs }"):
                        with html.Div(
                            v_bind="attrs",
                            v_on="on",
                        ):
                            with v2.VBtn(
                                **style,
                                click=(zoom, "['in']"),
                            ):
                                v2.VIcon("mdi-magnify-plus", large=True)
                            v2.VDivider(vertical=True)
                            with v2.VBtn(
                                **style,
                                click=(zoom, "['out']"),
                            ):
                                v2.VIcon("mdi-magnify-minus", large=True)
                            v2.VDivider(vertical=True)
                            with v2.VBtn(
                                **style,
                                click=(move, "['up']"),
                            ):
                                v2.VIcon("mdi-arrow-up-thick", large=True)
                            v2.VDivider(vertical=True)
                            with v2.VBtn(
                                **style,
                                click=(move, "['down']"),
                            ):
                                v2.VIcon("mdi-arrow-down-thick", large=True)
                            v2.VDivider(vertical=True)
                            with v2.VBtn(
                                **style,
                                click=(move, "['left']"),
                            ):
                                v2.VIcon("mdi-arrow-left-thick", large=True)
                            v2.VDivider(vertical=True)
                            with v2.VBtn(
                                **style,
                                click=(move, "['right']"),
                            ):
                                v2.VIcon("mdi-arrow-right-thick", large=True)
                    html.Span("View Camera Controls")
