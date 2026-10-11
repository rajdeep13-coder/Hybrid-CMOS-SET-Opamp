# Hybrid CMOS-SET Operational Amplifier (Op-Amp)

A research and design repository for a hybrid Single-Electron Transistor (SET) and Complementary Metal-Oxide-Semiconductor (CMOS) operational amplifier. This project investigates integration schemes, macro-modeling of SET devices, and simulation of high-gain, low-power hybrid analog building blocks.

## Project Overview
As CMOS scaling approaches fundamental physical limits, Single-Electron Transistors (SETs) offer a promising post-CMOS alternative with ultra-low power dissipation via the Coulomb blockade effect. However, standalone SETs suffer from poor current drivability and high output impedance. 

This project explores a **Hybrid CMOS-SET architecture** in the analog domain. By combining SET-level power efficiency with CMOS drive strength, we propose a hybrid Operational Amplifier. The design is modeled and simulated as a single, unified system within the MATLAB/Simulink environment, aiming to benchmark its gain, bandwidth, and power dissipation against conventional CMOS op-amps.


**Differential Amplifier Design & Biasing**
*   [GitHub: CMOS-Differential-MOSFET-Amplifier-Design](https://github.com/AidinFamiZagharami/CMOS-Differential-MOSFET-Amplifier-Design)
*   [GitHub: VLSI-Differential-Amplifier-Design](https://github.com/snehilraj1124-ship-it/VLSI-Differential-Amplifier-Design)
*   [NCKU Electronics Lab Lecture: Differential Amplifiers (PDF)](http://msic.ee.ncku.edu.tw/course/Electronics%20Lab%20II/202309/Lecture/Lab2.pdf)
*   [Electrical Flux: MOSFET Differential Amplifier Design & Biasing](https://electricalflux.com/learn-components/mosfet-differential-amplifier-design-biasing)

**Low-Power Op-Amps & Simulation Tooling**
*   [ResearchGate: Low Power Two Stage CMOS Operational Amplifier](https://www.researchgate.net/publication/391322961_Low_Power_Two_Stage_CMOS_Operational_Amplifier)
*   [MathWorks Docs: Simscape Electrical CMOS Logic](https://in.mathworks.com/help/simscape-electrical/ref/cmosand.html) (Reference for modeling custom logic and analog blocks)