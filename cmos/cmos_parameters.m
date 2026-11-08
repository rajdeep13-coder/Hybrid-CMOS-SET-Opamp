%% cmos_parameters.m
% =========================================================================
% CENTRAL PARAMETER SPECIFICATION FOR STANDALONE CMOS DIFFERENTIAL STAGE
% =========================================================================
% Academic Project: Hybrid CMOS-SET Operational Amplifier
% Milestone: Standalone Transistor-Level CMOS Differential Input Stage
%
% This script defines all electrical rails, transistor model parameters,
% physical dimensions, biasing conditions, test stimulus parameters, and
% numerical solver configurations.
%
% Compatible with:
% - MATLAB Simulink / Simscape Electrical models
% - Offline numerical cross-verification suites
% =========================================================================

function params = cmos_parameters(profile)
    if nargin < 1 || isempty(profile)
        profile = 'hybrid_synopsis_0v8'; % Default: 0.8 V rail matching project synopsis
    end

    fprintf('=================================================================\n');
    fprintf('Loading CMOS Differential Stage Parameters: Profile [%s]\n', profile);
    fprintf('=================================================================\n');

    params = struct();
    params.profile = profile;

    %% 1. Power Supply and Voltage Rails
    switch lower(profile)
        case 'hybrid_synopsis_0v8'
            % Intended operating condition from project synopsis (Jana et al. 2013)
            % Optimized for direct cascade into 0.8 V room-temperature SET stage
            params.Vdd = 0.8;               % Positive power supply rail (V)
            params.Vss = 0.0;               % Negative power supply rail / Ground (V)
            params.Vicm = 0.40;             % Input common-mode bias voltage (V) (mid-rail Vdd/2)
            params.Vth_n0 = 0.22;           % Low-Vt NMOS threshold voltage (V)
            params.Vth_p0 = -0.25;          % Low-Vt PMOS threshold voltage (V) (|Vth_p| = 0.25 V)
            params.note = 'Synopsis-aligned 0.8V low-voltage rail with low-Vt analog devices';

        case 'conventional_cmos_1v8'
            % Standard foundry 180nm CMOS baseline comparison
            params.Vdd = 1.8;               % Positive power supply rail (V)
            params.Vss = 0.0;               % Ground reference (V)
            params.Vicm = 0.90;             % Mid-rail common-mode voltage (V)
            params.Vth_n0 = 0.45;           % Standard NMOS threshold voltage (V)
            params.Vth_p0 = -0.45;          % Standard PMOS threshold voltage (V)
            params.note = 'Conventional 1.8V 180nm standard CMOS PDK baseline';

        case 'conventional_cmos_1v2'
            % 130nm / 65nm low-power standard CMOS baseline
            params.Vdd = 1.2;               % Positive power supply rail (V)
            params.Vss = 0.0;               % Ground reference (V)
            params.Vicm = 0.60;             % Mid-rail common-mode voltage (V)
            params.Vth_n0 = 0.35;           % Moderate-Vt NMOS threshold (V)
            params.Vth_p0 = -0.35;          % Moderate-Vt PMOS threshold (V)
            params.note = 'Conventional 1.2V low-power CMOS baseline';

        otherwise
            error('Unknown parameter profile: %s. Use hybrid_synopsis_0v8, conventional_cmos_1v8, or conventional_cmos_1v2', profile);
    end

    %% 2. Biasing and Tail Current Source
    params.Itail = 2.0e-6;                  % Total tail bias current (A) (2.0 uA)
    params.Rtail = 5.0e6;                   % Internal output impedance of tail current source (Ohm) (5 MOhm)
    params.C_tail = 15.0e-15;               % Parasitic capacitance at common-source node (F) (15 fF)
    params.Vtail_compliance = 0.10;         % Minimum required voltage across tail source for active compliance (V)

    %% 3. NMOS Input Differential Pair (M1, M2) Parameters
    % Matched transistors operating in saturation at quiescent point:
    % Id1 = Id2 = Itail / 2 = 1.0 uA
    params.nmos = struct();
    params.nmos.Vth = params.Vth_n0;        % Threshold voltage (V)
    params.nmos.Kp = 312.5e-6;              % Transconductance parameter Kp = mu_n * Cox * (W/L) (A/V^2)
    params.nmos.lambda = 0.25;              % Channel length modulation parameter (1/V)
    params.nmos.W = 1.6e-6;                 % Channel width (m) (1.6 um)
    params.nmos.L = 1.0e-6;                 % Channel length (m) (1.0 um)
    params.nmos.mu_Cox = 195.3e-6;          % Process transconductance mu_n * Cox (A/V^2)
    params.nmos.rd = 1.0;                   % Ohmic drain contact resistance (Ohm)
    params.nmos.rs = 1.0;                   % Ohmic source contact resistance (Ohm)
    params.nmos.Cgs = 12.0e-15;             % Gate-to-source capacitance (F) (12 fF)
    params.nmos.Cgd = 3.0e-15;              % Gate-to-drain overlap/Miller capacitance (F) (3 fF)
    params.nmos.Cdb = 4.0e-15;              % Drain-to-bulk junction capacitance (F) (4 fF)

    %% 4. PMOS Current Mirror Active Load (M3, M4) Parameters
    % M3: Diode-connected reference device (Gate tied to Drain)
    % M4: Active mirror load transistor delivering high incremental output impedance
    params.pmos = struct();
    params.pmos.Vth = params.Vth_p0;        % Threshold voltage (V) (negative for PMOS)
    params.pmos.Vth_mag = abs(params.Vth_p0); % Absolute threshold magnitude |Vth_p| (V)
    params.pmos.Kp = 312.5e-6;              % Transconductance parameter Kp = mu_p * Cox * (W/L) (A/V^2)
    params.pmos.lambda = 0.25;              % Channel length modulation parameter (1/V)
    params.pmos.W = 4.8e-6;                 % Channel width (m) (4.8 um, 3x NMOS width to match mobility)
    params.pmos.L = 1.0e-6;                 % Channel length (m) (1.0 um)
    params.pmos.mu_Cox = 65.1e-6;           % Process transconductance mu_p * Cox (A/V^2)
    params.pmos.rd = 1.0;                   % Ohmic drain contact resistance (Ohm)
    params.pmos.rs = 1.0;                   % Ohmic source contact resistance (Ohm)
    params.pmos.Cgs = 24.0e-15;             % Gate-to-source capacitance (F) (24 fF)
    params.pmos.Cgd = 5.0e-15;              % Gate-to-drain overlap capacitance (F) (5 fF)
    params.pmos.Cdb = 8.0e-15;              % Drain-to-bulk junction capacitance (F) (8 fF)

    %% 5. Theoretical Quiescent Operating Point Derivation
    params.Id_branch_nominal = params.Itail / 2; % Nominal branch drain current: 1.0 uA
    
    % NMOS overdrive voltage: Id = 0.5 * Kp * Vov^2 -> Vov = sqrt(2 * Id / Kp)
    params.Vov_n = sqrt(2 * params.Id_branch_nominal / params.nmos.Kp); % ~ 0.080 V (80 mV)
    params.Vgs_n = params.nmos.Vth + params.Vov_n;                      % ~ 0.300 V
    params.Vs_nominal = params.Vicm - params.Vgs_n;                     % Common-source node voltage ~ 0.100 V
    
    % Tail source compliance check:
    params.Vtail_actual = params.Vs_nominal - params.Vss;               % 0.100 V >= Vtail_compliance (0.10 V)
    
    % PMOS active load overdrive voltage:
    params.Vov_p = sqrt(2 * params.Id_branch_nominal / params.pmos.Kp); % ~ 0.080 V (80 mV)
    params.Vsg_p = params.pmos.Vth_mag + params.Vov_p;                  % ~ 0.330 V
    params.Vd1_nominal = params.Vdd - params.Vsg_p;                     % Node D1 (diode load drain/gate) ~ 0.470 V
    params.Vout_quiescent = params.Vd1_nominal;                         % Symmetrical quiescent output ~ 0.470 V

    % Transconductance and small-signal parameters:
    params.gm1 = sqrt(2 * params.nmos.Kp * params.Id_branch_nominal);   % gm = 25.0 uS
    params.gm3 = sqrt(2 * params.pmos.Kp * params.Id_branch_nominal);   % gm_load = 25.0 uS
    params.ro_n = 1 / (params.nmos.lambda * params.Id_branch_nominal);  % ro_n = 4.0 MOhm
    params.ro_p = 1 / (params.pmos.lambda * params.Id_branch_nominal);  % ro_p = 4.0 MOhm
    params.ro_out = (params.ro_n * params.ro_p) / (params.ro_n + params.ro_p); % ro1 = 2.0 MOhm
    
    % Voltage gains:
    params.Av_differential = params.gm1 * params.ro_out;                % Avd = +50.0 V/V (33.98 dB)
    params.Av_diff_dB = 20 * log10(params.Av_differential);
    params.Av_common_mode = -params.ro_out / (2 * params.Rtail);        % Avcm = -0.20 V/V (-13.98 dB)
    params.Av_cm_dB = 20 * log10(abs(params.Av_common_mode));
    params.CMRR = abs(params.Av_differential / params.Av_common_mode);  % CMRR = 250 (47.96 dB)
    params.CMRR_dB = 20 * log10(params.CMRR);

    %% 6. External Load and Testbench Interface
    params.CL = 0.5e-12;                    % Load capacitance (F) (0.5 pF, representing Miller input of Stage 2)
    params.RL = 10.0e6;                     % Load resistance (Ohm) (10 MOhm, input impedance of next stage)

    %% 7. Signal Test Stimuli
    % Mode A: DC Differential Sweep
    params.sweep_Vid_min = -0.015;          % -15 mV
    params.sweep_Vid_max = +0.015;          % +15 mV
    params.sweep_Vid_step = 0.0002;         % 0.2 mV steps

    % Mode B: Transient Small-Signal Sinusoid
    params.trans_Vid_peak = 0.002;          % 2.0 mV peak differential amplitude (4.0 mV pk-pk)
    params.trans_freq = 1000.0;             % 1 kHz test frequency
    params.trans_cycles = 5.0;              % 5 cycles
    params.trans_stop_time = params.trans_cycles / params.trans_freq; % 0.005 s (5 ms)

    % Mode C: Common-Mode Disturbance Rejection Test
    params.cm_test_amp = 0.020;             % 20 mV common-mode ripple
    params.cm_test_freq = 100.0;            % 100 Hz ripple frequency

    %% 8. Numerical Solver and Simulation Settings
    params.solver = 'ode23t';               % Stiff/DAE trapezoidal solver
    params.rel_tol = 1e-5;                  % Relative error tolerance
    params.abs_tol = 1e-6;                  % Absolute error tolerance
    params.max_step = 1e-6;                 % Maximum integration step (1 us)
    params.min_step = 1e-12;                % Minimum step size (1 ps)
    params.init_step = 1e-8;                % Initial step size (10 ns)

    %% 9. Export to MATLAB Workspace
    assignin('base', 'CMOSParams', params);
    assignin('base', 'params', params);

    fprintf('Parameters successfully loaded into base workspace variable "CMOSParams".\n');
    fprintf('  - VDD = %.2f V, VSS = %.2f V, VICM = %.2f V\n', params.Vdd, params.Vss, params.Vicm);
    fprintf('  - Itail = %.2f uA, gm1 = %.2f uS, Rout = %.2f MOhm\n', params.Itail*1e6, params.gm1*1e6, params.ro_out*1e-6);
    fprintf('  - Predicted Differential Gain Avd = %.2f V/V (%.2f dB)\n', params.Av_differential, params.Av_diff_dB);
    fprintf('  - Predicted CMRR = %.2f (%.2f dB)\n', params.CMRR, params.CMRR_dB);
    fprintf('=================================================================\n\n');
end
