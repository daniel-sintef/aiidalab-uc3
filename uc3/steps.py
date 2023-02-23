"""The AiiDAlab App steps."""
import json
import uuid
import logging
import subprocess
from copy import copy
from pathlib import Path

import ipywidgets as ipw
import shortuuid
import traitlets
from aiida.engine import ProcessState, submit
from aiida.orm import ArrayData, Code, Dict, Str, ProcessNode, load_code
from aiida.plugins import CalculationFactory
from aiidalab_widgets_base import (
    AiidaNodeViewWidget,
    ProcessMonitor,
    ProcessNodesTreeWidget,
    WizardAppWidgetStep,
)

from uc3.base_widgets_mod import ComputationalResourcesWidget

STYLE = {"description_width": "180px"}
LAYOUT = {"width": "400px"}


class UploadSshKey(ipw.VBox, WizardAppWidgetStep):
    def __init__(self, **kwargs):
        self._inp_private_key = ipw.FileUpload(
            accept="",
            layout=LAYOUT,
            style=STYLE,
            description="Choose Private key",
            multiple=False,
        )
        self._inp_private_key.observe(self._set_private_key, ["value"])
        self._key_fname = None
        self._key_content = None

        self._upload_button = ipw.Button(
            description="Upload Key",
            disabled=True,
        )
        self._upload_button.on_click(self._upload_key_press)
        self._logger = kwargs.pop("logger", logging.getLogger("aiidalab_mp_uc3"))

        text_description = ipw.HTML(
            value="   Key must be called aiidalabkey. \n Skip Manually to the next step if you have already uploaded a key",
        )

        children = [text_description, self._inp_private_key, self._upload_button]
        super().__init__(children, **kwargs)

    def _set_private_key(self, _=None):
        self._logger.info("F: _set_private_key")
        # unwrap private key file and setting temporary private_key content
        private_key_abs_fname, private_key_content = self._private_key
        if private_key_abs_fname is None:  # check private key file
            self.message = "Please upload your private key file."
            return False

        self._upload_button.disabled = False

    @property
    def _private_key(self):
        """Unwrap private key file and setting filename and file content."""
        self._logger.info("F: _private_key START")

        if self._inp_private_key.value:
            (fname, _value), *_ = self._inp_private_key.value.items()
            content = copy(_value["content"])
            self._inp_private_key.value.clear()
            # self._inp_private_key._counter = 0  # pylint: disable=protected-access
            self._logger.info("F: _private_key END")
            self._key_fname = fname
            self._key_content = content
            return fname, content

        return None, None

    def _add_private_key(self, private_key_fname, private_key_content):
        """
        param private_key_fname: string
        param private_key_content: bytes
        """
        fpath = Path.home() / ".ssh" / private_key_fname
        if fpath.exists():
            # if file already exist and has the same content
            if fpath.read_bytes() == private_key_content:
                return fpath.name

            fpath = fpath / "_" / shortuuid.uuid()
        fpath.write_bytes(private_key_content)

        fpath.chmod(0o600)

        return fpath

    def _upload_key_press(self, _=None):
        # # Write private key in ~/.ssh/ and use the name of upload file,
        # if exist, generate random string and append to filename then override current name.
        # self._add_private_key(private_key_abs_fname, private_key_content)
        self._logger.info("F: _upload_key_press")

        try:
            self._add_private_key(self._key_fname, self._key_content)
        except Exception as e:
            self._logger.exception(e)
        self.state = self.State.SUCCESS


class InstallComputerAndCode(ipw.VBox, WizardAppWidgetStep):
    def __init__(self, **kwargs):

        self._install_codecomputer_button = ipw.Button(
            description="Click to Install Code & Computer",
            layout=ipw.Layout(width="50%"),
        )
        self._install_codecomputer_button.on_click(self._install_codecomputer)
        self._logger = kwargs.pop("logger", logging.getLogger("aiidalab_mp_uc3"))

        children = [self._install_codecomputer_button]
        super().__init__(children, **kwargs)

    def _install_codecomputer(self, _=None):
        self._logger.info("F: _install_codecomputer")
        try:
            self._logger.info("F: _install_codecomputer, skip start")
            load_code("FSP")
            self.message = "Code already installed!"
            self.state = self.State.SUCCESS
            self._logger.info("F: _install_codecomputer, skip success!")
            return
        except Exception:
            pass

        self._logger.info("F: _install_codecomputer, full install")
        self.message = "Installing Computer"
        keygen_cmd = [
            "sh",
            "/home/jovyan/apps/aiidalab-uc3/setup_droplet.sh",
        ]
        subprocess.run(keygen_cmd, capture_output=True)
        self.state = self.State.SUCCESS


