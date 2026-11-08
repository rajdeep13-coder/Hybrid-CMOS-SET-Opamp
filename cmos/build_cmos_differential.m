%% build_cmos_differential.m
% =========================================================================
% PROGRAMMATIC SIMULINK / SIMSCAPE ELECTRICAL BUILD SCRIPT
% =========================================================================
% Academic Project: Hybrid CMOS-SET Operational Amplifier
% Milestone: Standalone Transistor-Level CMOS Differential Input Stage
%
% This script programmatically constructs and wires the complete
% transistor-level CMOS differential amplifier in MATLAB/Simulink using
% official MathWorks APIs:
%   new_system, add_block, add_line, set_param, save_system.
%
% Key Wiring Rules Implemented:
%   - All semiconductor and passive circuit connections use Simscape
%     Physical Conserving Ports (LConn / RConn handles).
%   - M1, M2 NMOS differential pair sources tied at common-source Node S.
%   - M3 PMOS active load is diode-connected (Drain shorted to Gate at Node D1).
%   - M4 PMOS active load gate is tied to Node D1; Drain connects to Node Vout.
%   - Tail current source and Rtail connect between Node S and GND.
%   - VDD source connects between PMOS sources and GND.
%   - Output load (RL || CL) connects between Node Vout and GND.
%   - Input drivers synthesize Vin+ = VCM + Vid/2 and Vin- = VCM - Vid/2
%     via Simulink-PS converters to controlled physical voltage sources.
%   - Conserving-port connections are added using exact PortHandles to
%     ensure version-independent compatibility across MATLAB releases.
% =========================================================================

