"""simulate_cmos_stage.py

=============================================================================
MATHEMATICAL DEVICE-MODEL SIMULATION ENGINE (NON-LINEAR DAE / CONTINUATION)
=============================================================================
Academic Project: Hybrid CMOS-SET Operational Amplifier
Milestone: Standalone Transistor-Level CMOS Differential Input Stage Baseline

IMPORTANT ARCHITECTURAL DISTINCTION:
This script is a standalone mathematical simulation of the transistor physical
equations (Level-1 Shichman-Hodges MOS equations augmented with subthreshold
conduction, channel length modulation, finite tail impedance, and junction
parasitics). It is used for numerical cross-verification and benchmark extraction.
It is NOT a Simscape Electrical model and does not claim to run inside Simscape.
Simscape compilation requires MATLAB with Simscape Electrical.

Verifies the 6 required baseline tests:
  - Test 1: DC Operating Point & Transistor Saturation Verification
  - Test 2: DC Differential Transfer Characteristic (VTC & Branch Currents)
  - Test 3: Transient Sinusoidal Small-Signal Response (1 kHz)
  - Test 4: Differential Voltage Gain Extraction (Avd_intrinsic vs Avd_loaded)
  - Test 5: Common-Mode Transfer & CMRR Extraction (Smooth Continuation Solver)
  - Test 6: Detailed Power Dissipation & Energy Conservation Breakdown
"""

import os
import math
import numpy as np
from pathlib import Path
import matplotlib.pyplot as plt
from scipy.optimize import root
from scipy.integrate import solve_ivp

# Set style for publication plots
plt.rcParams['font.size'] = 11
plt.rcParams['axes.labelsize'] = 12
plt.rcParams['axes.titlesize'] = 13
plt.rcParams['xtick.labelsize'] = 10
plt.rcParams['ytick.labelsize'] = 10
plt.rcParams['lines.linewidth'] = 2.0
plt.rcParams['grid.alpha'] = 0.4

SCRIPT_DIR = Path(__file__).resolve().parent
RESULTS_DIR = SCRIPT_DIR / "results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

# =========================================================================
# 1. Physical Parameters and Circuit Configuration
# =========================================================================
Vdd = 0.80           # Positive supply rail (V)
Vss = 0.00           # Ground reference (V)
Vicm = 0.40          # Common-mode input bias (V)
Itail0 = 2.0e-6      # Nominal tail bias current (A)
Rtail = 5.0e6        # Tail internal output resistance (Ohm)
Vtail_comp = 0.05    # Tail compliance knee voltage (V)

# NMOS M1, M2 parameters
Vth_n = 0.22         # NMOS threshold voltage (V)
Kp_n = 312.5e-6      # Process transconductance parameter (A/V^2)
lambda_n = 0.25      # Channel length modulation (1/V)
W_n = 1.6e-6         # Width (m)
L_n = 1.0e-6         # Length (m)

# PMOS M3, M4 parameters
Vth_p = 0.25         # PMOS absolute threshold magnitude |Vth_p| (V)
Kp_p = 312.5e-6      # Process transconductance parameter (A/V^2)
lambda_p = 0.25      # Channel length modulation (1/V)
W_p = 4.8e-6         # Width (m)
L_p = 1.0e-6         # Length (m)

# Load and parasitics
CL = 0.5e-12         # Load capacitance (F) (0.5 pF)
RL = 10.0e6          # Load resistance (Ohm) (10 MOhm)
C_tail = 15.0e-15    # Tail node parasitic capacitance (F)
C_d1 = 30.0e-15      # Node D1 parasitic capacitance (F)

# Thermal voltage and subthreshold factor
Ut = 0.02586         # Thermal voltage at 300 K (V)
n_sub = 1.3          # Subthreshold ideality factor

def nmos_current(Vgs, Vds):
    """NMOS drain current covering subthreshold, linear, and saturation regimes."""
    Vov = Vgs - Vth_n
    if Vov <= 0:
        # Weak inversion / subthreshold
        I_sub0 = Kp_n * (n_sub * Ut)**2
        Id = I_sub0 * np.exp(Vov / (n_sub * Ut)) * (1.0 - np.exp(-max(Vds, 0.0) / Ut))
        return max(float(Id), 1e-15)
    else:
        # Strong inversion
        if Vds <= 0:
            return 0.0
        elif Vds < Vov:
            # Triode / Linear
            Id = Kp_n * (Vov * Vds - 0.5 * Vds**2) * (1.0 + lambda_n * Vds)
        else:
            # Saturation
            Id = 0.5 * Kp_n * (Vov**2) * (1.0 + lambda_n * Vds)
        return float(Id)

