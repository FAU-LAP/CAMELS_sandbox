import requests
from ophyd import Signal, SignalRO, Device
from PySide6.QtWidgets import QLabel, QLineEdit


from .CAMELS_sandbox import SandboxServer
from nomad_camels.main_classes.device_class import Connection_Config

sandboxes = {}


class Demo_Server_Signal(Signal):
    """
    A class to create a signal that can be used to communicate with the demo server
    """

    def __init__(
        self,
        name,
        value=0.0,
        timestamp=None,
        parent=None,
        labels=None,
        kind="hinted",
        tolerance=None,
        rtolerance=None,
        metadata=None,
        cl=None,
        attr_name="",
        parameter_name="",
        demo_server_port=8080,
        parameter_type="float",
    ):
        super().__init__(
            name=name,
            value=value,
            timestamp=timestamp,
            parent=parent,
            labels=labels,
            kind=kind,
            tolerance=tolerance,
            rtolerance=rtolerance,
            metadata=metadata,
            cl=cl,
            attr_name=attr_name,
        )
        self.parameter_name = parameter_name
        if parameter_type == "str":
            self.parameter_type = str
        elif parameter_type == "float":
            self.parameter_type = float
        elif parameter_type == "int":
            self.parameter_type = int
        elif parameter_type == "bool":
            self.parameter_type = bool
        else:
            self.parameter_type = parameter_type
        self.url = None
        self.set_port(demo_server_port)

    def set_port(self, demo_server_port, demo_server_host="localhost"):

        if demo_server_port is None:
            self.url = f"http://{demo_server_host}/"
        else:
            self.url = f"http://{demo_server_host}:{demo_server_port}/"

    def put(self, value, *args, timestamp=None, force=False, metadata=None, **kwargs):
        """
        A function to put a value to the server
        """
        if self.parameter_type:
            value = self.parameter_type(value)
        result = requests.get(self.url, params={self.parameter_name: value})
        if result.status_code != 200:
            raise ConnectionError(result.text)
        super().put(
            value, *args, timestamp=timestamp, force=force, metadata=metadata, **kwargs
        )

    def describe(self):
        """Add "Demo Server" as source to the description of the signal."""
        info = super().describe()
        info[self.name].update({"source": "Demo Server"})
        return info


class Demo_Server_SignalRO(SignalRO):
    """
    A class to create a signal that can be used to communicate with the demo server
    """

    def __init__(
        self,
        name,
        value=0.0,
        timestamp=None,
        parent=None,
        labels=None,
        kind="hinted",
        tolerance=None,
        rtolerance=None,
        metadata=None,
        cl=None,
        attr_name="",
        parameter_name="",
        demo_server_port=8080,
        parameter_type="float",
    ):
        super().__init__(
            name=name,
            value=value,
            timestamp=timestamp,
            parent=parent,
            labels=labels,
            kind=kind,
            tolerance=tolerance,
            rtolerance=rtolerance,
            metadata=metadata,
            cl=cl,
            attr_name=attr_name,
        )
        self.parameter_name = parameter_name
        if parameter_type == "str":
            self.parameter_type = str
        elif parameter_type == "float":
            self.parameter_type = float
        elif parameter_type == "int":
            self.parameter_type = int
        elif parameter_type == "bool":
            self.parameter_type = bool
        else:
            self.parameter_type = parameter_type
        self.url = None
        self.set_port(demo_server_port)

    def set_port(self, demo_server_port, demo_server_host="localhost"):
        if demo_server_port is None:
            self.url = f"http://{demo_server_host}/"
        else:
            self.url = f"http://{demo_server_host}:{demo_server_port}/"

    def get(self):
        """
        A function to get a value from the server
        """
        result = requests.get(self.url, params={self.parameter_name: ""})
        if result.status_code != 200:
            raise ConnectionError(result.text)
        value = result.text
        if self.parameter_type:
            value = self.parameter_type(value)
        self._readback = value
        return super().get()

    def describe(self):
        """Add "Demo Server" as source to the description of the signal."""
        info = super().describe()
        info[self.name].update({"source": "Demo Server"})
        return info


class Demo_Server_Device(Device):
    """
    A class to create a device that can be used to communicate with the demo server
    """

    def __init__(
        self,
        prefix="",
        *,
        name,
        kind=None,
        read_attrs=None,
        configuration_attrs=None,
        parent=None,
        demo_server_port=8080,
        demo_server_host="localhost",
        **kwargs,
    ):
        super().__init__(
            prefix=prefix,
            name=name,
            kind=kind,
            read_attrs=read_attrs,
            configuration_attrs=configuration_attrs,
            parent=parent,
            **kwargs,
        )
        if name == "test":
            return
        self.demo_server_port = demo_server_port
        self.demo_server_host = demo_server_host
        if self.demo_server_port:
            for comp in self.walk_signals():
                item = comp.item
                if isinstance(item, (Demo_Server_Signal, Demo_Server_SignalRO)):
                    item.set_port(self.demo_server_port, self.demo_server_host)

        global sandboxes
        demo_name = f"{self.demo_server_host}_{self.demo_server_port}"
        if demo_name not in sandboxes:
            sandboxes[demo_name] = SandboxServer(
                self.demo_server_host, self.demo_server_port
            )
        sandboxes[demo_name].add_using_instrument()

    def finalize_steps(self):
        """
        A function to finalize the steps of the device
        """
        global sandboxes
        demo_name = f"{self.demo_server_host}_{self.demo_server_port}"
        if demo_name in sandboxes:
            sandboxes[demo_name].remove_using_instrument()
            if sandboxes[demo_name].n_using_instruments == 0:
                sandboxes.pop(demo_name)


class ServerConnection(Connection_Config):
    def __init__(self, parent=None):
        super().__init__(parent)

        label_host = QLabel("Host:")
        self.line_edit_host = QLineEdit("127.0.0.1")
        label_port = QLabel("Port:")
        self.line_edit_port = QLineEdit("8182")

        self.layout().addWidget(label_host, 0, 0)
        self.layout().addWidget(self.line_edit_host, 0, 1)
        self.layout().addWidget(label_port, 1, 0)
        self.layout().addWidget(self.line_edit_port, 1, 1)

    def load_settings(self, settings_dict):
        super().load_settings(settings_dict)
        if "connection" in settings_dict:
            settings_dict = settings_dict["connection"]
        if "demo_server_host" in settings_dict:
            self.line_edit_host.setText(settings_dict["demo_server_host"])
        if "demo_server_port" in settings_dict:
            self.line_edit_port.setText(str(settings_dict["demo_server_port"]))

    def get_settings(self):
        settings_dict = super().get_settings()
        settings_dict["demo_server_host"] = self.line_edit_host.text()
        settings_dict["demo_server_port"] = int(self.line_edit_port.text())
        return settings_dict