function build_cmos_differential(profile)
    if nargin < 1 || isempty(profile)
        profile = 'hybrid_synopsis_0v8';
    end

    modelName = 'CMOS_Differential_Stage';
    fprintf('=================================================================\n');
    fprintf('Building Transistor-Level Model: %s.slx (Profile: %s)\n', modelName, profile);
    fprintf('=================================================================\n');

    % 1. Load central parameters
    cmos_dir = fileparts(mfilename('fullpath'));
    run(fullfile(cmos_dir, 'cmos_parameters.m'));
    params = evalin('base', 'CMOSParams');

    % 2. Check MATLAB / Simulink / Simscape Environment
    hasMatlab = ~isempty(ver('matlab'));
    hasSimulink = ~isempty(ver('simulink'));
    hasSimscape = ~isempty(ver('simscape'));
    hasSimElectronics = ~isempty(ver('sps')) || ~isempty(ver('physmod'));

    fprintf('Environment Diagnostics:\n');
    fprintf('  - MATLAB Installed: %d\n', hasMatlab);
    fprintf('  - Simulink Installed: %d\n', hasSimulink);
    fprintf('  - Simscape Core Installed: %d\n', hasSimscape);
    fprintf('  - Simscape Electrical / Physmod: %d\n', hasSimElectronics);

    slxFile = fullfile(cmos_dir, [modelName '.slx']);

    if ~hasSimulink || ~hasSimscape
        fprintf('\n[STATUS: UNTESTED IN CURRENT ENVIRONMENT]\n');
        fprintf('MATLAB Simulink / Simscape is not active in this execution environment.\n');
        fprintf('To compile and simulate this physical network:\n');
        fprintf('  1. Launch MATLAB R2020b or later on a workstation with Simscape Electrical.\n');
        fprintf('  2. >> cd(''%s'')\n', cmos_dir);
        fprintf('  3. >> build_cmos_differential(''%s'')\n', profile);
        fprintf('  4. >> run_cmos_simulation(''%s'')\n', profile);
        fprintf('=================================================================\n');
        return;
    end

    % 3. Close system if already open in memory
    if bdIsLoaded(modelName)
        close_system(modelName, 0);
    end

    % 4. Create new system
    fprintf('Creating new Simulink model: %s...\n', modelName);
    new_system(modelName);
    open_system(modelName);

    % Configure solver parameters for non-linear stiff electrical DAEs
    set_param(modelName, 'Solver', params.solver);
    set_param(modelName, 'StopTime', sprintf('%.6f', params.trans_stop_time));
    set_param(modelName, 'RelTol', sprintf('%.1e', params.rel_tol));
    set_param(modelName, 'AbsTol', sprintf('%.1e', params.abs_tol));
    set_param(modelName, 'MaxStep', sprintf('%.1e', params.max_step));
    set_param(modelName, 'SaveTime', 'on');
    set_param(modelName, 'TimeSaveName', 'tout');

    %% 5. Add Input Signal Synthesis Blocks (Simulink Domain)
    % V_ICM Bias Constant (0.40 V)
    add_block('simulink/Sources/Constant', [modelName '/V_ICM_Bias'], ...
        'Position', [40, 60, 80, 80], 'Value', 'CMOSParams.Vicm');

    % Differential Sine Generator (Vid_peak / 2)
    add_block('simulink/Sources/Sine Wave', [modelName '/Vid_Sine_Source'], ...
        'Position', [40, 110, 80, 130], ...
        'Amplitude', 'CMOSParams.trans_Vid_peak / 2', ...
        'Frequency', '2*pi*CMOSParams.trans_freq');

    % Inverter for negative differential leg (-Vid / 2)
    add_block('simulink/Math Operations/Gain', [modelName '/Invert_Vid_Leg'], ...
        'Position', [110, 140, 140, 160], 'Gain', '-1');

    % Common-mode ripple disturbance (20 mV, 100 Hz)
    add_block('simulink/Sources/Sine Wave', [modelName '/Vcm_Disturbance'], ...
        'Position', [40, 180, 80, 200], ...
        'Amplitude', 'CMOSParams.cm_test_amp', ...
        'Frequency', '2*pi*CMOSParams.cm_test_freq');

    % Synthesize: Vin+ = Vicm + Vid/2 + Vcm_dist
    add_block('simulink/Math Operations/Sum', [modelName '/Sum_Vin_pos'], ...
        'Position', [180, 65, 205, 105], 'Inputs', '+++');

    % Synthesize: Vin- = Vicm - Vid/2 + Vcm_dist
    add_block('simulink/Math Operations/Sum', [modelName '/Sum_Vin_neg'], ...
        'Position', [180, 135, 205, 175], 'Inputs', '+++');

    % Differential extraction for verification: Vid = Vin+ - Vin-
    add_block('simulink/Math Operations/Sum', [modelName '/Extract_Vid'], ...
        'Position', [250, 110, 275, 140], 'Inputs', '+-');

    %% 6. Add Simscape Core Physical Blocks
    % Check available library root: Foundation Library (fl_lib) is standard across all releases
    mosfet_n_path = 'fl_lib/Electrical/Electrical Elements/N-Channel MOSFET';
    mosfet_p_path = 'fl_lib/Electrical/Electrical Elements/P-Channel MOSFET';

    % Simscape Environment & Rails
    add_block('nesl_utility/Solver Configuration', [modelName '/Solver_Config'], ...
        'Position', [330, 20, 375, 50]);
    add_block('fl_lib/Electrical/Electrical Elements/Electrical Reference', [modelName '/GND_Ref'], ...
        'Position', [340, 75, 365, 100]);
    add_block('fl_lib/Electrical/Electrical Sources/DC Voltage Source', [modelName '/VDD_Supply'], ...
        'Position', [430, 20, 470, 55], 'v0', 'CMOSParams.Vdd');

    % Input Drivers (Simulink-PS + Controlled Voltage Sources)
    add_block('nesl_utility/Simulink-PS Converter', [modelName '/PS_Vin_pos'], ...
        'Position', [280, 75, 310, 95]);
    add_block('fl_lib/Electrical/Electrical Sources/Controlled Voltage Source', [modelName '/Src_Vin_pos'], ...
        'Position', [340, 130, 380, 170]);

    add_block('nesl_utility/Simulink-PS Converter', [modelName '/PS_Vin_neg'], ...
        'Position', [280, 150, 310, 170]);
    add_block('fl_lib/Electrical/Electrical Sources/Controlled Voltage Source', [modelName '/Src_Vin_neg'], ...
        'Position', [340, 210, 380, 250]);

    % Transistors M1 and M2 (NMOS Differential Pair)
    add_block(mosfet_n_path, [modelName '/M1_NMOS_Pos'], 'Position', [520, 240, 560, 280], ...
        'vth', 'CMOSParams.nmos.Vth', 'kp', 'CMOSParams.nmos.Kp', 'lambda', 'CMOSParams.nmos.lambda', ...
        'rd', 'CMOSParams.nmos.rd', 'rs', 'CMOSParams.nmos.rs');
    add_block(mosfet_n_path, [modelName '/M2_NMOS_Neg'], 'Position', [670, 240, 710, 280], ...
        'vth', 'CMOSParams.nmos.Vth', 'kp', 'CMOSParams.nmos.Kp', 'lambda', 'CMOSParams.nmos.lambda', ...
        'rd', 'CMOSParams.nmos.rd', 'rs', 'CMOSParams.nmos.rs');

    % Transistors M3 and M4 (PMOS Active Current Mirror Load)
    add_block(mosfet_p_path, [modelName '/M3_PMOS_Ref'], 'Position', [520, 100, 560, 140], ...
        'vth', 'CMOSParams.pmos.Vth_mag', 'kp', 'CMOSParams.pmos.Kp', 'lambda', 'CMOSParams.pmos.lambda', ...
        'rd', 'CMOSParams.pmos.rd', 'rs', 'CMOSParams.pmos.rs');
    add_block(mosfet_p_path, [modelName '/M4_PMOS_Mirror'], 'Position', [670, 100, 710, 140], ...
        'vth', 'CMOSParams.pmos.Vth_mag', 'kp', 'CMOSParams.pmos.Kp', 'lambda', 'CMOSParams.pmos.lambda', ...
        'rd', 'CMOSParams.pmos.rd', 'rs', 'CMOSParams.pmos.rs');

    % Tail Current Source & Internal Resistance
    add_block('fl_lib/Electrical/Electrical Sources/DC Current Source', [modelName '/Tail_Source'], ...
        'Position', [590, 340, 630, 380], 'i0', 'CMOSParams.Itail');
    add_block('fl_lib/Electrical/Electrical Elements/Resistor', [modelName '/R_tail'], ...
        'Position', [670, 345, 710, 375], 'R', 'CMOSParams.Rtail');

    % Output Load (CL || RL)
    add_block('fl_lib/Electrical/Electrical Elements/Capacitor', [modelName '/CL_Load'], ...
        'Position', [780, 200, 820, 230], 'c', 'CMOSParams.CL');
    add_block('fl_lib/Electrical/Electrical Elements/Resistor', [modelName '/RL_Load'], ...
        'Position', [840, 200, 880, 230], 'R', 'CMOSParams.RL');

    % Physical Sensors
    add_block('fl_lib/Electrical/Electrical Sensors/Voltage Sensor', [modelName '/Sensor_Vout'], ...
        'Position', [900, 150, 940, 185]);
    add_block('fl_lib/Electrical/Electrical Sensors/Voltage Sensor', [modelName '/Sensor_Vs'], ...
        'Position', [520, 340, 560, 375]);
    add_block('fl_lib/Electrical/Electrical Sensors/Current Sensor', [modelName '/Sensor_Id1'], ...
        'Position', [520, 175, 560, 210]);
    add_block('fl_lib/Electrical/Electrical Sensors/Current Sensor', [modelName '/Sensor_Id2'], ...
        'Position', [670, 175, 710, 210]);

    % PS-Simulink Converters
    add_block('nesl_utility/PS-Simulink Converter', [modelName '/PS_Sim_Vout'], 'Position', [960, 155, 990, 175]);
    add_block('nesl_utility/PS-Simulink Converter', [modelName '/PS_Sim_Vs'], 'Position', [520, 400, 550, 420]);
    add_block('nesl_utility/PS-Simulink Converter', [modelName '/PS_Sim_Id1'], 'Position', [580, 180, 610, 200]);
    add_block('nesl_utility/PS-Simulink Converter', [modelName '/PS_Sim_Id2'], 'Position', [730, 180, 760, 200]);

    % Monitoring Scopes & Outports
    add_block('simulink/Sinks/Scope', [modelName '/Scope_Diff_IO'], 'Position', [1040, 100, 1075, 140], 'NumInputPorts', '4');
    add_block('simulink/Sinks/Scope', [modelName '/Scope_Branch_Currents'], 'Position', [1040, 180, 1075, 220], 'NumInputPorts', '2');
    add_block('simulink/Sinks/Out1', [modelName '/Vout'], 'Position', [1040, 150, 1070, 165]);
    add_block('simulink/Sinks/To Workspace', [modelName '/Log_Vout'], ...
        'Position', [1030, 60, 1090, 80], 'VariableName', 'sim_Vout', 'SaveFormat', 'Structure With Time');

    %% 7. Add Physical Conserving Connections via Port Handles
    fprintf('Connecting physical conserving ports...\n');
    connect_physical_ports(modelName);

    %% 8. Add Simulink Signal Connections
    fprintf('Connecting Simulink signal routing lines...\n');
    add_line(modelName, 'V_ICM_Bias/1', 'Sum_Vin_pos/1');
    add_line(modelName, 'V_ICM_Bias/1', 'Sum_Vin_neg/1');
    add_line(modelName, 'Vid_Sine_Source/1', 'Sum_Vin_pos/2');
    add_line(modelName, 'Vid_Sine_Source/1', 'Invert_Vid_Leg/1');
    add_line(modelName, 'Invert_Vid_Leg/1', 'Sum_Vin_neg/2');
    add_line(modelName, 'Vcm_Disturbance/1', 'Sum_Vin_pos/3');
    add_line(modelName, 'Vcm_Disturbance/1', 'Sum_Vin_neg/3');

    add_line(modelName, 'Sum_Vin_pos/1', 'PS_Vin_pos/1');
    add_line(modelName, 'Sum_Vin_neg/1', 'PS_Vin_neg/1');
    add_line(modelName, 'Sum_Vin_pos/1', 'Extract_Vid/1');
    add_line(modelName, 'Sum_Vin_neg/1', 'Extract_Vid/2');

    add_line(modelName, 'Sum_Vin_pos/1', 'Scope_Diff_IO/1');
    add_line(modelName, 'Sum_Vin_neg/1', 'Scope_Diff_IO/2');
    add_line(modelName, 'Extract_Vid/1', 'Scope_Diff_IO/3');
    add_line(modelName, 'PS_Sim_Vout/1', 'Scope_Diff_IO/4');

    add_line(modelName, 'PS_Sim_Vout/1', 'Vout/1');
    add_line(modelName, 'PS_Sim_Vout/1', 'Log_Vout/1');

    add_line(modelName, 'PS_Sim_Id1/1', 'Scope_Branch_Currents/1');
    add_line(modelName, 'PS_Sim_Id2/1', 'Scope_Branch_Currents/2');

    % 9. Save diagram
    save_system(modelName, slxFile);
    fprintf('[OK] Transistor-level model successfully constructed and saved to:\n  %s\n', slxFile);
    fprintf('=================================================================\n\n');