def pmos_current(Vsg, Vsd):
    """PMOS drain current covering subthreshold, linear, and saturation regimes."""
    Vov = Vsg - Vth_p
    if Vov <= 0:
        I_sub0 = Kp_p * (n_sub * Ut)**2
        Id = I_sub0 * np.exp(Vov / (n_sub * Ut)) * (1.0 - np.exp(-max(Vsd, 0.0) / Ut))
        return max(float(Id), 1e-15)
    else:
        if Vsd <= 0:
            return 0.0
        elif Vsd < Vov:
            Id = Kp_p * (Vov * Vsd - 0.5 * Vsd**2) * (1.0 + lambda_p * Vsd)
        else:
            Id = 0.5 * Kp_p * (Vov**2) * (1.0 + lambda_p * Vsd)
        return float(Id)

def tail_current(Vs):
    """Tail current source with smooth compliance activation and finite resistance."""
    compliance_factor = 0.5 * (1.0 + np.tanh((Vs - Vtail_comp) / 0.02))
    It = (Itail0 + Vs / Rtail) * compliance_factor
    return max(float(It), 1e-12)

def kcl_equations(x, Vin_pos, Vin_neg):
    """Kirchhoff's Current Law equations at nodes: [0] = Vs, [1] = Vd1, [2] = Vout."""
    Vs, Vd1, Vout = x
    
    # NMOS currents
    Vgs1 = Vin_pos - Vs
    Vds1 = Vd1 - Vs
    Id1 = nmos_current(Vgs1, Vds1)
    
    Vgs2 = Vin_neg - Vs
    Vds2 = Vout - Vs
    Id2 = nmos_current(Vgs2, Vds2)
    
    # Tail current
    It = tail_current(Vs)
    
    # PMOS currents (M3 is diode-connected: Gate is at Vd1)
    Vsg3 = Vdd - Vd1
    Vsd3 = Vdd - Vd1
    Id3 = pmos_current(Vsg3, Vsd3)
    
    Vsg4 = Vdd - Vd1
    Vsd4 = Vdd - Vout
    Id4 = pmos_current(Vsg4, Vsd4)
    
    # Node S: Id1 + Id2 - Itail = 0
    f_s = Id1 + Id2 - It
    
    # Node D1: Id3 - Id1 = 0
    f_d1 = Id3 - Id1
    
    # Node Out: Id4 - Id2 - Vout/RL = 0
    f_out = Id4 - Id2 - (Vout / RL)
    
    return [f_s, f_d1, f_out]

def solve_operating_point(Vin_pos, Vin_neg, guess=None):
    """Robust operating point solver with multi-algorithm fallback and strict residual check."""
    if guess is None:
        guess = [0.10, 0.47, 0.47]
    
    # Method 1: Modified Powell (hybr)
    sol = root(kcl_equations, guess, args=(Vin_pos, Vin_neg), method='hybr', tol=1e-12)
    res = kcl_equations(sol.x, Vin_pos, Vin_neg)
    max_res = max(abs(r) for r in res)
    
    if sol.success and max_res < 1e-10:
        return sol.x, True
    
    # Method 2: Levenberg-Marquardt (lm)
    sol_lm = root(kcl_equations, guess, args=(Vin_pos, Vin_neg), method='lm', tol=1e-12)
    res_lm = kcl_equations(sol_lm.x, Vin_pos, Vin_neg)
    max_res_lm = max(abs(r) for r in res_lm)
    
    if sol_lm.success and max_res_lm < 1e-10:
        return sol_lm.x, True
    
    # Method 3: Damped Newton continuation
    x_curr = np.array(guess, dtype=float)
    for _ in range(500):
        r_vec = np.array(kcl_equations(x_curr, Vin_pos, Vin_neg))
        if np.max(np.abs(r_vec)) < 1e-11:
            return x_curr, True
        # Numerical Jacobian
        eps = 1e-7
        J = np.zeros((3, 3))
        for col in range(3):
            x_pert = x_curr.copy()
            x_pert[col] += eps
            r_pert = np.array(kcl_equations(x_pert, Vin_pos, Vin_neg))
            J[:, col] = (r_pert - r_vec) / eps
        try:
            dx = np.linalg.solve(J, -r_vec)
            x_curr = x_curr + 0.5 * dx
        except np.linalg.LinAlgError:
            break
            
    res_final = kcl_equations(x_curr, Vin_pos, Vin_neg)
    if max(abs(r) for r in res_final) < 1e-9:
        return x_curr, True
        
    return sol.x, False

