%% build_full_model.m
% Programmatically constructs the complete Hybrid CMOS-SET Operational Amplifier
% (Hybrid_OpAmp_Full.slx) integrating Differential, SET-CMOS Integrating,
% and Buffer stages using Simulink APIs.

function build_full_model()
    modelName = 'Hybrid_OpAmp_Full';
    fprintf('Building complete model: %s.slx...\n', modelName);

    % Ensure parameters are loaded in base workspace
    if ~evalin('base', 'exist(''OpAmpParams'', ''var'')')
        derive_or_configure_parameters('room_temp');
    end

    projectRoot = fileparts(fileparts(mfilename('fullpath')));
    modelsDir = fullfile(projectRoot, 'models');
    if ~exist(modelsDir, 'dir')
        mkdir(modelsDir);
    end
    modelPath = fullfile(modelsDir, [modelName '.slx']);

    % Close model if already open
    if bdIsLoaded(modelName)
        close_system(modelName, 0);
    end

    % Create new Simulink system
    new_system(modelName);
    open_system(modelName);

    % Solver and Simulation Settings
    set_param(modelName, 'Solver', 'ode23t');
    set_param(modelName, 'StopTime', '0.002');
    set_param(modelName, 'RelTol', '1e-5');
    set_param(modelName, 'AbsTol', '1e-6');
    set_param(modelName, 'SaveTime', 'on');
    set_param(modelName, 'TimeSaveName', 'tout');

    % 1. Input Signal Selection (Open-Loop vs Closed-Loop Unity Gain)
    add_block('simulink/Sources/In1', [modelName '/Vin_pos_ext'], 'Position', [30, 80, 60, 95]);
    add_block('simulink/Sources/In1', [modelName '/Vin_neg_ext'], 'Position', [30, 140, 60, 155]);

    % Internal Test Sources
    add_block('simulink/Sources/Constant', [modelName '/DC_Bias'], ...
        'Position', [30, 200, 60, 220], 'Value', 'OpAmpParams.Vicm');
    add_block('simulink/Sources/Step', [modelName '/Test_Step'], ...
        'Position', [30, 240, 60, 260], 'Time', '0.0002', 'Before', '0', 'After', '0.05');
    add_block('simulink/Math Operations/Sum', [modelName '/Sum_Pos_In'], ...
        'Position', [90, 210, 110, 240], 'Inputs', '++');

    % Loop Switch (Closed-loop unity gain buffer vs open-loop test)
    add_block('simulink/Signal Routing/Manual Switch', [modelName '/Mode_Switch_Pos'], ...
        'Position', [150, 80, 180, 115]);
    add_block('simulink/Signal Routing/Manual Switch', [modelName '/Closed_Loop_Switch'], ...
        'Position', [150, 140, 180, 175]);

    % 2. STAGE 1: CMOS Differential Input Subsystem
    add_block('simulink/Math Operations/Sum', [modelName '/Vid_Calc'], ...
        'Position', [220, 100, 240, 130], 'Inputs', '+-');
    add_block('simulink/Math Operations/Gain', [modelName '/gm1_Transconductance'], ...
        'Position', [270, 105, 330, 135], 'Gain', 'OpAmpParams.gm1');
    add_block('simulink/Math Operations/Gain', [modelName '/ro1_Output_Resist'], ...
        'Position', [360, 105, 410, 135], 'Gain', 'OpAmpParams.ro1');

    % 3. STAGE 2: Hybrid SET-CMOS Integrating / Gain Subsystem
    % Summing node for Miller integration
    add_block('simulink/Math Operations/Sum', [modelName '/KCL_Stage2'], ...
        'Position', [450, 110, 470, 150], 'Inputs', '+--');
    add_block('simulink/Math Operations/Gain', [modelName '/gm2_Stage2'], ...
        'Position', [420, 180, 460, 205], 'Gain', 'OpAmpParams.gm2', 'Orientation', 'up');

    % Miller Integrator (1 / (Cc * s))
    add_block('simulink/Continuous/Integrator', [modelName '/Miller_Integrator'], ...
        'Position', [510, 120, 545, 150], ...
        'InitialCondition', 'OpAmpParams.Vicm', ...
        'LimitOutput', 'on', ...
        'UpperSaturationLimit', 'OpAmpParams.Vdd - 0.05', ...
        'LowerSaturationLimit', 'OpAmpParams.Vss + 0.05');

    add_block('simulink/Math Operations/Gain', [modelName '/Cc_Inv'], ...
        'Position', [570, 125, 620, 145], 'Gain', '1 / OpAmpParams.Cc');

    % Feedback conductances (ro2 & SET active load)
    add_block('simulink/Math Operations/Gain', [modelName '/go2_Feedback'], ...
        'Position', [510, 180, 560, 200], 'Gain', '1 / OpAmpParams.ro2', 'Orientation', 'left');

    % 4. STAGE 3: CMOS Output Buffer Subsystem
    add_block('simulink/Math Operations/Gain', [modelName '/Buffer_Gain'], ...
        'Position', [660, 125, 710, 145], 'Gain', 'OpAmpParams.Av3');
    add_block('simulink/Discontinuities/Saturation', [modelName '/Buffer_Limiter'], ...
        'Position', [730, 120, 760, 150], ...
        'UpperLimit', 'OpAmpParams.Vdd - 0.05', ...
        'LowerLimit', 'OpAmpParams.Vss + 0.05');

    % 5. Power Dissipation Calculation
    add_block('simulink/Sources/Constant', [modelName '/Static_Power_uW'], ...
        'Position', [660, 230, 720, 250], 'Value', 'OpAmpParams.Pdiss_est_uW');

    % 6. Output Ports & Scopes
    add_block('simulink/Sinks/Out1', [modelName '/Vout'], 'Position', [830, 125, 860, 145]);
    add_block('simulink/Sinks/Out1', [modelName '/Power_uW'], 'Position', [830, 230, 860, 250]);
    add_block('simulink/Sinks/Scope', [modelName '/Scope_Full'], 'Position', [830, 65, 865, 100]);
    add_block('simulink/Sinks/To Workspace', [modelName '/Log_Vout_Full'], ...
        'Position', [810, 175, 870, 195], 'VariableName', 'Vout_full', 'SaveFormat', 'Structure With Time');
    add_block('simulink/Sinks/To Workspace', [modelName '/Log_Vin_Full'], ...
        'Position', [220, 45, 280, 65], 'VariableName', 'Vin_full', 'SaveFormat', 'Structure With Time');

    % 7. Signal Routing & Connections
    add_line(modelName, 'DC_Bias/1', 'Sum_Pos_In/1');
    add_line(modelName, 'Test_Step/1', 'Sum_Pos_In/2');
    add_line(modelName, 'Vin_pos_ext/1', 'Mode_Switch_Pos/1');
    add_line(modelName, 'Sum_Pos_In/1', 'Mode_Switch_Pos/2');

    add_line(modelName, 'Mode_Switch_Pos/1', 'Vid_Calc/1');
    add_line(modelName, 'Mode_Switch_Pos/1', 'Log_Vin_Full/1');

    add_line(modelName, 'Vin_neg_ext/1', 'Closed_Loop_Switch/1');
    % Feedback from output for closed-loop buffer:
    add_line(modelName, 'Buffer_Limiter/1', 'Closed_Loop_Switch/2');
    add_line(modelName, 'Closed_Loop_Switch/1', 'Vid_Calc/2');

    add_line(modelName, 'Vid_Calc/1', 'gm1_Transconductance/1');
    add_line(modelName, 'gm1_Transconductance/1', 'ro1_Output_Resist/1');
    add_line(modelName, 'ro1_Output_Resist/1', 'KCL_Stage2/1');

    add_line(modelName, 'KCL_Stage2/1', 'Miller_Integrator/1');
    add_line(modelName, 'Miller_Integrator/1', 'Cc_Inv/1');
    add_line(modelName, 'Cc_Inv/1', 'Buffer_Gain/1');

    % Integrator inner feedback
    add_line(modelName, 'Cc_Inv/1', 'go2_Feedback/1');
    add_line(modelName, 'go2_Feedback/1', 'KCL_Stage2/2');

    % Buffer to outputs
    add_line(modelName, 'Buffer_Gain/1', 'Buffer_Limiter/1');
    add_line(modelName, 'Buffer_Limiter/1', 'Vout/1');
    add_line(modelName, 'Buffer_Limiter/1', 'Scope_Full/1');
    add_line(modelName, 'Buffer_Limiter/1', 'Log_Vout_Full/1');

    add_line(modelName, 'Static_Power_uW/1', 'Power_uW/1');

    % Save system
    save_system(modelName, modelPath);
    fprintf('Successfully built and saved: %s\n', modelPath);
end
