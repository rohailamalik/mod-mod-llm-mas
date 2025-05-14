import sys
import importlib.util
import json
import math
import random
import inspect

from PythonSim.classes import Component, PowerPort, SignalPort

def has_safe_constructor(cls):
    sig = inspect.signature(cls.__init__)
    for name, param in list(sig.parameters.items())[2:]:  # skip self, name
        if param.default is inspect.Parameter.empty:
            return False
    return True

def connect_all_ports(component, zero_input: bool = True):
    for port in component.get_ports():
        if isinstance(port, PowerPort):
            dummy = PowerPort(f"dummy_{port.name}")
            val = 0.0 if zero_input else random.uniform(0.1, 10.0)
            dummy.write_effort(val)
            dummy.write_flow(val)
            port.connect_port(dummy)
        elif isinstance(port, SignalPort):
            dummy = SignalPort(f"dummy_{port.name}")
            val = 0.0 if zero_input else random.uniform(0.1, 10.0)
            dummy.write_signal(val)
            port.connect_port(dummy)

def validate_component_class(cls):
    errors = []
    try:
        if not has_safe_constructor(cls):
            errors.append("Missing default parameters in constructor.")
        comp = cls("TestComponent")

        if len(comp.get_ports()) == 0:
            errors.append("No ports defined.")

        if len(comp.get_logged_variables()) == 0:
            errors.append("No logged variables.")

        for mode in ["zero", "random"]:
            connect_all_ports(comp, zero_input=(mode == "zero"))
            try:
                comp.step(0.01)
                comp.update_signal_ports()
                for name, fn in comp.get_logged_variables().items():
                    val = fn()
                    if not isinstance(val, (int, float)):
                        errors.append(f"{name} returned non-numeric: {val}")
                    elif math.isnan(val):
                        errors.append(f"{name} returned NaN")
            except Exception as e:
                errors.append(f"Step/update failed on {mode} input: {e}")
    except Exception as e:
        errors.append(f"Fatal error: {e}")

    return {"status": "pass" if not errors else "fail", "issues": errors}

def load_class_from_file(path):
    spec = importlib.util.spec_from_file_location("mod", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    for attr in dir(mod):
        obj = getattr(mod, attr)
        if isinstance(obj, type) and issubclass(obj, Component) and obj is not Component:
            return obj

    raise ValueError("No valid Component subclass found in file.")

if __name__ == "__main__":
    file_path = sys.argv[1]
    result = {"status": "fail", "issues": ["Unknown error."]}
    try:
        cls = load_class_from_file(file_path)
        result = validate_component_class(cls)
    except Exception as e:
        result = {"status": "fail", "issues": [str(e)]}
    print(json.dumps(result))