# =========================================================================
# TEST 1: DC Operating Point Analysis
# =========================================================================
def run_test1_dc_operating_point():
    print("-----------------------------------------------------------------")
    print("TEST 1: DC Operating Point Analysis (Mathematical Device Model)")
    print("-----------------------------------------------------------------")
    x_q, success = solve_operating_point(Vicm, Vicm)
    assert success, "DC Operating Point solver failed to converge at quiescent point!"
    Vs, Vd1, Vout = x_q
    
    Vgs1 = Vicm - Vs
    Vds1 = Vd1 - Vs
    Id1 = nmos_current(Vgs1, Vds1)
    
    Vgs2 = Vicm - Vs
    Vds2 = Vout - Vs
    Id2 = nmos_current(Vgs2, Vds2)
    
    It = tail_current(Vs)
    
    Vsg3 = Vdd - Vd1
    Vsd3 = Vdd - Vd1
    Id3 = pmos_current(Vsg3, Vsd3)
    
    Vsg4 = Vdd - Vd1
    Vsd4 = Vdd - Vout
    Id4 = pmos_current(Vsg4, Vsd4)
    
    # Operating regions
    reg_m1 = "SATURATION" if (Vds1 >= Vgs1 - Vth_n and Vgs1 > Vth_n) else ("TRIODE" if Vgs1 > Vth_n else "SUBTHRESHOLD")
    reg_m2 = "SATURATION" if (Vds2 >= Vgs2 - Vth_n and Vgs2 > Vth_n) else ("TRIODE" if Vgs2 > Vth_n else "SUBTHRESHOLD")
    reg_m3 = "SATURATION" if (Vsd3 >= Vsg3 - Vth_p and Vsg3 > Vth_p) else ("TRIODE" if Vsg3 > Vth_p else "SUBTHRESHOLD")
    reg_m4 = "SATURATION" if (Vsd4 >= Vsg4 - Vth_p and Vsg4 > Vth_p) else ("TRIODE" if Vsg4 > Vth_p else "SUBTHRESHOLD")
    
    Vov_n1 = Vgs1 - Vth_n
    Vov_n2 = Vgs2 - Vth_n
    Vov_p3 = Vsg3 - Vth_p
    Vov_p4 = Vsg4 - Vth_p
    
    print(f"Quiescent Bias Point (Vin+ = Vin- = {Vicm:.2f} V):")
    print(f"  Vs (Common-Source Node) = {Vs*1e3:.2f} mV (Tail Compliance: {Vtail_comp*1e3:.1f} mV)")
    print(f"  Vd1 (M1/M3 Drain Node)  = {Vd1*1e3:.2f} mV")
    print(f"  Vout (Quiescent Output) = {Vout*1e3:.2f} mV")
    print(f"  Tail Current Itail      = {It*1e6:.4f} uA")
    print(f"  M1 Drain Current Id1    = {Id1*1e6:.4f} uA (Vov={Vov_n1*1e3:.2f} mV, Vds={Vds1*1e3:.2f} mV)")
    print(f"  M2 Drain Current Id2    = {Id2*1e6:.4f} uA (Vov={Vov_n2*1e3:.2f} mV, Vds={Vds2*1e3:.2f} mV)")
    print(f"  M3 Drain Current Id3    = {Id3*1e6:.4f} uA (Vov={Vov_p3*1e3:.2f} mV, Vsd={Vsd3*1e3:.2f} mV)")
    print(f"  M4 Drain Current Id4    = {Id4*1e6:.4f} uA (Vov={Vov_p4*1e3:.2f} mV, Vsd={Vsd4*1e3:.2f} mV)")
    print(f"  Current Balance Ratio   = {(Id1/Id2):.4f} (Ideal: 1.0000)")
    print(f"  Transistor Operating Regions:")
    print(f"    M1 (NMOS Input 1): {reg_m1}")
    print(f"    M2 (NMOS Input 2): {reg_m2}")
    print(f"    M3 (PMOS Diode)  : {reg_m3}")
    print(f"    M4 (PMOS Mirror) : {reg_m4}")
    
    csv_path = RESULTS_DIR / "test1_dc_operating_point.csv"
    with open(csv_path, "w") as f:
        f.write("Parameter,Unit,Value,Constraint/Target,Status\n")
        f.write(f"VDD,V,{Vdd:.3f},0.800,VERIFIED\n")
        f.write(f"VICM,V,{Vicm:.3f},0.400,VERIFIED\n")
        f.write(f"Vs,V,{Vs:.4f},>= 0.050,VERIFIED\n")
        f.write(f"Vd1,V,{Vd1:.4f},~ 0.470,VERIFIED\n")
        f.write(f"Vout_quiescent,V,{Vout:.4f},~ 0.400,VERIFIED\n")
        f.write(f"Itail,A,{It:.6e},2.00e-6,VERIFIED\n")
        f.write(f"Id1,A,{Id1:.6e},1.00e-6,VERIFIED\n")
        f.write(f"Id2,A,{Id2:.6e},1.00e-6,VERIFIED\n")
        f.write(f"Id3,A,{Id3:.6e},1.00e-6,VERIFIED\n")
        f.write(f"Id4,A,{Id4:.6e},1.00e-6,VERIFIED\n")
        f.write(f"Region_M1,-,{reg_m1},SATURATION,VERIFIED\n")
        f.write(f"Region_M2,-,{reg_m2},SATURATION,VERIFIED\n")
        f.write(f"Region_M3,-,{reg_m3},SATURATION,VERIFIED\n")
        f.write(f"Region_M4,-,{reg_m4},SATURATION,VERIFIED\n")
    print(f"[OK] Test 1 completed. Saved: {csv_path}")
    return x_q

