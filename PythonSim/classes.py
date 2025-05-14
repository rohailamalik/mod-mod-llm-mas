from __future__ import annotations

class Port:
    def __init__(self, name: str):
        self.name = name

    def connect_port(self, other):
        raise NotImplementedError("Subclasses must implement connect method.")

class PowerPort(Port):
    def __init__(self, name: str):
        super().__init__(name)

        self.effort = 0.0
        self.flow = 0.0

        self.connected: PowerPort | None = None

    def connect_port(self, other: PowerPort):
        if not isinstance(other, PowerPort):
            raise TypeError(f"[{self.name}] can only connect to another PowerPort.")
        self.connected = other

    def write_effort(self, value: float):
        self.effort = value

    def write_flow(self, value: float):
        self.flow = value

    def read_effort(self) -> float:
        if self.connected:
            return self.connected.effort
        else: raise TypeError(f"[{self.name}] Read error: port not connected.")

    def read_flow(self) -> float:
        if self.connected:
            return self.connected.flow
        else: raise TypeError(f"[{self.name}] Read error: port not connected.")

class SignalPort(Port):
    def __init__(self, name: str):
        super().__init__(name)

        self.signal = 0.0
        self.connected: SignalPort | None = None

    def connect_port(self, other: SignalPort):
        if not isinstance(other, SignalPort):
            raise TypeError(f"[{self.name}] can only connect to another SignalPort.")
        self.connected = other

    def write_signal(self, value: float):
        self.signal = value

    def read_signal(self) -> float:
        if self.connected:
            return self.connected.signal
        else: raise TypeError(f"[{self.name}] Read error: port not connected.")

class Component:
    def __init__(self, name: str):
        self.name = name
        self.ports: list[Port] = []
        self.variables: dict[str, callable] = {}
        self.signal_ports: dict[str, SignalPort] = {}

    def add_port(self, port: Port):
        self.ports.append(port)

    def get_ports(self):
        return self.ports

    def add_variable(self, name: str, value_getter: callable):
        qualified_name = f"{self.name}_{name}"
        self.variables[qualified_name] = value_getter

        # Automatically create signal port for this variable
        sig_port = SignalPort(qualified_name)
        self.signal_ports[qualified_name] = sig_port
        self.ports.append(sig_port)

    def update_signal_ports(self):
        for name, port in self.signal_ports.items():
            port.write_signal(self.variables[name]())

    def get_logged_variables(self):
        return self.variables

    def step(self, dt: float):
        raise NotImplementedError("Each component must implement the step method.")

class System:
    def __init__(self):
        self.components: list[Component] = []
        self.logs: dict[str, list[float]] = {"time": []}

    def add_component(self, comp: Component):
        self.components.append(comp)

    def connect(self, port1: Port, port2: Port):
        port1.connect_port(port2)
        port2.connect_port(port1)
        print(f"[{port1.name}] and [{port2.name}] connected")

    def initialize_logging(self):
        for comp in self.components:
            for name in comp.get_logged_variables():
                self.logs[name] = []

    def log_step(self, t: float):
        self.logs["time"].append(t)
        for comp in self.components:
            for name, getter in comp.get_logged_variables().items():
                try:
                    self.logs[name].append(getter())
                except:
                    self.logs[name].append(None)

    def step(self, dt: float):
        for comp in self.components:
            comp.step(dt)
            comp.update_signal_ports()

    def simulate(self, t_end: float, dt: float):
        self.initialize_logging()
        t = 0.0
        while t <= t_end:
            self.step(dt)
            self.log_step(t)
            t += dt
        print("Simulation complete.")
        return self.logs
