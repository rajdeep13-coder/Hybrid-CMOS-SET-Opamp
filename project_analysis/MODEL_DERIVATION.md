# Mathematical and Circuit Model Derivation

**Project:** Hybrid CMOS–SET Operational Amplifier  
**Document Ref:** DERIV-001  
**Revision:** 1.0  
**Date:** October 19, 2026  

---

## 1. Single-Electron Transistor (SET) Analytical Model

### 1.1 Physical Principles & Orthodox Theory
The Single-Electron Transistor consists of a small conducting island (quantum dot) separated from source and drain reservoirs by two tunnel barriers (capacitances $C_1, C_2$, tunnel resistances $R_1, R_2$) and capacitively coupled to an external gate electrode ($C_g$).

```
                 Vd (Drain)
                     |
                   [ C2, R2 ] (Tunnel Junction 2)
                     |
         Vg ------[ Cg ]------ (Island, Q)
                     |
                   [ C1, R1 ] (Tunnel Junction 1)
                     |
                 Vs (Source)
```

The total island capacitance is:
$$C_{\Sigma} = C_1 + C_2 + C_g$$

The electrostatic charging energy required to add a single electron of charge $e = 1.6022 \times 10^{-19}\text{ C}$ to the neutral island is:
$$E_C = \frac{e^2}{2 C_{\Sigma}}$$

For single-electron tunneling to dominate over thermal and quantum fluctuations:
1. **Thermal Criterion:**
   $$E_C \gg k_B T \implies \frac{e^2}{2 C_{\Sigma}} \gg k_B T$$
   At room temperature ($T = 300\text{ K}$), $k_B T \approx 25.86\text{ meV}$. For stable operation ($E_C \ge 10 k_B T \approx 260\text{ meV}$):
   $$C_{\Sigma} \le \frac{e^2}{2 \times 0.26\text{ eV}} \approx 0.31\text{ aF} = 3.1 \times 10^{-19}\text{ F}$$
   At cryogenic temperatures ($T = 4.2\text{ K}$), $k_B T \approx 0.36\text{ meV}$, allowing capacitances up to $C_{\Sigma} \approx 20\text{ aF}$.

2. **Quantum Resistance Criterion:**
   To localize electrons on the island and prevent quantum wave-packet smearing:
   $$R_1, R_2 \gg R_Q = \frac{h}{e^2} \approx 25.81\text{ k}\Omega$$
   Typically, tunnel resistances are chosen in the range $R_T \in [10^5\ \Omega, 10^7\ \Omega]$.

### 1.2 Orthodox Tunneling Rates
Under the orthodox theory of single-electron tunneling, the free energy change when an electron tunnels across junction 1 or 2 is:
$$\Delta F_{1\pm} = \pm \frac{e}{C_{\Sigma}} \left[ C_g(V_g - V_s) + C_2(V_d - V_s) + Q_0 \right] - \frac{e^2}{2 C_{\Sigma}}$$
$$\Delta F_{2\pm} = \pm \frac{e}{C_{\Sigma}} \left[ C_g(V_g - V_d) + C_1(V_s - V_d) + Q_0 \right] - \frac{e^2}{2 C_{\Sigma}}$$

The tunneling transition rate $\Gamma_i$ across barrier $i$ is:
$$\Gamma_i(\Delta F) = \frac{\Delta F}{e^2 R_i \left( 1 - \exp\left( -\frac{\Delta F}{k_B T} \right) \right)}$$

### 1.3 Compact Closed-Form Expression (Uchida / MIB Model)
For symmetric devices ($C_1 = C_2 = C_T$, $R_1 = R_2 = R_T$), the steady-state drain current can be expressed in closed analytical form:

$$I_{ds}(V_{ds}, V_{gs}, T) = \frac{V_{ds}}{2 R_T} \cdot \frac{\sinh\left( \frac{e V_{ds}}{2 k_B T} \right)}{\cosh\left( \frac{e V_{ds}}{2 k_B T} \right) + \cosh\left( \frac{e (V_{gs} - V_{g0})}{k_B T \cdot (C_{\Sigma} / C_g)} \right)} \cdot \left[ 1 - \exp\left( -\frac{|V_{ds}|}{V_{th,SET}} \right) \right]$$

where:
- $\Delta V_{gs} = \frac{e}{C_g}$ is the period of Coulomb oscillations.
- $V_{g0}$ is the gate voltage corresponding to the peak of the Coulomb conductance.
- $V_{th,SET} = \frac{e}{C_{\Sigma}}$ is the Coulomb blockade threshold voltage.
- When $|V_{ds}| < V_{th,SET}$ and $V_{gs}$ is off-resonance, $I_{ds} \approx 0$ (Coulomb blockade).
- Incremental output conductance in the active region:
  $$g_{ds,SET} = \frac{\partial I_{ds}}{\partial V_{ds}} \approx \frac{1}{r_{ds,SET}} \ll \frac{1}{R_T}$$
  yielding an extremely large incremental resistance $r_{ds,SET} \sim 10\text{ M}\Omega - 100\text{ M}\Omega$.

