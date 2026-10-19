# References and Assumptions Analysis

**Project:** Hybrid CMOS–SET Operational Amplifier  
**Document Ref:** REF-ASSUMP-001  
**Revision:** 1.0  
**Date:** October 19, 2026  

---

## 1. Reference Literature Review & Benchmark Mapping

The design and modeling methodology relies on peer-reviewed literature and standard VLSI reference designs:

### 1.1 Core SET Device and Macro-Model References
1. **El Kazdir, M. S., Rzaizi, M., El Assali, K., & Abouelaoualim, D. (2022).**  
   *"Design and simulation of hybrid SET-CMOS logic inverter using macro-model technique."*  
   *Revista Mexicana de Física*, 68(6), 061401. DOI: [10.31349/RevMexFis.68.061401](https://doi.org/10.31349/RevMexFis.68.061401).  
   *Relevance:* Direct benchmark cited in the project synopsis for modeling hybrid SET-CMOS architectures within MATLAB/Simulink Simscape environment. Confirmed room-temperature operability using equivalent macro-modeling.

2. **Jana, A., Singh, N. B., Sing, J. K., & Sarkar, S. K. (2013).**  
   *"Design and simulation of hybrid CMOS–SET circuits."*  
   *Microelectronics Reliability*, 53(4), 592–599. DOI: [10.1016/j.microrel.2012.11.006](https://doi.org/10.1016/j.microrel.2012.11.006).  
   *Relevance:* Primary reference in the synopsis and literature review for room-temperature SET parameters ($V_{DD} = 0.8\text{ V}$, sub-attofarad capacitances $C_1, C_2 \approx 0.15\text{ aF}, C_g \approx 0.25\text{ aF}$, $R_T \approx 1\text{ M}\Omega$). Demonstrates ~6x power savings over pure CMOS logic.

3. **Mahapatra, S., Vaish, V., Wasshuber, C., Banerjee, K., & Ionescu, A. M. (2004).**  
   *"Analytical modeling of single electron transistor for hybrid CMOS-SET analog/digital circuit design."*  
   *IEEE Transactions on Electron Devices*, 51(11), 1772–1782.  
   *Relevance:* Derives the MIB compact analytical model used for SPICE and mathematical simulations of SET devices under orthodox tunneling theory.

4. **Uchida, K., Matsuzawa, K., Koga, J., Ohba, R., Takagi, S.-I., & Toriumi, A. (2000).**  
   *"Analytical Single-Electron Transistor (SET) Model for Design and Analysis of Realistic SET Circuits."*  
   *Japanese Journal of Applied Physics*, 39(Part 1, No. 4B), 2321–2324. DOI: [10.1143/JJAP.39.2321](https://doi.org/10.1143/JJAP.39.2321).  
   *Relevance:* Formulates the closed-form analytical tunneling current equations with hyperbolic functions capturing Coulomb oscillations and thermal excitation across arbitrary drain-source voltages.

5. **Shah, R., Parekh, R., & Dhavse, R. (2021).**  
   *"Design strategy and simulation of single-gate SET for novel SETMOS hybridization."*  
   *Journal of Computational Electronics*, 20(1), 218–229.  
   *Relevance:* Investigates SETMOS biasing, threshold voltage shifts, and stability at room temperature.

### 1.2 Baseline Analog Op-Amp References
6. **Razavi, B. (2001).**  
   *Design of Analog CMOS Integrated Circuits.* McGraw-Hill, New York.  
   *Relevance:* Fundamental reference for CMOS differential pair sizing, transconductance calculation, active current mirrors, dominant-pole Miller compensation, CMRR, and output buffer stages.

7. **Allen, P. E., & Holberg, D. R. (2011).**  
   *CMOS Analog Circuit Design.* 3rd Edition, Oxford University Press.  
   *Relevance:* Methodologies for multi-stage low-power op-amp compensation, slew rate derivation, and phase margin analysis.

---

## 2. Explicit Classification of Project Information

```
+---------------------------------------------------------------------------------------+
|  SUPPORTED BY REPOSITORY:                                                             |
|  - 3-stage cascade: CMOS Diff -> Hybrid SET-CMOS Gain -> CMOS Output Buffer (Fig. 3)  |
|  - SET parameters in scripts/init_workspace.m (C1, C2, Cg, R1, R2, Temp)              |
|  - Supply voltage VDD = 0.8 V (Jana et al. 2013)                                      |
|  - Metric extraction targets: Adc, GBW, PM, SR, Power (scripts/extract_metrics.m)     |
+---------------------------------------------------------------------------------------+
                                           |
                                           v
+---------------------------------------------------------------------------------------+
|  MATHEMATICALLY DERIVED:                                                              |
|  - Differential transconductance gm1 = sqrt(2*mu*Cox*(W/L)*Id)                        |
|  - Miller integrator stage dynamics: Vo(s) = -gm2 / (s*Cc + go2) * Vi(s)              |
|  - Coulomb blockade charging energy: Ec = e^2 / (2*C_sigma)                           |
|  - Coulomb oscillation period: Delta Vg = e / Cg                                      |
|  - Closed-loop integrator transfer function: H(s) = -1 / (s * R * C)                  |
+---------------------------------------------------------------------------------------+
                                           |
                                           v
+---------------------------------------------------------------------------------------+
|  INTRODUCED ASSUMPTIONS:                                                              |
|  - Symmetrical SET junction capacitances: C1 = C2, R1 = R2                            |
|  - Zero background offset charge: Q0 = 0                                              |
|  - Input common-mode voltage: VICM = 0.4 V (mid-rail)                                 |
|  - Output buffer architecture: Common-drain source follower with Av ~ 1               |
|  - Dual implementation of "Integral": Both intermediate Miller stage and active R-C   |
+---------------------------------------------------------------------------------------+
                                           |
                                           v
+---------------------------------------------------------------------------------------+
|  UNRESOLVED ITEMS / LAB-SPECIFIC FACTORS:                                             |
|  - Specific foundry PDK parameters (e.g., TSMC 180nm vs 65nm)                         |
|  - Exact physical layout parasitic capacitances of interconnects                      |
|  - Random background charge fluctuation over time (1/f noise)                         |
+---------------------------------------------------------------------------------------+
```

---

## 3. Detailed Justification for Introduced Assumptions

### Assumption 1: Symmetrical SET Junctions ($C_1 = C_2$, $R_1 = R_2$)
- *Rationale:* In both the Uchida analytical model and the MIB compact model, symmetrical junctions represent the standard manufacturing target for single-island quantum dots. Asymmetry introduces non-zero offset current without improving small-signal transconductance.
- *Impact:* Guarantees smooth, well-defined Coulomb diamonds and simplifies parameter configuration.

### Assumption 2: Zero Initial Background Charge ($Q_0 = 0$)
- *Rationale:* Background charge trapped in substrate oxide fluctuates randomly in real hardware. In simulation and nominal design, $Q_0 = 0$ corresponds to the ideal Coulomb blockade center.
- *Impact:* Operating points and transfer curves remain deterministic. Parameter sweeps can vary $Q_0$ if background charge tolerance is tested.

### Assumption 3: Definition of "Integral Section"
- *Rationale:* In analog IC design, the second stage of a two-stage or three-stage amplifier with a compensation capacitor $C_c$ is mathematically an **active Miller integrator**. When tested as a standalone block, it integrates node currents onto $C_c$. Additionally, when configured in a closed loop, the entire op-amp or gain block acts as an active analog integrator.
- *Implementation Choice:* To eliminate all ambiguity:
  - Model 1 (`Hybrid_OpAmp_Integral.slx`) implements the hybrid SET-CMOS gain-integrating stage with compensation capacitor $C_c$, featuring test inputs for both open-loop step integration and closed-loop RC integration.
  - Model 2 (`Hybrid_OpAmp_Differential.slx`) implements the pure differential input stage with common-mode and differential inputs.
  - Model 3 (`Hybrid_OpAmp_Full.slx`) cascades all three stages into the complete operational amplifier.

### Assumption 4: Single Supply with Mid-Rail Reference ($V_{DD} = 0.8\text{ V}, V_{SS} = 0\text{ V}, V_{CM} = 0.4\text{ V}$)
- *Rationale:* Modern low-power IoT circuits employ single-supply rails. Mid-rail biasing ($0.4\text{ V}$) ensures maximum symmetric output voltage swing before saturation.