class ExitMessage(ipw.VBox, WizardAppWidgetStep):
    def __init__(self, **kwargs):

        text_description = ipw.HTML(
            value='   Installation done, you can now go to the <a href="uc3.ipynb">UC3 app</a>! ',
        )

        children = [text_description]
        super().__init__(children, **kwargs)


class ComputerCodeSetupStep(ipw.VBox, WizardAppWidgetStep):
    """Setup AiiDA Computer and Code."""

    disabled = traitlets.Bool()
    mpuc3_code = traitlets.Instance(Code, allow_none=True)

    def __init__(self, **kwargs) -> None:

        # create descritpive text
        text_description = ipw.HTML(
            value="   Use of FSP@unity is recommened. If you do not see it in the list run the <a href=\"install_uc3.ipynb\">'Install UC3' app</a> first!",
        )
        # create code selection field
        self.computer_code_selector = ComputationalResourcesWidget(
            default_calc_job_plugin="dummy_marketuc3"
        )
        self.computer_code_selector.observe(self._set_code_value, ["value"])

        items_layout = ipw.Layout(padding="20px", align_items="stretch", width="75%")

        # create confirmation button
        self.confirm_button = ipw.Button(
            description="Confirm choice",
            disabled=True,
        )
        self.confirm_button.on_click(self._update_state)

        # setup widget
        super().__init__(
            (text_description, self.computer_code_selector, self.confirm_button),
            layout=items_layout,
            **kwargs,
        )

    def _set_code_value(self, _) -> None:
        self.confirm_button.disabled = not bool(self.computer_code_selector.value)
        self.mpuc3_code = load_code(self.computer_code_selector.value)

    def reset(self):
        with self.hold_trait_notifications():
            self.style.value = None
            self.toppings.value = []
            self.mpuc3_code = None

    @traitlets.default("state")
    def _default_state(self):
        return self.State.READY

    def _update_state(self, _=None) -> None:
        """Update the step's state based on traits and widget state.

        The step state influences the representation of the step (e.g. the "icon") and
        whether the "Next step" button is enabled.
        """

        if self.mpuc3_code:
            # The configuration is non-empty, we can move on to the next step.
            self.state = self.State.SUCCESS
        else:
            # In all other cases the step is always considered to be in the "init" state.
            self.state = self.State.READY

    @traitlets.observe("state")
    def _observe_state(self, change):
        with self.hold_trait_notifications():
            self.disabled = change["new"] == self.State.SUCCESS
            self.confirm_button.disabled = change["new"] is not self.State.CONFIGURED

    @traitlets.observe("disabled")
    def _observe_disabled(self, change):
        with self.hold_trait_notifications():
            for child in self.children:
                child.disabled = change["new"]


