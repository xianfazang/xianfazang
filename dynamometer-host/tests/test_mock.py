"""Mock 设备与采样测试。"""

from dynamometer_host.core.sampling import SampleStore
from dynamometer_host.devices.base import ServoState
from dynamometer_host.devices.bus import DeviceBus


def test_mock_load_unload_cycle():
    bus = DeviceBus.create_mock()
    assert bus.servo.state == ServoState.DISCONNECTED
    assert bus.initialize_servo()
    assert bus.servo.state == ServoState.IDLE
    assert bus.load_servo(target_speed_rpm=1000, target_torque_nm=1.0)
    assert bus.servo.state == ServoState.LOADED
    for _ in range(20):
        bus.poll()
    sample = bus.poll()
    assert abs(sample.speed_rpm) > 10
    assert bus.unload_servo()
    assert bus.servo.state == ServoState.IDLE


def test_brake_independent_of_load():
    bus = DeviceBus.create_mock()
    bus.initialize_servo()
    bus.set_brake_percent(40.0)
    assert abs(bus.brake.get_brake_percent() - 40.0) < 1e-6
    assert abs(bus.ao.get_voltage(0) - 4.0) < 1e-6
    # 未加载时制动仍生效
    assert bus.servo.state == ServoState.IDLE
    s = bus.poll()
    assert s.brake_percent == 40.0


def test_sample_store_csv(tmp_path):
    store = SampleStore()
    store.add(
        torque_nm=1.0,
        speed_rpm=100.0,
        p_out_w=10.0,
        temperature_c=30.0,
        angle_deg=1.0,
        voltage_v=48.0,
        current_a=1.0,
        p_in_w=48.0,
        efficiency_pct=20.0,
        brake_percent=0.0,
    )
    path = store.export_csv(tmp_path / "s.csv")
    text = path.read_text(encoding="utf-8-sig")
    assert "torque_nm" in text
    assert len(store) == 1
