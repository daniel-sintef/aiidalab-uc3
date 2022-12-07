"""Modifications to AiiDAlab base widgets."""
import os
from copy import deepcopy
from pathlib import Path

import ipywidgets as ipw
import requests
import traitlets
import yaml
from aiidalab_widgets_base import (
    ComputationalResourcesWidget as OriginalComputationalResourcesWidget,
)
from aiidalab_widgets_base.computational_resources import (
    AiidaCodeSetup,
    AiidaComputerSetup,
    SshComputerSetup,
)
from aiidalab_widgets_base.databases import (
    ComputationalResourcesDatabaseWidget as OriginalComputationalResourcesDatabaseWidget,
)
from aiidalab_widgets_base.utils import StatusHTML


class ComputationalResourcesDatabaseWidget(
    OriginalComputationalResourcesDatabaseWidget
):
    """Custom version for ComputationalResourcesDatabaseWidget."""

    def update(self, _=None) -> None:
        """Overload the `update()` method to use custom registry."""
        with self.hold_trait_notifications():
            aiida_code_registry_database: dict = requests.get(
                "https://aiidateam.github.io/aiida-code-registry/database.json"
            ).json()

            app_database = {}
            for computer in (
                folder.path
                for folder in os.scandir(
                    Path(__name__).resolve().parent / "setup_files"
                )
            ):
                computer_path = Path(computer).resolve()
                code_setup = yaml.safe_load(
                    (computer_path / "code_setup.yml").read_bytes()
                )
                app_database[computer_path.name] = {
                    "computer-configure": yaml.safe_load(
                        (computer_path / "computer_configure.yml").read_bytes()
                    ),
                    "computer-setup": yaml.safe_load(
                        (computer_path / "computer_setup.yml").read_bytes()
                    ),
                    f"{code_setup['label']}-{computer_path.name}": code_setup,
                }
                app_database["default"] = computer_path.name
            app_database = {"dummy_marketuc3": app_database}

            database = deepcopy(aiida_code_registry_database)
            database.update(app_database)

            self.database = (
                self.clean_up_database(database, self.input_plugin)
                if self.input_plugin
                else database
            )


class ComputationalResourcesWidget(OriginalComputationalResourcesWidget):
    """Custom version for ComputationalResourcesWidget."""

    def __init__(self, description="Select code:", path_to_root="../", **kwargs):
        """Dropdown for Codes for one input plugin.

        description (str): Description to display before the dropdown.
        """
        self.output = ipw.HTML()
        self.setup_message = StatusHTML()
        self.code_select_dropdown = ipw.Dropdown(
            description=description, disabled=True, value=None
        )
        traitlets.link((self, "codes"), (self.code_select_dropdown, "options"))
        traitlets.link((self.code_select_dropdown, "value"), (self, "value"))

        self.observe(
            self.refresh, names=["allow_disabled_computers", "allow_hidden_codes"]
        )

        self.btn_setup_new_code = ipw.ToggleButton(description="Setup new code")
        self.btn_setup_new_code.observe(self._setup_new_code, "value")

        self._setup_new_code_output = ipw.Output(layout={"width": "500px"})

        children = [
            ipw.HBox([self.code_select_dropdown, self.btn_setup_new_code]),
            self._setup_new_code_output,
            self.output,
        ]
        super(OriginalComputationalResourcesWidget, self).__init__(
            children=children, **kwargs
        )

        # Setting up codes and computers.
        self.comp_resources_database = ComputationalResourcesDatabaseWidget(
            input_plugin=self.input_plugin
        )

        self.ssh_computer_setup = SshComputerSetup()
        ipw.dlink(
            (self.ssh_computer_setup, "message"),
            (self.setup_message, "message"),
        )

        ipw.dlink(
            (self.comp_resources_database, "ssh_config"),
            (self.ssh_computer_setup, "ssh_config"),
        )

        self.aiida_computer_setup = AiidaComputerSetup()
        ipw.dlink(
            (self.aiida_computer_setup, "message"),
            (self.setup_message, "message"),
        )
        ipw.dlink(
            (self.comp_resources_database, "computer_setup"),
            (self.aiida_computer_setup, "computer_setup"),
        )

        # Set up AiiDA code.
        self.aiida_code_setup = AiidaCodeSetup()
        ipw.dlink(
            (self.aiida_code_setup, "message"),
            (self.setup_message, "message"),
        )
        ipw.dlink(
            (self.comp_resources_database, "code_setup"),
            (self.aiida_code_setup, "code_setup"),
        )
        self.aiida_code_setup.on_setup_code_success(self.refresh)

        # After a successfull computer setup the codes widget should be refreshed.
        # E.g. the list of available computers needs to be updated.
        self.aiida_computer_setup.on_setup_computer_success(
            self.aiida_code_setup.refresh
        )

        # Quick setup.
        quick_setup_button = ipw.Button(description="Quick Setup")
        quick_setup_button.on_click(self.quick_setup)
        quick_setup = ipw.VBox(
            children=[
                self.ssh_computer_setup.username,
                quick_setup_button,
                self.aiida_code_setup.setup_code_out,
            ]
        )

        # Detailed setup.
        detailed_setup = ipw.Accordion(
            children=[
                self.ssh_computer_setup,
                self.aiida_computer_setup,
                self.aiida_code_setup,
            ]
        )
        detailed_setup.set_title(0, "Set up password-less SSH connection")
        detailed_setup.set_title(1, "Set up a computer in AiiDA")
        detailed_setup.set_title(2, "Set up a code in AiiDA")

        self.output_tab = ipw.Tab(children=[quick_setup, detailed_setup])
        self.output_tab.set_title(0, "Quick Setup")
        self.output_tab.set_title(1, "Detailed Setup")

        self.refresh()
