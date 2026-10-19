# Hybrid CMOS–SET Op-Amp Verification and Test Plan

**Document ID:** TP-ENG-001  
**Revision:** 1.0  
**Date:** October 19, 2026  
**Status:** Approved for Implementation & Validation  

---

## 1. Overview and Test Objectives

This document establishes the comprehensive test protocol for validating the three MATLAB/Simulink models and underlying physics/circuit equations of the Hybrid CMOS–SET Operational Amplifier:

1. **Model 1:** Standalone SET-CMOS Integral Section (`Hybrid_OpAmp_Integral.slx`)
2. **Model 2:** Standalone CMOS Differential Input Stage (`Hybrid_OpAmp_Differential.slx`)
3. **Model 3:** Complete Cascaded Hybrid CMOS–SET Op-Amp (`Hybrid_OpAmp_Full.slx`)

---

## 2. Test Architecture & Environment Matrix

| Execution Environment | Tooling / Engine | Test Type | Coverage |
| :--- | :--- | :--- | :--- |
| **MATLAB / Simulink** | `check_environment.m`, `validate_models.m`, `run_all_simulations.m` | Block compilation, update checks, solver configuration, Simulink integration | Primary automation suite for end-users running MATLAB. |
| **Python Numerical Engine** | `run_python_simulation_suite.py` (NumPy, SciPy, Matplotlib) | Stiff ODE integration, MIB/Uchida tunneling evaluation, AC Bode sweep, VTC extraction | Independent cross-verification and offline execution. |

---

## 3. Test Cases: Standalone Integral Section (`Hybrid_OpAmp_Integral.slx`)

### Test INT-01: Transient Step Integration Response
- **Objective:** Verify that the hybrid SET-CMOS stage behaves as an active Miller integrator in response to a step input.
- **Input Conditions:** Quiescent DC bias $V_{ICM} = 0.40\text{ V}$. Input step $\Delta V_{in} = 2.0\text{ mV}$ applied at $t = 0.5\ \mu\text{s}$.
- **Governing Equation:**
  $$\frac{dV_{out}}{dt} = - \frac{g_{m2} \Delta V_{in}}{C_c} = - \frac{(40 \times 10^{-6}\text{ S}) \times (2 \times 10^{-3}\text{ V})}{0.5 \times 10^{-12}\text{ F}} = -0.16\text{ V}/\mu\text{s}$$
- **Expected Result:**
  - Prior to $0.5\ \mu\text{s}$, $V_{out} = 0.40\text{ V}$.
  - After $0.5\ \mu\text{s}$, $V_{out}$ ramps downward with a linear slope of $-0.16\text{ V}/\mu\text{s} \pm 5\%$.
  - Reaches lower saturation limit $0.05\text{ V}$ at approximately $t = 2.69\ \mu\text{s}$ and clamps stably without numerical instability.
- **Acceptance Criteria:** Slope within $[-0.15\text{ V}/\mu\text{s}, -0.17\text{ V}/\mu\text{s}]$, clean rail clamping at $0.05\text{ V}$.

### Test INT-02: Sinusoidal Frequency Integration
- **Objective:** Demonstrate continuous time-domain integration and verify $90^\circ$ phase lag across the dominant integrating bandwidth.
- **Input Conditions:** $V_{in}(t) = 1.0\text{ mV} \cdot \sin(2\pi \cdot 100\text{ kHz} \cdot t)$ superimposed on $0.40\text{ V}$ bias.
- **Expected Result:**
  $$V_{out}(t) = 0.40\text{ V} + \frac{g_{m2} V_{in,pk}}{2\pi f C_c} \cos(2\pi \cdot 100\text{ kHz} \cdot t)$$
  - Output amplitude: $A_{out} = \frac{40 \times 10^{-6} \times 1 \times 10^{-3}}{2\pi \times 10^5 \times 0.5 \times 10^{-12}} = 0.127\text{ V}$ peak-to-peak swing around $0.40\text{ V}$.
  - Phase relationship: exact $-90^\circ$ phase lag (cosine waveform from sine input).
- **Acceptance Criteria:** Phase lag $90^\circ \pm 5^\circ$, amplitude $0.127\text{ V} \pm 10\%$.

---

## 4. Test Cases: Standalone Differential Stage (`Hybrid_OpAmp_Differential.slx`)

### Test DIFF-01: DC Differential Voltage Transfer Characteristic (VTC)
- **Objective:** Measure the differential voltage gain $A_{vd1}$, input linear range, and saturation limits.
- **Input Conditions:** Common-mode bias $V_{ICM} = 0.40\text{ V}$. Differential voltage $V_{id} = V_{in+} - V_{in-}$ swept over $[-15\text{ mV}, +15\text{ mV}]$.
- **Expected Result:**
  - Small-signal differential gain $A_{vd1} = g_{m1} \cdot r_{o1} = 25\ \mu\text{S} \times 2.0\text{ M}\Omega = 50.0\text{ V/V}$ ($34.0\text{ dB}$).
  - Linear output swing: from $0.05\text{ V}$ to $0.75\text{ V}$ ($\Delta V = 0.70\text{ V}$).
  - Linear input range: $\pm \frac{0.35\text{ V}}{50\text{ V/V}} = \pm 7.0\text{ mV}$.
  - Output clamps cleanly at $0.05\text{ V}$ for $V_{id} \le -7.0\text{ mV}$ and at $0.75\text{ V}$ for $V_{id} \ge +7.0\text{ mV}$.
