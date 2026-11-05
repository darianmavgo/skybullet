#!/usr/bin/env python3
"""Phase 1 range budget: how far does a glider released from a blade tip fly?

2D point-mass model: parabolic drag polar, exponential atmosphere, a load-factor limit,
and a climb-angle limiter (trim) so a fast release becomes a zoom climb that settles into
a best-glide instead of looping. Without the limiter the model tumbles in endless loops.
All numbers are game-physics estimates, not engineering data.

Usage: python3 sim/range_budget.py
"""
import math

G = 9.81
TARGET_M = 30 * 1609.344  # 30 miles


def rho(h):
    return 1.225 * math.exp(-max(h, 0.0) / 8500.0)


def fly(h0, v0, mass=50.0, area=2.5, aspect=20.0, cd0=0.012, e=0.9, n_max=3.0,
        release_pitch_deg=0.0, max_climb_deg=30.0, dt=0.02):
    """Return (range_m, flight_time_s, max_altitude_m, glide_ld) for a release at altitude h0."""
    k = 1.0 / (math.pi * e * aspect)
    cl_best = math.sqrt(cd0 / k)
    ld = cl_best / (cd0 + k * cl_best ** 2)
    x, h, t = 0.0, h0, 0.0
    v = v0
    gamma = math.radians(release_pitch_deg)  # flight path angle
    h_max = h0
    while h > 0 and t < 20000:
        q = 0.5 * rho(h) * v * v
        cl = min(cl_best, n_max * mass * G / max(q * area, 1e-6))
        if gamma > math.radians(max_climb_deg):  # trim/stabiliser: hold the climb angle, never loop
            cl = min(cl, mass * G * math.cos(gamma) / max(q * area, 1e-6))
        lift = q * area * cl
        drag = q * area * (cd0 + k * cl * cl)
        v_dot = (-drag - mass * G * math.sin(gamma)) / mass
        gamma_dot = (lift - mass * G * math.cos(gamma)) / (mass * max(v, 1.0))
        v = max(v + v_dot * dt, 1.0)
        gamma += gamma_dot * dt
        x += v * math.cos(gamma) * dt
        h += v * math.sin(gamma) * dt
        h_max = max(h_max, h)
        t += dt
    return x, t, h_max, ld


if __name__ == "__main__":
    mass, area, aspect = 50.0, 2.5, 20.0
    _, _, _, ld = fly(1000, 100, mass, area, aspect)
    print(f"Glider: {mass:.0f} kg, {area} m^2 wing, AR {aspect:.0f}, best L/D {ld:.1f}")
    print(f"Target: {TARGET_M/1000:.1f} km (30 mi)\n")
    print("Range in km (release pitch 0 deg, 3 g cap, 30 deg max climb); '*' = reaches target")
    speeds = (50, 100, 150, 200)
    print("alt\\tip speed  " + "".join(f"{v:>9} m/s" for v in speeds))
    for h in (500, 1000, 1500, 2000, 3000, 4000):
        row = ""
        for v in speeds:
            r = fly(h, v, mass, area, aspect)[0]
            row += f"{r/1000:>9.1f}{'*' if r >= TARGET_M else ' '}    "
        print(f"{h:>5} m      {row}")
    print("\nTip-speed g-load a = v^2/r for blade radius r:")
    for r in (50, 100, 200):
        print(f"  r={r:>3} m: " + "  ".join(f"{v} m/s -> {v*v/r/G:5.1f} g" for v in speeds))