---

## 2. CMOS Differential Input Stage Formulation

The first stage is a balanced CMOS differential pair with an active current-mirror load.

### 2.1 Differential and Common-Mode Transfer
For an input differential signal $v_{id} = V_{in+} - V_{in-}$ with common-mode level $V_{ICM} = \frac{V_{in+} + V_{in-}}{2}$:
- Tail current $I_{tail}$ divides equally in quiescent equilibrium: $I_{D1} = I_{D2} = \frac{I_{tail}}{2}$.
- Differential transconductance:
  $$g_{m1} = \frac{I_{tail}}{V_{OV1}} = \sqrt{2 \mu_n C_{ox} \left(\frac{W}{L}\right)_1 \frac{I_{tail}}{2}}$$
- Small-signal differential current injected into the active mirror load:
  $$i_{out1} = g_{m1} \cdot v_{id}$$
- Output resistance at the single-ended output node:
  $$r_{o1} = r_{ds,n1} \parallel r_{ds,p1} = \frac{1}{(\lambda_n + \lambda_p) (I_{tail}/2)}$$
- First-stage differential voltage gain:
  $$A_{vd1} = \frac{v_{o1}}{v_{id}} = g_{m1} \cdot r_{o1}$$
- Common-mode voltage gain:
  $$A_{vcm1} \approx - \frac{1}{2 g_{m,mirror} R_{tail}} \approx - \frac{r_{o1}}{2 R_{tail}}$$
- Common-Mode Rejection Ratio (CMRR):
  $$\text{CMRR} = \left|\frac{A_{vd1}}{A_{vcm1}}\right| \approx 2 g_{m1} R_{tail}$$
  With an active cascode tail or long-channel current source having $R_{tail} \ge 5\text{ M}\Omega$ and $g_{m1} = 25\ \mu\text{S}$:
  $$\text{CMRR} \approx 2 \times (25 \times 10^{-6}) \times (5 \times 10^6) = 250 \approx 48\text{ dB} \text{ (basic)} \to 70\text{ dB (active load)}$$

---

## 3. Hybrid SET-CMOS Gain and Integrating Stage ("Integral Section")

### 3.1 Architecture and Dynamics
The second stage consists of a CMOS driver transistor (PMOS or NMOS) combined with an SET operating as an ultra-high impedance active load, shunted by a Miller compensation capacitor $C_c$.

```
                       VDD
                        |
                 [ CMOS Driver ] (gm2, ro2)
                        |
            Vin2 -------+-------- Vout2
                        |      |
                    [  SET  ] [ Cc ] (Feedback)
                    [  Load ]  |
                        |      |
                       GND <---+
```

### 3.2 State-Space and Differential Equation
Applying Kirchhoff's Current Law (KCL) at the intermediate node $V_{out2}$:

$$C_c \frac{d(V_{out2} - V_{in2})}{dt} + I_{CMOS}(V_{in2}, V_{out2}) + I_{SET}(V_{out2}) + \frac{V_{out2}}{R_{load2}} = 0$$

Linearizing around the DC operating point ($V_{in20}, V_{out20}$):
$$I_{CMOS} \approx I_{Q2} + g_{m2} v_{in2} + g_{ds2} v_{out2}$$
$$I_{SET} \approx I_{Q2} + g_{ds,SET} v_{out2}$$

Let total nodal output conductance be $g_{o2} = g_{ds2} + g_{ds,SET} + \frac{1}{R_{load2}} = \frac{1}{r_{o2}}$.  
Then:
$$C_c \frac{d v_{out2}}{dt} - C_c \frac{d v_{in2}}{dt} + g_{m2} v_{in2} + g_{o2} v_{out2} = 0$$

Taking the Laplace transform ($v(0) = 0$):
$$s C_c V_{out2}(s) + g_{o2} V_{out2}(s) = s C_c V_{in2}(s) - g_{m2} V_{in2}(s)$$

$$\frac{V_{out2}(s)}{V_{in2}(s)} = - \frac{g_{m2} - s C_c}{g_{o2} + s C_c} = - \frac{g_{m2} r_{o2} \left( 1 - s \frac{C_c}{g_{m2}} \right)}{1 + s C_c r_{o2}}$$

### 3.3 The Integrator Interpretation
At frequencies above the open-loop pole $\omega_{p2} = \frac{1}{r_{o2} C_c}$ (typically $\sim 100\text{ Hz}$ to $1\text{ kHz}$):
$$\frac{V_{out2}(s)}{V_{in2}(s)} \approx - \frac{g_{m2}}{s C_c}$$

