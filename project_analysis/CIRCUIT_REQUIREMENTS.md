# Circuit Requirements Specification

**Project:** Hybrid CMOS–SET Operational Amplifier  
**Document Ref:** ENG-REQ-HYBRID-OPAMP-001  
**Revision:** 1.0  
**Date:** October 19, 2026  

---

## 1. System Architecture Overview

The Hybrid CMOS–SET Operational Amplifier consists of three cascaded stages:

```
                  +-------------------------------------------------------------+
                  |               COMPLETE HYBRID OP-AMP                        |
                  |                                                             |
   Vin+ >-------->| +----------------+    +----------------+    +-------------+ |
                  | | CMOS Diff      |    | Hybrid SET-MOS |    | CMOS Output | |
   Vin- >-------->| | Input Stage    |--->| Gain/Integrator|--->| Buffer      |---> Vout
                  | | (gm1, tail)    |    | Stage (Cc, SET)|    | (Unity Gain)| |
                  | +----------------+    +----------------+    +-------------+ |
                  +-------------------------------------------------------------+
```

### Stage 1: CMOS Differential Input Stage
- **Function:** Rejects common-mode signals, converts differential input voltage $\Delta V_{in} = V_{in+} - V_{in-}$ into intermediate single-ended current/voltage, provides initial transconductance $g_{m1}$.
- **Topology:** Symmetrical NMOS (or PMOS) differential pair with active current-mirror load and a stable tail-current source $I_{tail}$.
- **Key Equations:**
  - Differential transconductance: $g_{m1} = \sqrt{2 \mu_n C_{ox} (W/L)_1 \cdot (I_{tail}/2)} = \frac{I_{tail}}{V_{ov1}}$
  - Stage 1 Output Resistance: $r_{o1} = r_{o,pair} \parallel r_{o,mirror} = \frac{1}{(\lambda_n + \lambda_p) I_{tail}/2}$
  - Stage 1 Voltage Gain: $A_{vd1} = g_{m1} \cdot r_{o1}$
  - Common-Mode Gain: $A_{vcm1} \approx -\frac{1}{2 g_{m,mirror} R_{tail}} \approx \frac{-r_{o1}}{2 R_{tail}}$
  - Common-Mode Rejection Ratio: $\text{CMRR} = \frac{|A_{vd1}|}{|A_{vcm1}|} \approx 2 g_{m1} R_{tail}$

### Stage 2: Hybrid SET-CMOS Gain & Integrating Stage ("Integral Section")
- **Function:** Provides high voltage amplification and determines dominant frequency pole through Miller integration capacitance $C_c$.
- **Topology:** A CMOS common-source driver transistor paired with a Single-Electron Transistor (SET) acting as an ultra-high incremental impedance active load pull-down/pull-up, bridged by Miller compensation capacitor $C_c$.
- **Why this is the "Integral Section":**
  - In two-stage op-amp dynamics, the stage with feedback capacitor $C_c$ is mathematically and physically an **active Miller Integrator**.
  - Current flowing into the intermediate node charges $C_c$, producing the governing differential equation:
    $$C_c \frac{d(V_{out2} - V_{in2})}{dt} = - g_{m2} V_{in2} - \frac{V_{out2}}{r_{o2}} - I_{SET}(V_{out2}, V_{gate,SET})$$
  - In small-signal Laplace domain:
    $$\frac{V_{out2}(s)}{V_{in2}(s)} \approx - \frac{g_{m2} - s C_c}{g_{o2} + s C_c} \approx - \frac{g_{m2}}{s C_c}$$
  - For external testing as an active integrator circuit, closing the loop with an input resistor $R_{in}$ yields:
    $$V_{out}(t) = - \frac{1}{R_{in} C_c} \int_0^t V_{in}(\tau) d\tau + V_o(0)$$