class ConfigureUserInputStep(ipw.VBox, WizardAppWidgetStep):

    disabled = traitlets.Bool()
    user_inputs = traitlets.Dict(allow_none=True)

    def __init__(self, **kwargs) -> None:
        # create fields to enter user values
        self.description_label_default = [
            ["ATSBcons", "ATSB Concentration (mol/l)", 0],
            ["Precurfr", "Precursor Volume Flow Rate (ml/min)", 0],
            ["Dispfr", "Dispersion Volume Flow Rate (l/min)", 0],
            ["Pilotch4fr", "Pilot Methane Volume Flow Rate (l/min)", 0],
            ["Piloto2fr", "Pilot Oxygen Volume Flow Rate (l/min)", 0],
            ["Fanrate", "Fan Extraction Volume Flow Rate (m3/h)", 0],
        ]

        def _setup_input_entry(description, init_value):
            form_item_layout = ipw.Layout(justify_content="space-between")
            form = ipw.HBox(
                [ipw.Label(value=description), ipw.FloatText(value=init_value)],
                layout=form_item_layout,
            )
            return form

        items_layout = ipw.Layout(padding="20px", align_items="stretch", width="75%")
        self.input_widgets = [
            _setup_input_entry(x[1], x[2]) for x in self.description_label_default
        ]

        # create confirmation button
        self.confirm_button = ipw.Button(
            description="Confirm user_inputs",
        )
        self.confirm_button.on_click(self._confirm_user_inputs)
        self.observe(self._update_state, ["user_inputs"])

        # setup widget
        super().__init__(
            self.input_widgets + [self.confirm_button], layout=items_layout, **kwargs
        )

    def _confirm_user_inputs(self, _) -> None:
        label_remapdict = {x[1]: x[0] for x in self.description_label_default}
        user_inputs = {
            label_remapdict[x.children[0].value]: x.children[1].value
            for x in self.input_widgets
        }

        self.user_inputs = user_inputs

    def reset(self):
        with self.hold_trait_notifications():
            self.style.value = None
            self.toppings.value = []
            self.user_inputs = {}

    @traitlets.default("state")
    def _default_state(self):
        return self.State.READY

    def _update_state(self, _=None):
        """Update the step's state based on traits and widget state.

        The step state influences the representation of the step (e.g. the "icon") and
        whether the "Next step" button is enabled.
        """

        if self.user_inputs:
            # The configuration is non-empty, we can move on to the next step.
            self.state = self.State.SUCCESS
        else:
            # In all other cases the step is always considered to be in the "init" state.
            self.state = self.State.READY

    @traitlets.observe("state")
    def _observe_state(self, change):
        with self.hold_trait_notifications():
            self.disabled = change["new"] == self.State.SUCCESS
            self.confirm_button.disabled = change["new"] is not self.State.CONFIGURED

    @traitlets.observe("disabled")
    def _observe_disabled(self, change):
        with self.hold_trait_notifications():
            for child in self.children:
                child.disabled = change["new"]


class ConfirmUserInputStep(ipw.VBox, WizardAppWidgetStep):

    process = traitlets.Instance(ProcessNode, allow_none=True)
    submit = traitlets.Bool()
    job_uuid = str(uuid.uuid4())
    job_uuidhtml = ipw.HTML(
        value="<h4>Please email your SINTEF contact with the following UUID: {}</h4>".format(job_uuid),
    )
    user_inputs = traitlets.Dict(allow_none=True)
    mpuc3_code = traitlets.Instance(Code, allow_none=True)

    def __init__(self, **kwargs):
        self.userinputs_label = ipw.HTML()

        # The second step has only function: executing the order by clicking on this button.
        self.submitcalc_button = ipw.Button(description="Submit calculation")
        self.submitcalc_button.on_click(self.submit_calc)
        super().__init__([self.userinputs_label, self.job_uuidhtml, self.submitcalc_button], **kwargs)

    def reset(self):
        self.submit = None

    @traitlets.observe("user_inputs")
    def _observe_configuration(self, change):
        "Format and show the user inputs."
        if change["new"]:
            self.userinputs_label.value = f"<h4>Configuration</h4><pre>{json.dumps(change['new'], indent=2)}</pre>"
        else:
            self.userinputs_label.value = (
                "<h4>Configuration</h4>[Please configure user inputs]"
            )

    def submit_calc(self, button):
        fluent_calcjob = CalculationFactory("dummy_marketuc3")
        fluentcalc_builder = fluent_calcjob.get_builder()
        fluentcalc_builder.user_inputs = Dict(dict=self.user_inputs)
        fluentcalc_builder.code = self.mpuc3_code
        fluentcalc_builder.job_uuid = Str(self.job_uuid)

        # Not sure how to get around hard coding this...
        fluentcalc_builder.metadata.options.resources = {
            "num_machines": 1,
            "num_mpiprocs_per_machine": 20,
        }

        # fluentcalc_builder.metadata.dry_run = True
        self.process = submit(fluentcalc_builder)
        self.submit = True
        self._update_state()
        return

    def _update_state(self, _=None):
        "Update the step's state based on the order status and configuration traits."
        if self.submit:  # the order has been submitted
            self.state = self.State.SUCCESS
        elif self.user_inputs:  # the order can be submitted
            self.state = self.State.CONFIGURED
        else:
            self.state = self.State.INIT

    @traitlets.observe("state")
    def _observe_state(self, change):
        """Enable the order button once the step is in the "configured" state."""
        # self.submitcalc_button.disabled = change["new"] != self.State.CONFIGURED