end

%% Helper Function: Connect Physical Conserving Ports Using Handles
function connect_physical_ports(sys)
    % Helper to retrieve port handle safely
    get_h = @(blk, ptype, idx) get_sub_port(sys, blk, ptype, idx);

    % Solver Configuration to GND
    safe_add_line(sys, get_h('Solver_Config', 'RConn', 1), get_h('GND_Ref', 'LConn', 1));

    % VDD Negative terminal to GND
    safe_add_line(sys, get_h('VDD_Supply', 'RConn', 1), get_h('GND_Ref', 'LConn', 1));

    % PMOS Sources to VDD Positive terminal
    safe_add_line(sys, get_h('VDD_Supply', 'LConn', 1), get_h('M3_PMOS_Ref', 'LConn', 1));
    safe_add_line(sys, get_h('VDD_Supply', 'LConn', 1), get_h('M4_PMOS_Mirror', 'LConn', 1));

    % Node D1: M3 Drain connects to M3 Gate (Diode connection)
    safe_add_line(sys, get_h('M3_PMOS_Ref', 'RConn', 1), get_h('M3_PMOS_Ref', 'LConn', 2));

    % Node D1: M3 Gate connects to M4 Gate (Current Mirror connection)
    safe_add_line(sys, get_h('M3_PMOS_Ref', 'LConn', 2), get_h('M4_PMOS_Mirror', 'LConn', 2));

    % M1 Drain Branch: M3 Drain connects to Sensor_Id1(+)
    safe_add_line(sys, get_h('M3_PMOS_Ref', 'RConn', 1), get_h('Sensor_Id1', 'LConn', 1));

    % Sensor_Id1(-) connects to M1 Drain
    safe_add_line(sys, get_h('Sensor_Id1', 'RConn', 1), get_h('M1_NMOS_Pos', 'LConn', 1));

    % M2 Drain / Output Node Vout: M4 Drain connects to Sensor_Id2(+)
    safe_add_line(sys, get_h('M4_PMOS_Mirror', 'RConn', 1), get_h('Sensor_Id2', 'LConn', 1));

    % Sensor_Id2(-) connects to M2 Drain
    safe_add_line(sys, get_h('Sensor_Id2', 'RConn', 1), get_h('M2_NMOS_Neg', 'LConn', 1));

    % Common-Source Node S: M1 Source to M2 Source
    safe_add_line(sys, get_h('M1_NMOS_Pos', 'RConn', 1), get_h('M2_NMOS_Neg', 'RConn', 1));

    % Node S to Tail Current Source(+) and Rtail(1)
    safe_add_line(sys, get_h('M1_NMOS_Pos', 'RConn', 1), get_h('Tail_Source', 'LConn', 1));
    safe_add_line(sys, get_h('M1_NMOS_Pos', 'RConn', 1), get_h('R_tail', 'LConn', 1));

    % Tail Source(-) and Rtail(2) to GND
    safe_add_line(sys, get_h('Tail_Source', 'RConn', 1), get_h('GND_Ref', 'LConn', 1));
    safe_add_line(sys, get_h('R_tail', 'RConn', 1), get_h('GND_Ref', 'LConn', 1));

    % Node Vout to Load Resistor RL and Load Capacitor CL
    safe_add_line(sys, get_h('M4_PMOS_Mirror', 'RConn', 1), get_h('RL_Load', 'LConn', 1));
    safe_add_line(sys, get_h('M4_PMOS_Mirror', 'RConn', 1), get_h('CL_Load', 'LConn', 1));
    safe_add_line(sys, get_h('RL_Load', 'RConn', 1), get_h('GND_Ref', 'LConn', 1));
    safe_add_line(sys, get_h('CL_Load', 'RConn', 1), get_h('GND_Ref', 'LConn', 1));

    % Voltage Sensors
    safe_add_line(sys, get_h('Sensor_Vout', 'LConn', 1), get_h('M4_PMOS_Mirror', 'RConn', 1));
    safe_add_line(sys, get_h('Sensor_Vout', 'RConn', 1), get_h('GND_Ref', 'LConn', 1));

    safe_add_line(sys, get_h('Sensor_Vs', 'LConn', 1), get_h('M1_NMOS_Pos', 'RConn', 1));
    safe_add_line(sys, get_h('Sensor_Vs', 'RConn', 1), get_h('GND_Ref', 'LConn', 1));

    % Input Drivers: PS converters to Controlled Sources
    safe_add_line(sys, get_h('PS_Vin_pos', 'RConn', 1), get_h('Src_Vin_pos', 'LConn', 1));
    safe_add_line(sys, get_h('PS_Vin_neg', 'RConn', 1), get_h('Src_Vin_neg', 'LConn', 1));

    % Controlled Sources to M1 Gate and M2 Gate
    safe_add_line(sys, get_h('Src_Vin_pos', 'RConn', 1), get_h('M1_NMOS_Pos', 'LConn', 2));
    safe_add_line(sys, get_h('Src_Vin_pos', 'RConn', 2), get_h('GND_Ref', 'LConn', 1));

    safe_add_line(sys, get_h('Src_Vin_neg', 'RConn', 1), get_h('M2_NMOS_Neg', 'LConn', 2));
    safe_add_line(sys, get_h('Src_Vin_neg', 'RConn', 2), get_h('GND_Ref', 'LConn', 1));

    % Sensor outputs to PS-Simulink converters
    safe_add_line(sys, get_h('Sensor_Vout', 'RConn', 2), get_h('PS_Sim_Vout', 'LConn', 1));
    safe_add_line(sys, get_h('Sensor_Vs', 'RConn', 2), get_h('PS_Sim_Vs', 'LConn', 1));
    safe_add_line(sys, get_h('Sensor_Id1', 'RConn', 2), get_h('PS_Sim_Id1', 'LConn', 1));
    safe_add_line(sys, get_h('Sensor_Id2', 'RConn', 2), get_h('PS_Sim_Id2', 'LConn', 1));
end

function p = get_sub_port(sys, blk, ptype, idx)
    ph = get_param([sys '/' blk], 'PortHandles');
    if strcmpi(ptype, 'LConn')
        p = ph.LConn(idx);
    elseif strcmpi(ptype, 'RConn')
        p = ph.RConn(idx);
    elseif strcmpi(ptype, 'Inport')
        p = ph.Inport(idx);
    else
        p = ph.Outport(idx);
    end
end

function safe_add_line(sys, p1, p2)
    try
        add_line(sys, p1, p2, 'autorouting', 'on');
    catch ME
        % Ignore duplicate line errors if already connected
        if ~contains(ME.identifier, 'DuplicateLine')
            fprintf('[WARN] Connection error between ports: %s\n', ME.message);
        end
    end
end
