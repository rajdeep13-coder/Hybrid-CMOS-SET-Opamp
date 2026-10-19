%% derive_or_configure_parameters.m
% Computes, derives, and exports all device, circuit, and bias parameters
% for the Hybrid CMOS-SET Operational Amplifier simulation.

function params = derive_or_configure_parameters(mode)
    if nargin < 1
        mode = 'room_temp'; % Options: 'room_temp' (300 K) or 'cryogenic' (4.2 K)
    end

    fprintf('Configuring Hybrid CMOS-SET parameters for mode: %s...\n', mode);

    params = struct();
    params.mode = mode;
    
    % Fundamental Constants
    params.q = 1.602176634e-19;     % Electron charge (C)
    params.kB = 1.380649e-23;       % Boltzmann constant (J/K)
    params.h = 6.62607015e-34;      % Planck constant (J*s)
    params.Rq = params.h / (params.q^2); % Quantum resistance ~ 25.81 kOhm

    % Supply and Biasing Rails
    params.Vdd = 0.8;               % Positive power supply (V) (Jana et al. 2013)
    params.Vss = 0.0;               % Negative power supply / Ground (V)
    params.Vicm = 0.4;              % Nominal input common-mode voltage (V) (Vdd/2)

    % SET Device Parameters
    if strcmpi(mode, 'room_temp')
        params.T = 300.0;           % Temperature in Kelvin
        params.C1 = 0.15e-18;       % Source tunnel junction capacitance (F)
        params.C2 = 0.15e-18;       % Drain tunnel junction capacitance (F)
        params.Cg = 0.25e-18;       % Gate capacitance (F)
        params.R1 = 1.0e6;          % Source tunnel junction resistance (Ohm)
        params.R2 = 1.0e6;          % Drain tunnel junction resistance (Ohm)
    else
        params.T = 4.2;             % Liquid Helium temperature in Kelvin
        params.C1 = 1.0e-18;        % Junction 1 capacitance (F)
        params.C2 = 1.0e-18;        % Junction 2 capacitance (F)
        params.Cg = 2.0e-18;        % Gate capacitance (F)
        params.R1 = 1.0e5;          % Junction 1 resistance (Ohm)
        params.R2 = 1.0e5;          % Junction 2 resistance (Ohm)
    end
    params.Q0 = 0.0;                % Background / offset charge (C)
    
    % Derived SET Metrics
    params.C_sigma = params.C1 + params.C2 + params.Cg;      % Total island capacitance (F)
    params.Ec = (params.q^2) / (2 * params.C_sigma);         % Charging energy (Joules)
    params.Ec_eV = params.Ec / params.q;                     % Charging energy (eV)
    params.kBT_eV = (params.kB * params.T) / params.q;       % Thermal energy (eV)
    params.Ec_to_kBT_ratio = params.Ec / (params.kB * params.T);
    params.delta_Vg = params.q / params.Cg;                  % Coulomb oscillation period (V)
    params.Vth_SET = params.q / params.C_sigma;              % Coulomb blockade threshold (V)

    % Stage 1: CMOS Differential Input Stage
    params.Itail = 2.0e-6;          % Tail current source (A)
    params.gm1 = 25.0e-6;           % Transconductance (S)
    params.ro1 = 2.0e6;             % Output impedance of stage 1 (Ohm)
    params.Rtail = 5.0e6;           % Tail current source output impedance (Ohm)
    params.Av1_diff = params.gm1 * params.ro1; % Differential voltage gain ~ 50 V/V (34 dB)
    params.Av1_cm = -params.ro1 / (2 * params.Rtail); % Common-mode gain ~ -0.2 V/V (-14 dB)
    params.CMRR1 = abs(params.Av1_diff / params.Av1_cm); % CMRR ~ 250 (48 dB)

    % Stage 2: Hybrid SET-CMOS Gain and Integrating Stage ("Integral Section")
    params.gm2 = 40.0e-6;           % Driver MOSFET transconductance (S)
    params.ro_cmos2 = 2.5e6;        % Driver MOSFET output impedance (Ohm)
    params.rds_SET = 10.0e6;        % Dynamic output impedance of SET active load (Ohm)
    params.ro2 = 1 / (1/params.ro_cmos2 + 1/params.rds_SET); % Combined node impedance ~ 2.0 MOhm
    params.Cc = 0.5e-12;            % Miller compensation / integration capacitance (F)
    params.Av2 = params.gm2 * params.ro2; % Stage 2 voltage gain ~ 80 V/V (38 dB)
    params.fp2 = 1 / (2 * pi * params.ro2 * params.Cc); % Dominant integrator pole ~ 159 Hz

    % Stage 3: CMOS Output Buffer
    params.gm3 = 250.0e-6;          % Buffer MOSFET transconductance (S)
    params.Rout3 = 1 / params.gm3;  % Output buffer impedance ~ 4 kOhm
    params.RL = 100.0e3;            % External load resistance (Ohm)
    params.CL = 2.0e-12;            % External load capacitance (F)
    params.Av3 = (params.gm3 * params.RL) / (1 + params.gm3 * params.RL); % Gain ~ 0.96 V/V (~0 dB)

    % Overall Cascade Op-Amp Parameters
    params.A0 = params.Av1_diff * params.Av2 * params.Av3; % Total DC open-loop gain ~ 3840 V/V (71.7 dB)
    params.A0_dB = 20 * log10(params.A0);
    params.GBW_Hz = params.gm1 / (2 * pi * params.Cc);     % Gain-Bandwidth Product ~ 7.96 MHz
    params.SlewRate = params.Itail / params.Cc;             % Slew rate ~ 4.0 V/us
    params.I_total_est = params.Itail + 0.3e-6 + 5.0e-6;    % Estimated quiescent current ~ 7.3 uA
    params.Pdiss_est_uW = params.Vdd * params.I_total_est * 1e6; % Estimated power ~ 5.84 uW

    % Integration / Testbench Parameters
    params.R_int = 100.0e3;         % Input resistor for closed-loop integrator configuration (Ohm)
    params.tau_int = params.R_int * params.Cc; % Integrator time constant ~ 50 us

    % Export to Base Workspace
    assignin('base', 'OpAmpParams', params);
    assignin('base', 'SET_Params', params);

    % Save to data file
    projectRoot = fileparts(fileparts(mfilename('fullpath')));
    dataPath = fullfile(projectRoot, 'simulink', 'data', 'set_parameters.mat');
    try
        save(dataPath, 'params');
        fprintf('Saved parameters struct to %s\n', dataPath);
    catch ME
        warning('Could not save MAT file: %s', ME.message);
    end

    fprintf('Parameter derivation complete. Estimated Open-Loop Gain: %.2f dB, GBW: %.2f MHz, Est Power: %.2f uW.\n', ...
        params.A0_dB, params.GBW_Hz / 1e6, params.Pdiss_est_uW);
end