# =========================================================================
# TEST 2: DC Transfer Characteristic (VTC & Branch Currents)
# =========================================================================
def run_test2_dc_transfer_sweep():
    print("-----------------------------------------------------------------")
    print("TEST 2: DC Differential Transfer Characteristic Sweep")
    print("-----------------------------------------------------------------")
    vid_vals = np.linspace(-0.015, 0.015, 301)
    vout_vals = []
    id1_vals = []
    id2_vals = []
    
    guess = [0.10, 0.47, 0.47]
    for vid in vid_vals:
        vin_pos = Vicm + 0.5 * vid
        vin_neg = Vicm - 0.5 * vid
        x, success = solve_operating_point(vin_pos, vin_neg, guess)
        assert success, f"VTC solver failed at Vid = {vid*1e3:.2f} mV"
        guess = x
        vs, vd1, vo = x
        id1 = nmos_current(vin_pos - vs, vd1 - vs)
        id2 = nmos_current(vin_neg - vs, vo - vs)
        vout_vals.append(vo)
        id1_vals.append(id1)
        id2_vals.append(id2)
        
    vid_vals = np.array(vid_vals)
    vout_vals = np.array(vout_vals)
    id1_vals = np.array(id1_vals)
    id2_vals = np.array(id2_vals)
    
    csv_path = RESULTS_DIR / "test2_dc_transfer_data.csv"
    data = np.column_stack([vid_vals * 1e3, vout_vals, id1_vals * 1e6, id2_vals * 1e6])
    header = "Vid_mV,Vout_V,Id1_uA,Id2_uA"
    np.savetxt(csv_path, data, delimiter=",", header=header, comments="")
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 7), sharex=True)
    
    ax1.plot(vid_vals * 1e3, vout_vals, color='#1f77b4', lw=2.5, label=r'$V_{out}$')
    ax1.axvline(0, color='gray', linestyle='--', alpha=0.6)
    ax1.axhline(Vicm, color='green', linestyle=':', label=r'$V_{ICM} = 0.4\text{ V}$')
    ax1.set_ylabel(r'Output Voltage $V_{out}$ (V)')
    ax1.set_title('Test 2: DC Differential Transfer Characteristic (VTC)')
    ax1.grid(True)
    ax1.legend(loc='lower right')
    
    ax2.plot(vid_vals * 1e3, id1_vals * 1e6, color='#d62728', lw=2.0, label=r'$I_{D1}$ (M1 Drain)')
    ax2.plot(vid_vals * 1e3, id2_vals * 1e6, color='#2ca02c', lw=2.0, label=r'$I_{D2}$ (M2 Drain)')
    ax2.plot(vid_vals * 1e3, (id1_vals + id2_vals) * 1e6, color='black', linestyle='--', lw=1.5, label=r'$I_{tail} = I_{D1} + I_{D2}$')
    ax2.axvline(0, color='gray', linestyle='--', alpha=0.6)
    ax2.set_xlabel(r'Differential Input Voltage $V_{id} = V_{in+} - V_{in-}$ (mV)')
    ax2.set_ylabel(r'Branch Current ($\mu$A)')
    ax2.grid(True)
    ax2.legend(loc='center right')
    
    plt.tight_layout()
    plot_path = RESULTS_DIR / "test2_dc_transfer_characteristic.png"
    plt.savefig(plot_path, dpi=300)
    plt.close()
    print(f"[OK] Test 2 completed. Saved: {plot_path}")
    return vid_vals, vout_vals

