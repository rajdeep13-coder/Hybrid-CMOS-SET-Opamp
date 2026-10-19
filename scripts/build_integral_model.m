%% build_integral_model.m
% Programmatically constructs the standalone Hybrid SET-CMOS Integral Model
% (Hybrid_OpAmp_Integral.slx) using Simulink APIs.

function build_integral_model()
    modelName = 'Hybrid_OpAmp_Integral';
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

    % Set Model Solver and Configuration
    set_param(modelName, 'Solver', 'ode23t');
    set_param(modelName, 'StopTime', '0.001');
    set_param(modelName, 'RelTol', '1e-5');
    set_param(modelName, 'AbsTol', '1e-6');
    set_param(modelName, 'SaveTime', 'on');
    set_param(modelName, 'TimeSaveName', 'tout');

    % Define Blocks to Add
    % 1. Input Sources & Selectors
    add_block('simulink/Sources/In1', [modelName '/Vin_ext'], 'Position', [40, 100, 70, 114]);
    add_block('simulink/Sources/Step', [modelName '/Test_Step'], ...
        'Position', [40, 150, 70, 170], 'Time', '0.0001', 'Before', '0', 'After', '0.01');
    add_block('simulink/Sources/Sine Wave', [modelName '/Test_Sine'], ...
        'Position', [40, 200, 70, 220], 'Amplitude', '0.005', 'Frequency', '2*pi*1000');
    add_block('simulink/Signal Routing/Manual Switch', [modelName '/Input_Switch'], ...
        'Position', [130, 150, 160, 185]);
    add_block('simulink/Signal Routing/Manual Switch', [modelName '/Source_Selector'], ...
        'Position', [210, 120, 240, 155]);

    % 2. Transconductance Stage (gm2)
    add_block('simulink/Math Operations/Gain', [modelName '/gm2_Driver'], ...
        'Position', [300, 125, 360, 155], 'Gain', 'OpAmpParams.gm2');

    % 3. Intermediate Summing Junction (KCL)
    add_block('simulink/Math Operations/Sum', [modelName '/KCL_Sum'], ...
        'Position', [410, 125, 435, 165], 'Inputs', '+--');

    % 4. Dominant Miller Integrator (1 / (Cc * s))
    add_block('simulink/Continuous/Integrator', [modelName '/Miller_Integrator'], ...
        'Position', [480, 125, 520, 165], ...
        'InitialCondition', 'OpAmpParams.Vicm', ...
        'LimitOutput', 'on', ...
        'UpperSaturationLimit', 'OpAmpParams.Vdd - 0.05', ...
        'LowerSaturationLimit', 'OpAmpParams.Vss + 0.05');
    
    add_block('simulink/Math Operations/Gain', [modelName '/Cc_Scaling'], ...
        'Position', [550, 130, 610, 160], 'Gain', '1 / OpAmpParams.Cc');

    % 5. Active Load Resistance (Finite ro2 feedback)
    add_block('simulink/Math Operations/Gain', [modelName '/ro2_Feedback'], ...
        'Position', [480, 220, 540, 250], 'Gain', '1 / OpAmpParams.ro2', 'Orientation', 'left');

    % 6. SET Dynamic Behavioural Current Block (Coulomb blockade effect)
    add_block('simulink/User-Defined Functions/MATLAB Function', [modelName '/SET_Active_Load'], ...
        'Position', [460, 290, 560, 340], 'Orientation', 'left');

    % Inject MATLAB Function code for SET dynamic active load
    setFunctionCode = sprintf([...
        'function I_set = SET_Active_Load(V_node, Vicm, Vth_set, rds_set)\n' ...
        '%% Evaluates incremental SET current around quiescent point Vicm\n' ...
        'delta_V = V_node - Vicm;\n' ...
        '%% SET Coulomb Blockade and active non-linear conductance\n' ...
        'if abs(delta_V) < Vth_set * 0.1\n' ...
        '    %% Inside tight Coulomb blockade zone\n' ...
        '    I_set = delta_V / (rds_set * 10.0);\n' ...
        'else\n' ...
        '    %% Beyond blockade threshold, normal dynamic resistance\n' ...
        '    I_set = delta_V / rds_set;\n' ...
        'end\n' ...
        'end\n']);
    
    try
        sf = sfroot;
        m = sf.find('Name', modelName, '-isa', 'Simulink.BlockDiagram');
        fBlock = m.find('Name', 'SET_Active_Load', '-isa', 'Stateflow.EMChart');
        if ~isempty(fBlock)
            fBlock.Script = setFunctionCode;
        end
    catch
        % Fallback if Stateflow API is unavailable in this edition
    end

    % 7. Output Ports & Scopes
    add_block('simulink/Sinks/Out1', [modelName '/Vout'], 'Position', [680, 135, 710, 150]);
    add_block('simulink/Sinks/Scope', [modelName '/Scope_Transient'], 'Position', [680, 75, 715, 110]);
    add_block('simulink/Sinks/To Workspace', [modelName '/Log_Vout'], ...
        'Position', [670, 200, 730, 220], 'VariableName', 'Vout_integral', 'SaveFormat', 'Structure With Time');
    add_block('simulink/Sinks/To Workspace', [modelName '/Log_Vin'], ...
        'Position', [300, 60, 360, 80], 'VariableName', 'Vin_integral', 'SaveFormat', 'Structure With Time');

    % 8. Connect Signal Lines
    add_line(modelName, 'Test_Step/1', 'Input_Switch/1');
    add_line(modelName, 'Test_Sine/1', 'Input_Switch/2');
    add_line(modelName, 'Vin_ext/1', 'Source_Selector/1');
    add_line(modelName, 'Input_Switch/1', 'Source_Selector/2');
    add_line(modelName, 'Source_Selector/1', 'gm2_Driver/1');
    add_line(modelName, 'Source_Selector/1', 'Log_Vin/1');
    
    add_line(modelName, 'gm2_Driver/1', 'KCL_Sum/1');
    add_line(modelName, 'KCL_Sum/1', 'Miller_Integrator/1');
    add_line(modelName, 'Miller_Integrator/1', 'Cc_Scaling/1');
    
    add_line(modelName, 'Cc_Scaling/1', 'Vout/1');
    add_line(modelName, 'Cc_Scaling/1', 'Scope_Transient/1');
    add_line(modelName, 'Cc_Scaling/1', 'Log_Vout/1');
    
    % Feedback lines
    add_line(modelName, 'Cc_Scaling/1', 'ro2_Feedback/1');
    add_line(modelName, 'ro2_Feedback/1', 'KCL_Sum/2');

    % Save system
    save_system(modelName, modelPath);
    fprintf('Successfully built and saved: %s\n', modelPath);
end