class MonitorProcessStep(ipw.VBox, WizardAppWidgetStep):

    process = traitlets.Instance(ProcessNode, allow_none=True)
    output = traitlets.Instance(ArrayData, allow_none=True)

    def __init__(self, **kwargs):
        self.process_tree = ProcessNodesTreeWidget()
        ipw.dlink((self, "process"), (self.process_tree, "value"),
                  transform=lambda x: x.uuid if x is not None else None)

        self.node_view = AiidaNodeViewWidget(layout={"width": "auto", "height": "auto"})
        ipw.dlink(
            (self.process_tree, "selected_nodes"),
            (self.node_view, "node"),
            transform=lambda nodes: nodes[0] if nodes else None,
        )
        self.process_status = ipw.VBox(children=[self.process_tree, self.node_view])

        # Setup process monitor
        self.process_monitor = ProcessMonitor(
            timeout=0.2,
            callbacks=[
                self.process_tree.update,
                self._update_state,
            ],
        )
        ipw.dlink((self, "process"), (self.process_monitor, "value"),
                  transform=lambda x: x.uuid if x is not None else None)

        self._logger = kwargs.pop("logger", logging.getLogger("aiidalab_mp_uc3"))

        super().__init__([self.process_status], **kwargs)

    def can_reset(self):
        # Do not allow reset while process is running.
        return self.state is not self.State.ACTIVE

    def reset(self):
        self.process = None

    def _update_state(self):
        self._logger.info("M: start")
        if self.process is None:
            self.state = self.State.INIT
        else:
            process_state = self.process.process_state
            if process_state in (
                ProcessState.CREATED,
                ProcessState.RUNNING,
                ProcessState.WAITING,
            ):
                self._logger.info("M: ACTIVE")
                self.state = self.State.ACTIVE
            elif process_state in (ProcessState.EXCEPTED, ProcessState.KILLED):
                self._logger.info("M: KILLED")
                self.state = self.State.FAIL
            elif process_state is ProcessState.FINISHED:
                self._logger.info("M: SUCCESS 1")
                self.state = self.State.SUCCESS
                self._logger.info("M: SUCCESS 2")
                self._logger.info(self.process)
                try:
                    self.output = self.process.outputs.output
                except Exception as e:
                    self._logger.exception(e)

    @traitlets.observe("process")
    def _observe_process(self, change):
        self._logger.info("MONITOR STATE %s", self.state)
        self._update_state()


class DisplayFinalOutput(ipw.VBox, WizardAppWidgetStep):

    output = traitlets.Instance(ArrayData, allow_none=True)

    def __init__(self, **kwargs):
        self.final_output = ipw.HTML()

        super().__init__([self.final_output], **kwargs)

    @traitlets.observe("output")
    def _call_observe(self, change):
        self._observe_configuration(self, change)

    def _observe_configuration(self, _, change):
        "Format and show the user inputs."
        if change["new"]:
            output = self.output
            area_flux = float(output.get_array("area_flux"))
            volume_flux = float(output.get_array("volume_flux"))
            particle_size = float(output.get_array("particle_size"))
            display_dict = {
                "Area Flux": area_flux,
                "Volume Flux": volume_flux,
                "Particle Size": particle_size,
            }
            self.final_output.value = (
                f"<h4>Configuration</h4><pre>{json.dumps(display_dict, indent=2)}</pre>"
            )
        else:
            self.final_output.value = (
                "<h4>Configuration</h4>[Please configure user inputs]"
            )