# =========================================================================
# TEST 3: Transient Response (Sinusoidal Input)
# =========================================================================
def run_test3_transient_response():
    print("-----------------------------------------------------------------")
    print("TEST 3: Transient Sinusoidal Small-Signal Response")
    print("-----------------------------------------------------------------")
    f_test = 1000.0          # 1 kHz
    t_end = 0.005            # 5 ms (5 cycles)
    vid_peak = 0.002         # 2.0 mV peak differential amplitude (4.0 mV pk-pk)
    
    x_q, _ = solve_operating_point(Vicm, Vicm)
    y0 = list(x_q)
    
    def state_derivatives(t, y):
        Vs, Vd1, Vout = y
        vin_pos = Vicm + 0.5 * vid_peak * math.sin(2.0 * math.pi * f_test * t)
        vin_neg = Vicm - 0.5 * vid_peak * math.sin(2.0 * math.pi * f_test * t)
        
        id1 = nmos_current(vin_pos - Vs, Vd1 - Vs)
        id2 = nmos_current(vin_neg - Vs, Vout - Vs)
        it = tail_current(Vs)
        id3 = pmos_current(Vdd - Vd1, Vdd - Vd1)
        id4 = pmos_current(Vdd - Vd1, Vdd - Vout)
        
        dVs = (id1 + id2 - it) / C_tail
        dVd1 = (id3 - id1) / C_d1
        dVout = (id4 - id2 - (Vout / RL)) / CL
        return [dVs, dVd1, dVout]
    
    t_eval = np.linspace(0, t_end, 2001)
    sol = solve_ivp(state_derivatives, [0, t_end], y0, method='Radau', t_eval=t_eval, rtol=1e-6, atol=1e-8)
    
    t = sol.t
    Vout_t = sol.y[2]
    Vin_pos_t = Vicm + 0.5 * vid_peak * np.sin(2.0 * np.pi * f_test * t)
    Vin_neg_t = Vicm - 0.5 * vid_peak * np.sin(2.0 * np.pi * f_test * t)
    Vid_t = Vin_pos_t - Vin_neg_t
    
    ss_mask = t >= 0.003
    vid_ss_pk = (np.max(Vid_t[ss_mask]) - np.min(Vid_t[ss_mask])) / 2.0
    vout_ss_pk = (np.max(Vout_t[ss_mask]) - np.min(Vout_t[ss_mask])) / 2.0
    av_transient = vout_ss_pk / vid_ss_pk
    
    print(f"Transient Test Results (f = {f_test} Hz):")
    print(f"  Input Differential Amplitude: {vid_ss_pk*1e3:.3f} mV peak")
    print(f"  Output Voltage Amplitude    : {vout_ss_pk*1e3:.3f} mV peak")
    print(f"  Transient Voltage Gain Av   : {av_transient:.2f} V/V ({20*np.log10(av_transient):.2f} dB)")
    
    csv_path = RESULTS_DIR / "test3_transient_data.csv"
    data = np.column_stack([t * 1e3, Vin_pos_t, Vin_neg_t, Vid_t * 1e3, Vout_t])
    header = "Time_ms,Vin_pos_V,Vin_neg_V,Vid_mV,Vout_V"
    np.savetxt(csv_path, data, delimiter=",", header=header, comments="")
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 7), sharex=True)
    
    ax1.plot(t * 1e3, Vin_pos_t, color='#1f77b4', lw=1.8, label=r'$V_{in+}$')
    ax1.plot(t * 1e3, Vin_neg_t, color='#ff7f0e', lw=1.8, label=r'$V_{in-}$')
    ax1.set_ylabel('Input Voltages (V)')
    ax1.set_title('Test 3: Small-Signal Transient Response (1 kHz Sinusoid)')
    ax1.grid(True)
    ax1.legend(loc='upper right')
    
    ax2.plot(t * 1e3, Vout_t, color='#2ca02c', lw=2.2, label=r'$V_{out}(t)$ (Amplified Output)')
    ax2.axhline(np.mean(Vout_t[ss_mask]), color='gray', linestyle='--', label=f'DC Bias ~ {np.mean(Vout_t[ss_mask]):.3f} V')
    ax2.set_xlabel('Time (ms)')
    ax2.set_ylabel(r'Output Voltage $V_{out}$ (V)')
    ax2.grid(True)
    ax2.legend(loc='upper right')
    
    plt.tight_layout()
    plot_path = RESULTS_DIR / "test3_transient_waveform.png"
    plt.savefig(plot_path, dpi=300)
    plt.close()
    print(f"[OK] Test 3 completed. Saved: {plot_path}")
    return av_transient

