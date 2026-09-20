"""功率 / 效率计算。"""

from __future__ import annotations

import math

# 低于此输入功率时效率视为无效
P_IN_MIN_W = 1e-3


def output_power(torque_nm: float, speed_rpm: float) -> float:
    """机械输出功率 (W)：P = T · 2πn / 60."""
    return torque_nm * (2.0 * math.pi * speed_rpm) / 60.0


def input_power(voltage_v: float, current_a: float) -> float:
    """电输入功率 (W)：P = V · I（直流或已处理有效值）。"""
    return voltage_v * current_a


def efficiency(p_out_w: float, p_in_w: float, p_min: float = P_IN_MIN_W) -> float | None:
    """效率 (%)；P_in 过小返回 None。"""
    if p_in_w <= p_min:
        return None
    return (p_out_w / p_in_w) * 100.0
