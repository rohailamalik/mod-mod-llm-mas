from results_pipeline import run_tasks_and_save, convert_results_to_html

task_list = [
    "We need to create an empirical speed-torque curve based model of a DC motor.",
    "We need to create an empirical speed-torque curve based model of a DC motor. The required torque demand asks the motor to provide a required amount of torque.",
    "We need to create a steady-state ODE-based model of a DC motor that neglects electrical inductance.",
    "We need to create a steady-state ODE-based model of a DC motor that neglects electrical inductance. The required torque demand asks the motor to provide a required amount of torque.",
    "We need to create a dynamic ODE-based model of a DC motor that includes both electrical inductance and mechanical dynamics.",
    "We need to create a dynamic ODE-based model of a DC motor that includes both electrical inductance and mechanical dynamics. The required torque demand asks the motor to provide a required amount of torque.",
    "We need to create an empirical speed-torque curve based model of a permanent magnet synchronous (PMS) motor.",
    "We need to create a dynamic ODE-based model of a DC motor that excludes electrical inductance but includes mechanical dynamics. The required torque demand asks the motor to provide a required amount of torque.",
    "We need to create a Thevenin equivalent model of a battery that assumes a constant voltage and internal resistance.",
    "We need to create a Thevenin equivalent model of a battery where the open-circuit voltage depends on the state of charge (SOC), and the model does not include capacitance effects.",
    "We need to create a Thevenin equivalent model of a battery where the open-circuit voltage depends on the state of charge (SOC), and the model includes both resistance and capacitance effects.",
    "We need to create a single-speed gearbox model that transmits rotational power from an input shaft to an output shaft with a fixed gear ratio.",
    "We need to create a vehicle longitudinal dynamics model that represents the translational motion of the vehicle based on applied traction and resistive forces."
]

run_tasks_and_save(task_list)
convert_results_to_html()