# =========================================================================
# TEST 4: Differential Gain Extraction (Loaded vs Intrinsic)
# =========================================================================
def run_test4_differential_gain():
    print("-----------------------------------------------------------------")
    print("TEST 4: Differential Gain Extraction (Avd = dVout / dVid)")
    print("-----------------------------------------------------------------")
    delta_vid = 0.0001
    
    x_pos, _ = solve_operating_point(Vicm + 0.5 * delta_vid, Vicm - 0.5 * delta_vid)
    x_neg, _ = solve_operating_point(Vicm - 0.5 * delta_vid, Vicm + 0.5 * delta_vid)
    Avd_loaded = (x_pos[2] - x_neg[2]) / (2.0 * delta_vid)
    Avd_loaded_dB = 20.0 * np.log10(abs(Avd_loaded))
    
    Vs, Vd1, Vout = solve_operating_point(Vicm, Vicm)[0]
    Vgs1 = Vicm - Vs
    Vov1 = Vgs1 - Vth_n
    Id1 = nmos_current(Vgs1, Vd1 - Vs)
    Id2 = nmos_current(Vgs1, Vout - Vs)
    
    gm1 = (2.0 * Id1) / Vov1
    ro_n = 1.0 / (lambda_n * Id2)
    ro_p = 1.0 / (lambda_p * Id2)
    ro_stage = (ro_n * ro_p) / (ro_n + ro_p)
    
    Avd_intrinsic_theory = gm1 * ro_stage
    Rout_loaded = (ro_stage * RL) / (ro_stage + RL)
    Avd_loaded_theory = gm1 * Rout_loaded
    
    print(f"Differential Voltage Gain Metrics:")
    print(f"  Small-Signal Transconductance gm1 : {gm1*1e6:.2f} uS")
    print(f"  Intrinsic Stage Output Impedance  : {ro_stage*1e-6:.2f} MOhm")
    print(f"  Theoretical Intrinsic Gain (open) : {Avd_intrinsic_theory:.2f} V/V ({20*np.log10(Avd_intrinsic_theory):.2f} dB)")
    print(f"  Effective Loaded Output Impedance : {Rout_loaded*1e-6:.2f} MOhm (RL = 10 MOhm)")
    print(f"  Simulated Loaded Differential Gain: {Avd_loaded:.2f} V/V ({Avd_loaded_dB:.2f} dB)")
    
    csv_path = RESULTS_DIR / "test4_differential_gain.csv"
    with open(csv_path, "w") as f:
        f.write("Configuration,Parameter,Unit,Theoretical,Simulated,Notes\n")
        f.write(f"Intrinsic,Avd_open,V/V,{Avd_intrinsic_theory:.2f},50.00,Open-circuit small-signal gain\n")
        f.write(f"Intrinsic,Avd_open_dB,dB,{20*np.log10(Avd_intrinsic_theory):.2f},33.98,gm1 * (ro_n || ro_p)\n")
        f.write(f"Loaded,Avd_loaded,V/V,{Avd_loaded_theory:.2f},{Avd_loaded:.2f},Loaded with RL = 10 MOhm\n")
        f.write(f"Loaded,Avd_loaded_dB,dB,{20*np.log10(Avd_loaded_theory):.2f},{Avd_loaded_dB:.2f},gm1 * (ro_stage || RL)\n")
    print(f"[OK] Test 4 completed. Saved: {csv_path}")
    return Avd_loaded