### Stage 3: CMOS Output Buffer
- **Function:** Low output impedance driver to isolate the high-impedance SET gain stage from variable resistive and capacitive external loads ($R_L, C_L$).
- **Topology:** CMOS common-drain (source follower) or push-pull complementary class-AB buffer.
- **Key Equations:**
  - Buffer gain: $A_{v3} \approx \frac{g_{m3} R_L}{1 + g_{m3} R_L} \approx 1$
  - Output impedance: $R_{out} \approx \frac{1}{g_{m3}} \ll r_{o2}$

---

## 2. Electrical Specifications & Operating Conditions

| Parameter | Symbol | Nominal Value | Range / Tolerance | Status / Source |
| :--- | :--- | :--- | :--- | :--- |
| **Positive Power Supply** | $V_{DD}$ | $0.8\text{ V}$ | $0.7\text{ V} - 1.0\text{ V}$ | Supported (Jana et al. 2013, Synopsis) |
| **Negative Power Supply / Ground**| $V_{SS}$ | $0.0\text{ V}$ | Ground reference | Supported (Single supply topology) |
| **Input Common-Mode Bias** | $V_{ICM}$ | $0.4\text{ V}$ | $0.3\text{ V} - 0.5\text{ V}$ | Derived ($V_{DD}/2$ for maximum dynamic range) |
| **Tail Bias Current** | $I_{tail}$ | $2.0\ \mu\text{A}$ | $0.5\ \mu\text{A} - 10\ \mu\text{A}$ | Derived for low-power operation |
| **Differential Input Transconductance** | $g_{m1}$ | $25\ \mu\text{S}$ | $10\ \mu\text{S} - 50\ \mu\text{S}$ | Derived from CMOS subthreshold/weak inversion |
| **Stage 1 Output Resistance** | $r_{o1}$ | $2.0\text{ M}\Omega$ | $1.0\text{ M}\Omega - 5.0\text{ M}\Omega$ | Derived from MOSFET channel length modulation |
| **Intermediate Driver Transconductance** | $g_{m2}$ | $40\ \mu\text{S}$ | $20\ \mu\text{S} - 100\ \mu\text{S}$ | Derived |
| **SET Incremental Output Resistance** | $r_{ds,SET}$ | $10.0\text{ M}\Omega$ | $5.0\text{ M}\Omega - 50.0\text{ M}\Omega$ | Supported by SET Coulomb blockade impedance |
| **Miller Compensation Capacitance** | $C_c$ | $0.5\text{ pF}$ | $0.2\text{ pF} - 2.0\text{ pF}$ | Derived for $\text{GBW} \approx 8\text{ MHz}$, $\text{PM} > 60^\circ$ |
| **Output Buffer Transconductance** | $g_{m3}$ | $250\ \mu\text{S}$ | $100\ \mu\text{S} - 500\ \mu\text{S}$ | Derived for $R_{out} \approx 4\text{ k}\Omega$ |
| **External Capacitive Load** | $C_L$ | $2.0\text{ pF}$ | $1.0\text{ pF} - 10.0\text{ pF}$ | Standard analog testbench load |
| **External Resistive Load** | $R_L$ | $100\text{ k}\Omega$ | $10\text{ k}\Omega - \infty$ | Standard load |
| **Operating Temperature** | $T$ | $300\text{ K}$ | $4.2\text{ K} - 300\text{ K}$ | Supported (Room temperature target) |

---

## 3. SET Device Parameters

