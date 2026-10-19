%% build_differential_model.m
% Programmatically constructs the standalone CMOS Differential Stage Model
% (Hybrid_OpAmp_Differential.slx) using Simulink APIs.

function build_differential_model()
    modelName = 'Hybrid_OpAmp_Differential';
    fprintf('Building standalone model: %s.slx...\n', modelName);

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

    % 1. External Differential Input Ports
    add_block('simulink/Sources/In1', [modelName '/Vin_pos'], 'Position', [40, 80, 70, 95]);
    add_block('simulink/Sources/In1', [modelName '/Vin_neg'], 'Position', [40, 140, 70, 155]);

    % 2. Internal Test Signal Generators (Differential & Common Mode)
    add_block('simulink/Sources/Constant', [modelName '/DC_Bias_pos'], ...
        'Position', [40, 200, 70, 220], 'Value', 'OpAmpParams.Vicm');
    add_block('simulink/Sources/Sine Wave', [modelName '/Diff_Sine'], ...
        'Position', [40, 250, 70, 270], 'Amplitude', '0.002', 'Frequency', '2*pi*1000');
    add_block('simulink/Sources/Sine Wave', [modelName '/CM_Disturbance'], ...
        'Position', [40, 310, 70, 330], 'Amplitude', '0.020', 'Frequency', '2*pi*100');

    % Synthesize test Vin+ and Vin-
    add_block('simulink/Math Operations/Sum', [modelName '/Sum_Pos_Test'], ...
        'Position', [120, 220, 140, 250], 'Inputs', '+++');
    add_block('simulink/Math Operations/Gain', [modelName '/Invert_Diff'], ...
        'Position', [100, 280, 130, 300], 'Gain', '-1');
    add_block('simulink/Math Operations/Sum', [modelName '/Sum_Neg_Test'], ...
        'Position', [160, 280, 180, 310], 'Inputs', '+++');

    % Input selection switches
    add_block('simulink/Signal Routing/Manual Switch', [modelName '/Switch_Pos'], ...
        'Position', [220, 80, 250, 115]);
    add_block('simulink/Signal Routing/Manual Switch', [modelName '/Switch_Neg'], ...
        'Position', [220, 140, 250, 175]);

    % 3. Differential and Common-Mode Extraction
    add_block('simulink/Math Operations/Sum', [modelName '/Extract_Vid'], ...
        'Position', [310, 100, 330, 130], 'Inputs', '+-');
    add_block('simulink/Math Operations/Sum', [modelName '/Sum_Vicm'], ...
        'Position', [310, 160, 330, 190], 'Inputs', '++');
    add_block('simulink/Math Operations/Gain', [modelName '/Half_Gain'], ...
        'Position', [350, 165, 380, 185], 'Gain', '0.5');

    % 4. Gain Paths
    % Differential Path (Avd1 = gm1 * ro1)
    add_block('simulink/Math Operations/Gain', [modelName '/Diff_Gain_Avd1'], ...
        'Position', [420, 105, 480, 135], 'Gain', 'OpAmpParams.Av1_diff');
    
    % Common-Mode Path (Avcm1 = -ro1 / (2 * Rtail))
    add_block('simulink/Math Operations/Sum', [modelName '/CM_Deviation'], ...
        'Position', [410, 165, 430, 195], 'Inputs', '+-');
    add_block('simulink/Sources/Constant', [modelName '/Nominal_Vicm'], ...
        'Position', [350, 210, 380, 230], 'Value', 'OpAmpParams.Vicm');
    add_block('simulink/Math Operations/Gain', [modelName '/CM_Gain_Avcm1'], ...
        'Position', [450, 170, 510, 200], 'Gain', 'OpAmpParams.Av1_cm');

    % 5. Stage 1 Output Summing and Bandwidth Limiting
    add_block('simulink/Math Operations/Sum', [modelName '/Sum_Stage1'], ...
        'Position', [540, 120, 565, 160], 'Inputs', '+++');
    add_block('simulink/Sources/Constant', [modelName '/DC_Quiescent_Out'], ...
        'Position', [470, 70, 500, 90], 'Value', 'OpAmpParams.Vicm');

    % Output pole filtering
    add_block('simulink/Continuous/Transfer Fcn', [modelName '/Pole_Stage1'], ...
        'Position', [590, 125, 660, 165], ...
        'Numerator', '[1]', ...
        'Denominator', '[1/(2*pi*50e6) 1]');

    % Saturation Limiter
    add_block('simulink/Discontinuities/Saturation', [modelName '/Output_Limiter'], ...
        'Position', [690, 130, 720, 160], ...
        'UpperLimit', 'OpAmpParams.Vdd - 0.05', ...
        'LowerLimit', 'OpAmpParams.Vss + 0.05');

    % 6. Output Ports & Scopes
    add_block('simulink/Sinks/Out1', [modelName '/Vout_diff_stage'], 'Position', [770, 135, 800, 155]);
    add_block('simulink/Sinks/Scope', [modelName '/Scope_Diff'], 'Position', [770, 70, 800, 105]);
    add_block('simulink/Sinks/To Workspace', [modelName '/Log_Vout1'], ...
        'Position', [760, 200, 820, 220], 'VariableName', 'Vout_diff', 'SaveFormat', 'Structure With Time');
    add_block('simulink/Sinks/To Workspace', [modelName '/Log_Vid'], ...
        'Position', [420, 45, 480, 65], 'VariableName', 'Vid', 'SaveFormat', 'Structure With Time');

    % 7. Connections
    add_line(modelName, 'DC_Bias_pos/1', 'Sum_Pos_Test/1');
    add_line(modelName, 'Diff_Sine/1', 'Sum_Pos_Test/2');
    add_line(modelName, 'CM_Disturbance/1', 'Sum_Pos_Test/3');
    add_line(modelName, 'Diff_Sine/1', 'Invert_Diff/1');
    add_line(modelName, 'DC_Bias_pos/1', 'Sum_Neg_Test/1');
    add_line(modelName, 'Invert_Diff/1', 'Sum_Neg_Test/2');
    add_line(modelName, 'CM_Disturbance/1', 'Sum_Neg_Test/3');

    add_line(modelName, 'Vin_pos/1', 'Switch_Pos/1');
    add_line(modelName, 'Sum_Pos_Test/1', 'Switch_Pos/2');
    add_line(modelName, 'Vin_neg/1', 'Switch_Neg/1');
    add_line(modelName, 'Sum_Neg_Test/1', 'Switch_Neg/2');

    add_line(modelName, 'Switch_Pos/1', 'Extract_Vid/1');
    add_line(modelName, 'Switch_Neg/1', 'Extract_Vid/2');
    add_line(modelName, 'Switch_Pos/1', 'Sum_Vicm/1');
    add_line(modelName, 'Switch_Neg/1', 'Sum_Vicm/2');

    add_line(modelName, 'Extract_Vid/1', 'Diff_Gain_Avd1/1');
    add_line(modelName, 'Extract_Vid/1', 'Log_Vid/1');
    add_line(modelName, 'Sum_Vicm/1', 'Half_Gain/1');
    add_line(modelName, 'Half_Gain/1', 'CM_Deviation/1');
    add_line(modelName, 'Nominal_Vicm/1', 'CM_Deviation/2');
    add_line(modelName, 'CM_Deviation/1', 'CM_Gain_Avcm1/1');

    add_line(modelName, 'DC_Quiescent_Out/1', 'Sum_Stage1/1');
    add_line(modelName, 'Diff_Gain_Avd1/1', 'Sum_Stage1/2');
    add_line(modelName, 'CM_Gain_Avcm1/1', 'Sum_Stage1/3');
    add_line(modelName, 'Sum_Stage1/1', 'Pole_Stage1/1');
    add_line(modelName, 'Pole_Stage1/1', 'Output_Limiter/1');
    add_line(modelName, 'Output_Limiter/1', 'Vout_diff_stage/1');
    add_line(modelName, 'Output_Limiter/1', 'Scope_Diff/1');
    add_line(modelName, 'Output_Limiter/1', 'Log_Vout1/1');

    % Save system
    save_system(modelName, modelPath);
    fprintf('Successfully built and saved: %s\n', modelPath);
end