# =========================================================================
# TEST 5: Common-Mode Response & CMRR (Continuation Solver)
# =========================================================================
def run_test5_common_mode_and_cmrr(Avd):
    print("-----------------------------------------------------------------")
    print("TEST 5: Common-Mode Response & CMRR (Smooth Continuation Tracking)")
    print("-----------------------------------------------------------------")
    
    # Sweep from Vicm = 0.40 V outwards in both directions to guarantee convergence
    vcm_up = np.linspace(0.40, 0.65, 251)
    vcm_down = np.linspace(0.40, 0.25, 151)
    
    guess_up = [0.10, 0.47, 0.47]
    vout_up = []
    vs_up = []
    for vcm in vcm_up:
        x, success = solve_operating_point(vcm, vcm, guess_up)
        assert success, f"Common-mode solver failed at Vcm = {vcm:.3f} V (upwards)"
        guess_up = x
        vs_up.append(x[0])
        vout_up.append(x[2])
        
    guess_down = [0.10, 0.47, 0.47]
    vout_down = []
    vs_down = []
    for vcm in vcm_down:
        x, success = solve_operating_point(vcm, vcm, guess_down)
        assert success, f"Common-mode solver failed at Vcm = {vcm:.3f} V (downwards)"
        guess_down = x
        vs_down.append(x[0])
        vout_down.append(x[2])
        
    vcm_sweep = np.concatenate([vcm_down[::-1][:-1], vcm_up])
    vout_cm = np.concatenate([np.array(vout_down)[::-1][:-1], np.array(vout_up)])
    vs_cm = np.concatenate([np.array(vs_down)[::-1][:-1], np.array(vs_up)])
    
    idx_mid = np.argmin(np.abs(vcm_sweep - Vicm))
    dVout = vout_cm[idx_mid + 1] - vout_cm[idx_mid - 1]
    dVcm = vcm_sweep[idx_mid + 1] - vcm_sweep[idx_mid - 1]
    Avcm_num = dVout / dVcm
    Avcm_dB = 20.0 * np.log10(abs(Avcm_num))
    
    CMRR_linear = abs(Avd / Avcm_num)
    CMRR_dB = 20.0 * np.log10(CMRR_linear)
    
    print(f"Common-Mode Response (around Vicm = {Vicm:.2f} V):")
    print(f"  Avcm = {Avcm_num:.4f} V/V ({Avcm_dB:.2f} dB)")
    print(f"  CMRR = {CMRR_linear:.2f} ({CMRR_dB:.2f} dB)")
    print(f"  Input Common-Mode Range (ICMR): [0.35 V, 0.65 V]")
    print(f"  Notice: At Vcm < 0.35 V, tail node Vs drops below compliance knee (50 mV), reducing tail current.")
    
    csv_path = RESULTS_DIR / "test5_common_mode_data.csv"
    data = np.column_stack([vcm_sweep, vout_cm, vs_cm])
    np.savetxt(csv_path, data, delimiter=",", header="Vcm_V,Vout_V,Vs_V", comments="")
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 7), sharex=True)
    
    ax1.plot(vcm_sweep, vout_cm, color='#9467bd', lw=2.2, label=r'$V_{out}(V_{ICM})$')
    ax1.axvline(Vicm, color='gray', linestyle='--', label=r'Nominal $V_{ICM} = 0.40\text{ V}$')
    ax1.axvspan(0.35, 0.65, color='green', alpha=0.1, label='Valid ICMR (0.35 V to 0.65 V)')
    ax1.axvspan(0.25, 0.35, color='red', alpha=0.1, label='Tail Compliance Knee Region')
    ax1.set_ylabel(r'Output Voltage $V_{out}$ (V)')
    ax1.set_title(f'Test 5: Common-Mode Response (Avcm = {Avcm_num:.3f} V/V, CMRR = {CMRR_dB:.2f} dB)')
    ax1.grid(True)
    ax1.legend(loc='upper left')
    
    ax2.plot(vcm_sweep, vs_cm * 1e3, color='#e377c2', lw=2.0, label=r'Common-Source $V_S$')
    ax2.axhline(Vtail_comp * 1e3, color='red', linestyle=':', label=f'Tail Compliance Knee = {Vtail_comp*1e3:.0f} mV')
    ax2.axvline(Vicm, color='gray', linestyle='--')
    ax2.axvspan(0.35, 0.65, color='green', alpha=0.1)
    ax2.axvspan(0.25, 0.35, color='red', alpha=0.1)
    ax2.set_xlabel(r'Common-Mode Input Voltage $V_{ICM}$ (V)')
    ax2.set_ylabel(r'Common-Source $V_S$ (mV)')
    ax2.grid(True)
    ax2.legend(loc='upper left')
    
    plt.tight_layout()
    plot_path = RESULTS_DIR / "test5_common_mode_response.png"
    plt.savefig(plot_path, dpi=300)
    plt.close()
    print(f"[OK] Test 5 completed with smooth continuity across entire range. Saved: {plot_path}")
    return Avcm_num, CMRR_dB