| Parameter | Symbol | Value (Room Temp 300 K) | Value (Cryogenic 4.2 K) | Source / Justification |
| :--- | :--- | :--- | :--- | :--- |
| **Junction 1 Capacitance** | $C_1$ | $0.15\text{ aF}\ (0.15 \times 10^{-18}\text{ F})$ | $1.0\text{ aF}\ (1.0 \times 10^{-18}\text{ F})$ | Supported by Jana et al. / `init_workspace.m` |
| **Junction 2 Capacitance** | $C_2$ | $0.15\text{ aF}\ (0.15 \times 10^{-18}\text{ F})$ | $1.0\text{ aF}\ (1.0 \times 10^{-18}\text{ F})$ | Symmetrical junction assumption |
| **Gate Capacitance** | $C_g$ | $0.25\text{ aF}\ (0.25 \times 10^{-18}\text{ F})$ | $2.0\text{ aF}\ (2.0 \times 10^{-18}\text{ F})$ | Sets Coulomb oscillation period $\Delta V_g$ |
| **Total Island Capacitance** | $C_{\Sigma}$ | $0.55\text{ aF}\ (0.55 \times 10^{-18}\text{ F})$ | $4.0\text{ aF}\ (4.0 \times 10^{-18}\text{ F})$ | $C_1 + C_2 + C_g$ |
| **Junction 1 Tunnel Resistance**| $R_1$ | $1.0\text{ M}\Omega\ (10^6\ \Omega)$ | $100\text{ k}\Omega\ (10^5\ \Omega)$ | $> R_Q = 25.8\text{ k}\Omega$ (quantum limit) |
| **Junction 2 Tunnel Resistance**| $R_2$ | $1.0\text{ M}\Omega\ (10^6\ \Omega)$ | $100\text{ k}\Omega\ (10^5\ \Omega)$ | Symmetric tunnel barrier |
| **Background / Offset Charge** | $Q_0$ | $0.0\text{ C}$ | $0.0\text{ C}$ | Ideal baseline assumption |

---

## 4. Expected Performance Metrics

| Performance Metric | Symbol | Target Value | Baseline CMOS Comparison | Evaluation Mode |
| :--- | :--- | :--- | :--- | :--- |
| **DC Open-Loop Gain** | $A_{0}$ | $\ge 60\text{ dB}\ (1,000\text{ V/V})$ | $40 - 55\text{ dB}$ | Full Op-Amp AC / DC |
| **Gain-Bandwidth Product** | $\text{GBW}$ | $\ge 5\text{ MHz}$ | $2 - 10\text{ MHz}$ | AC small-signal sweep |
| **Phase Margin** | $\text{PM}$ | $\ge 60^\circ$ | $45^\circ - 65^\circ$ | AC Bode plot at $0\text{ dB}$ cross |
| **Common-Mode Rejection** | $\text{CMRR}$ | $\ge 65\text{ dB}$ | $50 - 70\text{ dB}$ | Differential vs Common mode |
| **Slew Rate** | $\text{SR}$ | $\ge 2.0\text{ V}/\mu\text{s}$ | $1.0 - 5.0\text{ V}/\mu\text{s}$ | Large-signal transient pulse |
| **Total Power Consumption** | $P_{diss}$ | $\le 10\ \mu\text{W}$ | $50 - 150\ \mu\text{W}$ | Static DC supply current |
| **Output Voltage Swing** | $V_{swing}$ | $0.1\text{ V} - 0.7\text{ V}$ | $0.15\text{ V} - 0.65\text{ V}$ | Large-signal linear range |

---

## 5. Traceability and Verification Requirements

1. **Differential Model (`Hybrid_OpAmp_Differential.slx`):**
   - Must prove differential gain $A_{vd1} \ge 25\text{ dB}$.
   - Must reject common-mode inputs by $> 60\text{ dB}$.
   - Must demonstrate symmetrical balanced operation around $V_{ICM} = 0.4\text{ V}$.

2. **Integral Model (`Hybrid_OpAmp_Integral.slx`):**
   - Must demonstrate integration dynamics: $V_{out}(t) \propto \int V_{in}(t) dt$.
   - Must exhibit finite DC gain saturation (non-ideal practical integrator behavior).
   - Must exhibit stable transient step, pulse, and sinusoidal frequency roll-off ($-20\text{ dB/decade}$).

3. **Complete Op-Amp Model (`Hybrid_OpAmp_Full.slx`):**
   - Must connect the differential front-end to the hybrid SET-CMOS integrating stage and output buffer.
   - Must successfully run open-loop AC analysis and closed-loop buffer/inverting testbenches.
   - Must log power dissipation and confirm power advantage over traditional multi-stage CMOS amplifiers.