- **Acceptance Criteria:** Measured gain $A_{vd1} \ge 30\text{ dB}$ ($> 31.6\text{ V/V}$), symmetrical around $V_{id} = 0$.

### Test DIFF-02: Common-Mode Response & CMRR Extraction
- **Objective:** Evaluate common-mode gain $A_{vcm1}$ and Common-Mode Rejection Ratio (CMRR).
- **Input Conditions:** $V_{id} = 0\text{ V}$. Common-mode input $V_{ICM}$ swept over $[0.20\text{ V}, 0.60\text{ V}]$ ($400\text{ mV}$ range).
- **Expected Result:**
  - Common-mode gain: $A_{vcm1} \approx - \frac{r_{o1}}{2 R_{tail}} = - \frac{2\text{ M}\Omega}{10\text{ M}\Omega} = -0.20\text{ V/V}$ ($-14.0\text{ dB}$).
  - Common-Mode Rejection Ratio:
    $$\text{CMRR} = 20 \log_{10}\left|\frac{A_{vd1}}{A_{vcm1}}\right| = 20 \log_{10}(250) = 47.96\text{ dB}$$
- **Acceptance Criteria:** $\text{CMRR} \ge 45.0\text{ dB}$, $|A_{vcm1}| \le 0.25\text{ V/V}$.

---

## 5. Test Cases: Complete Hybrid Op-Amp (`Hybrid_OpAmp_Full.slx`)

### Test FULL-01: AC Small-Signal Frequency Response (Bode Analysis)
- **Objective:** Determine the DC open-loop gain $A_0$, dominant pole frequency $f_{p1}$, unity-gain bandwidth ($\text{GBW}$), second pole $f_{p2}$, and Phase Margin ($\text{PM}$).
- **Input Conditions:** AC small-signal excitation swept logarithmically from $10\text{ Hz}$ to $100\text{ MHz}$.
- **Target Specifications:**
  - DC Open-Loop Gain: $A_0 \ge 60.0\text{ dB}$. (Nominal derived: $71.7\text{ dB}$).
  - Gain-Bandwidth Product: $\text{GBW} \ge 5.0\text{ MHz}$. (Nominal derived: $7.96\text{ MHz}$).
  - Phase Margin: $\text{PM} \ge 60.0^\circ$. (Nominal derived: $68^\circ - 70^\circ$).
- **Acceptance Criteria:** $A_0 \ge 60\text{ dB}$, $\text{GBW} \ge 5\text{ MHz}$, $\text{PM} \ge 60^\circ$.

### Test FULL-02: Large-Signal Transient Step Response (Unity-Gain Buffer)
- **Objective:** Measure large-signal settling time, closed-loop tracking accuracy, overshoot, and Slew Rate ($\text{SR}$).
- **Input Conditions:** Op-amp connected in closed-loop unity-gain buffer configuration ($V_{in-} \leftarrow V_{out}$). Input step from $0.40\text{ V}$ to $0.50\text{ V}$ ($+100\text{ mV}$) applied at $t = 5.0\ \mu\text{s}$.
- **Expected Result:**
  - Slew rate: $\text{SR} = \frac{I_{tail}}{C_c} = \frac{2.0\ \mu\text{A}}{0.5\text{ pF}} = 4.0\text{ V}/\mu\text{s}$.
  - Slew transition time for $100\text{ mV}$: $\Delta t = \frac{0.10\text{ V}}{4.0\text{ V}/\mu\text{s}} = 0.025\ \mu\text{s} = 25\text{ ns}$.
  - Settling to $0.50\text{ V}$ without oscillatory ringing due to high phase margin ($\text{PM} \approx 70^\circ$).
- **Acceptance Criteria:** Steady-state tracking error $< 0.1\%$, $\text{SR} \ge 2.0\text{ V}/\mu\text{s}$, zero sustained oscillation.

### Test FULL-03: Static Power Dissipation Benchmark
- **Objective:** Measure total DC supply current and verify power savings against standard all-CMOS op-amp baselines.
- **Calculation:**
  $$P_{total} = V_{DD} \cdot I_{total} = 0.8\text{ V} \times (I_{tail} + I_{SET\_stage} + I_{buffer})$$
  $$P_{total} \approx 0.8\text{ V} \times (2.0\ \mu\text{A} + 0.3\ \mu\text{A} + 5.0\ \mu\text{A}) = 5.84\ \mu\text{W}$$
- **Benchmark Baseline:** Conventional 2-stage CMOS op-amp consumes $50\ \mu\text{W} - 150\ \mu\text{W}$ at comparable bandwidth.
- **Acceptance Criteria:** $P_{total} \le 10.0\ \mu\text{W}$ (demonstrating $\ge 8\times$ power reduction).

### Test FULL-04: Room-Temperature Coulomb Blockade Stability
- **Objective:** Verify that chosen SET parameters satisfy physical single-electron tunneling criteria at $T = 300\text{ K}$.
- **Evaluation:**
  - Total island capacitance: $C_{\Sigma} = C_1 + C_2 + C_g = 0.55\text{ aF}$.
  - Charging energy: $E_C = \frac{e^2}{2 C_{\Sigma}} = 0.1456\text{ eV} = 145.6\text{ meV}$.
  - Thermal energy at $300\text{ K}$: $k_B T = 25.86\text{ meV}$.
  - Ratio: $\frac{E_C}{k_B T} = \frac{145.6}{25.86} = 5.63 > 5.0$.
- **Acceptance Criteria:** $\frac{E_C}{k_B T} \ge 5.0$, $R_1, R_2 \gg 25.81\text{ k}\Omega$.