In the time domain, this represents direct mathematical integration:
$$v_{out2}(t) = - \frac{g_{m2}}{C_c} \int_0^t v_{in2}(\tau) d\tau + v_{out2}(0)$$

When configured as a standalone active integrator with an input series resistor $R_{in}$:
$$H(s) = \frac{V_{out}(s)}{V_{in}(s)} = - \frac{1}{s R_{in} C_c}$$
$$v_{out}(t) = - \frac{1}{R_{in} C_c} \int_0^t v_{in}(\tau) d\tau$$

Saturation limits are enforced by supply rails:
$$0.05\text{ V} \le V_{out2}(t) \le V_{DD} - 0.05\text{ V}$$

---

## 4. Complete Operational Amplifier Cascade

### 4.1 Overall Transfer Function
Cascading the three stages:
1. Differential Stage: $A_1(s) = \frac{A_{vd1}}{1 + s / \omega_{p1}}$
2. Hybrid SET-CMOS Integrating Stage: $A_2(s) = \frac{-A_{v2} (1 - s / \omega_z)}{1 + s / \omega_{p2,eff}}$
3. Output Buffer: $A_3(s) \approx \frac{A_{v3}}{1 + s / \omega_{p3}} \approx 1$

Through the Miller effect, the effective capacitance at the output of Stage 1 is multiplied by the stage 2 gain:
$$C_{in,eff2} \approx C_c (1 + |A_{v2}|)$$
This creates the **dominant pole** of the entire amplifier at:
$$\omega_p \approx \frac{1}{r_{o1} C_c |A_{v2}|} = \frac{1}{r_{o1} C_c (g_{m2} r_{o2})}$$

### 4.2 DC Gain and Gain-Bandwidth Product (GBW)
- DC Open-Loop Gain:
  $$A_0 = A_{vd1} \cdot |A_{v2}| \cdot A_{v3} = (g_{m1} r_{o1}) \cdot (g_{m2} r_{o2}) \cdot 1$$
- Gain-Bandwidth Product (unity-gain frequency):
  $$\text{GBW} = A_0 \cdot \omega_p = \frac{g_{m1} r_{o1} \cdot g_{m2} r_{o2}}{r_{o1} C_c g_{m2} r_{o2}} = \frac{g_{m1}}{C_c}$$
  For $g_{m1} = 25\ \mu\text{S}$ and $C_c = 0.5\text{ pF}$:
  $$\text{GBW} = \frac{25 \times 10^{-6}\text{ S}}{0.5 \times 10^{-12}\text{ F}} = 50 \times 10^6\text{ rad/s} \approx 7.96\text{ MHz}$$

### 4.3 Phase Margin (PM)
The second pole occurs at the output buffer / load node:
$$\omega_{p,nd} \approx \frac{g_{m3}}{C_L}$$
For $g_{m3} = 250\ \mu\text{S}$ and $C_L = 2\text{ pF}$:
$$\omega_{p,nd} = \frac{250 \times 10^{-6}}{2 \times 10^{-12}} = 125 \times 10^6\text{ rad/s} \approx 19.9\text{ MHz}$$
Since $\omega_{p,nd} \approx 2.5 \times \text{GBW}$, the phase margin is:
$$\text{PM} \approx 90^\circ - \arctan\left(\frac{\text{GBW}}{\omega_{p,nd}}\right) \approx 90^\circ - \arctan\left(\frac{7.96}{19.9}\right) \approx 90^\circ - 21.8^\circ = 68.2^\circ$$
This satisfies the required stability margin ($\text{PM} \ge 60^\circ$).

### 4.4 Slew Rate (SR)
The maximum charging current into the Miller capacitor is limited by the tail current $I_{tail}$ of the input differential pair:
$$\text{SR} = \frac{I_{tail}}{C_c} = \frac{2.0 \times 10^{-6}\text{ A}}{0.5 \times 10^{-12}\text{ F}} = 4.0 \times 10^6\text{ V/s} = 4.0\text{ V}/\mu\text{s}$$

### 4.5 Static Power Consumption
Total DC supply current:
$$I_{total} = I_{tail} + I_{SET\_stage} + I_{buffer}$$
Where:
- $I_{tail} = 2.0\ \mu\text{A}$
- $I_{SET\_stage} \approx 0.1\ \mu\text{A} - 0.5\ \mu\text{A}$ (ultra-low due to SET high tunnel resistance and Coulomb blockade)
- $I_{buffer} \approx 5.0\ \mu\text{A}$
$$I_{total} \approx 2.0 + 0.3 + 5.0 = 7.3\ \mu\text{A}$$
Total power dissipation at $V_{DD} = 0.8\text{ V}$:
$$P_{total} = 0.8\text{ V} \times 7.3\ \mu\text{A} = 5.84\ \mu\text{W}$$
This is roughly an order of magnitude lower than conventional all-CMOS op-amps operating at similar bandwidths ($50 - 150\ \mu\text{W}$).
