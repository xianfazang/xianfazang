"""计算单元测试。"""

from dynamometer_host.core.calc import efficiency, input_power, output_power


def test_output_power_known_value():
    # T=1 Nm, n=60 RPM → P = 1 * 2π * 60 / 60 = 2π W
    import math

    assert abs(output_power(1.0, 60.0) - 2 * math.pi) < 1e-9


def test_input_power():
    assert input_power(48.0, 2.5) == 120.0


def test_efficiency_valid():
    eta = efficiency(90.0, 100.0)
    assert eta is not None
    assert abs(eta - 90.0) < 1e-9


def test_efficiency_invalid_when_pin_small():
    assert efficiency(1.0, 0.0) is None
    assert efficiency(1.0, 1e-6) is None
