import math


def wheel_speeds(v, w, radius=0.0762, track=0.38):
    return ((v - w * track / 2.0) / radius, (v + w * track / 2.0) / radius)


def test_straight_motion():
    left, right = wheel_speeds(0.2, 0.0)
    assert math.isclose(left, right, rel_tol=1e-9)


def test_in_place_turn():
    left, right = wheel_speeds(0.0, 0.8)
    assert left < 0 < right


def test_reverse():
    left, right = wheel_speeds(-0.2, 0.0)
    assert left < 0 and right < 0