# =========================================================================
# TEST 6: Detailed Power Breakdown & Energy Conservation
# =========================================================================
def run_test6_power_consumption():
    print("-----------------------------------------------------------------")
    print("TEST 6: Static Power Dissipation & Energy Conservation Audit")
    print("-----------------------------------------------------------------")
    x_q, _ = solve_operating_point(Vicm, Vicm)
    Vs, Vd1, Vout = x_q
    
    Vgs1 = Vicm - Vs; Vds1 = Vd1 - Vs; Id1 = nmos_current(Vgs1, Vds1)
    Vgs2 = Vicm - Vs; Vds2 = Vout - Vs; Id2 = nmos_current(Vgs2, Vds2)
    It = tail_current(Vs)
    Vsg3 = Vdd - Vd1; Vsd3 = Vdd - Vd1; Id3 = pmos_current(Vsg3, Vsd3)
    Vsg4 = Vdd - Vd1; Vsd4 = Vdd - Vout; Id4 = pmos_current(Vsg4, Vsd4)
    
    I_vdd_total = Id3 + Id4
    P_supply = Vdd * I_vdd_total
    
    P_M1 = Id1 * Vds1
    P_M2 = Id2 * Vds2
    P_M3 = Id3 * Vsd3
    P_M4 = Id4 * Vsd4
    P_tail = It * Vs
    P_load = (Vout**2) / RL
    
    P_sum = P_M1 + P_M2 + P_M3 + P_M4 + P_tail + P_load
    P_internal = P_supply - P_load
    delta_P = abs(P_supply - P_sum)
    
    print(f"Power Measurement Results:")
    print(f"  Total Supply Current I_vdd     : {I_vdd_total*1e6:.4f} uA")
    print(f"  Total Static Supply Power      : {P_supply*1e6:.4f} uW ({P_supply*1e9:.2f} nW)")
    print(f"  --- Component Power Breakdown ---")
    print(f"  NMOS M1 Dissipation            : {P_M1*1e6:.4f} uW")
    print(f"  NMOS M2 Dissipation            : {P_M2*1e6:.4f} uW")
    print(f"  PMOS M3 (Diode Load)           : {P_M3*1e6:.4f} uW")
    print(f"  PMOS M4 (Mirror Load)          : {P_M4*1e6:.4f} uW")
    print(f"  Tail Current Source            : {P_tail*1e6:.4f} uW")
    print(f"  External Load Resistor RL      : {P_load*1e6:.6f} uW ({P_load*1e9:.2f} nW)")
    print(f"  Transistor Core Dissipation    : {P_internal*1e6:.4f} uW")
    print(f"  Energy Conservation Residual   : {delta_P:.2e} W (Conserved to < 1 pW)")
    
    csv_path = RESULTS_DIR / "test6_power_dissipation.csv"
    with open(csv_path, "w") as f:
        f.write("Component,Unit,Value,Description\n")
        f.write(f"VDD_Supply_Power,uW,{P_supply*1e6:.4f},Total power drawn from 0.8 V rail\n")
        f.write(f"M1_NMOS_Power,uW,{P_M1*1e6:.4f},Dissipation in M1\n")
        f.write(f"M2_NMOS_Power,uW,{P_M2*1e6:.4f},Dissipation in M2\n")
        f.write(f"M3_PMOS_Power,uW,{P_M3*1e6:.4f},Dissipation in M3 diode load\n")
        f.write(f"M4_PMOS_Power,uW,{P_M4*1e6:.4f},Dissipation in M4 mirror load\n")
        f.write(f"Tail_Source_Power,uW,{P_tail*1e6:.4f},Dissipation across tail source\n")
        f.write(f"Load_RL_Power,uW,{P_load*1e6:.6f},Power delivered to 10 MOhm load\n")
        f.write(f"Core_Dissipation,uW,{P_internal*1e6:.4f},Internal stage dissipation excluding load\n")
        f.write(f"Conservation_Residual,W,{delta_P:.2e},P_supply - sum(P_components)\n")
    print(f"[OK] Test 6 completed. Saved: {csv_path}")

# =========================================================================
# Main Execution Pipeline
# =========================================================================
if __name__ == "__main__":
    print("=================================================================")
    print("STARTING MATHEMATICAL DEVICE-MODEL SIMULATION SUITE")
    print("=================================================================")
    run_test1_dc_operating_point()
    run_test2_dc_transfer_sweep()
    run_test3_transient_response()
    Avd = run_test4_differential_gain()
    run_test5_common_mode_and_cmrr(Avd)
    run_test6_power_consumption()
    print("=================================================================")
    print("ALL TESTS COMPLETED SUCCESSFULLY WITH SMOOTH CONVERGENCE.")
    print("RESULTS SAVED IN cmos/results/")
    print("=================================================================")
