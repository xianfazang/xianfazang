"""无界面冒烟：导入包、计算与 Mock 设备自检。"""

from __future__ import annotations


def run_smoke() -> int:
    from dynamometer_host.core.calc import efficiency, input_power, output_power
    from dynamometer_host.devices.bus import DeviceBus

    p_out = output_power(torque_nm=2.0, speed_rpm=1000.0)
    p_in = input_power(voltage_v=48.0, current_a=5.0)
    eta = efficiency(p_out, p_in)
    assert p_out > 0 and p_in > 0 and eta is not None and 0 < eta <= 100

    bus = DeviceBus.create_mock()
    bus.servo.initialize()
    bus.servo.load(target_speed_rpm=800.0, target_torque_nm=1.5)
    bus.brake.set_brake_percent(30.0)
    sample = bus.poll()
    assert sample.torque_nm >= 0
    bus.servo.unload()
    bus.brake.set_brake_percent(0.0)

    print("smoke OK: calc + MockServo/Torque/Brake")
    print(f"  P_out={p_out:.3f} W  P_in={p_in:.3f} W  eta={eta:.2f}%")
    print(
        f"  poll: T={sample.torque_nm:.3f} Nm  n={sample.speed_rpm:.1f} RPM  "
        f"brake={sample.brake_percent:.1f}%"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(run_smoke())
