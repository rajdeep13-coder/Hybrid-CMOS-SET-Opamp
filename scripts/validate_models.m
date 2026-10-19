%% validate_models.m
% Automates model compilation checks, structural linting, and metric validation
% for all three Hybrid CMOS-SET Op-Amp Simulink models.

function testSummary = validate_models()
    fprintf('=================================================================\n');
    fprintf('  HYBRID CMOS-SET OP-AMP SIMULINK MODEL VALIDATION SUITE          \n');
    fprintf('=================================================================\n\n');

    testSummary = struct();
    testSummary.timestamp = datestr(now, 'yyyy-mm-dd HH:MM:SS');
    testSummary.tests = {};

    % Ensure parameters are loaded
    if ~evalin('base', 'exist(''OpAmpParams'', ''var'')')
        derive_or_configure_parameters('room_temp');
    end
    params = evalin('base', 'OpAmpParams');

    models = {'Hybrid_OpAmp_Integral', 'Hybrid_OpAmp_Differential', 'Hybrid_OpAmp_Full'};
    projectRoot = fileparts(fileparts(mfilename('fullpath')));
    modelsDir = fullfile(projectRoot, 'models');
    addpath(modelsDir);

    hasSimulink = ~isempty(ver('simulink')) && license('test', 'Simulink');

    for i = 1:length(models)
        mName = models{i};
        filePath = fullfile(modelsDir, [mName '.slx']);
        fprintf('Validating Model %d/3: %s\n', i, mName);

        % Test 1: File Existence
        if exist(filePath, 'file') == 2
            fprintf('  [PASS] File exists on disk: %s\n', filePath);
            record_test(mName, 'File Existence', 'PASS', 'File exists');
        else
            fprintf('  [FAIL] File missing: %s\n', filePath);
            record_test(mName, 'File Existence', 'FAIL', 'File not found');
            continue;
        end

        % Test 2: Model Compilation / Update Check
        if hasSimulink
            try
                load_system(mName);
                set_param(mName, 'SimulationCommand', 'update');
                fprintf('  [PASS] Simulink compilation and update successful.\n');
                record_test(mName, 'Model Compilation', 'PASS', 'Model compiles without errors');
                close_system(mName, 0);
            catch ME
                fprintf('  [FAIL] Model update error: %s\n', ME.message);
                record_test(mName, 'Model Compilation', 'FAIL', ME.message);
            end
        else
            fprintf('  [SKIP] Model compile check skipped (Simulink not available in host env).\n');
            record_test(mName, 'Model Compilation', 'SKIPPED', 'Host lacks Simulink license');
        end
    end

    % Test 3: Mathematical Metric Validation Against Specifications
    fprintf('\nExecuting Analytical Metric Validation:\n');
    
    % Metric 1: Open-Loop Gain
    gain_pass = params.A0_dB >= 60.0;
    fprintf('  [%s] DC Open-Loop Gain: %.2f dB (Target: >= 60 dB)\n', ...
        pass_str(gain_pass), params.A0_dB);
    record_test('Full Model', 'DC Open-Loop Gain Target', pass_str(gain_pass), sprintf('%.2f dB', params.A0_dB));

    % Metric 2: Gain-Bandwidth Product
    gbw_pass = (params.GBW_Hz / 1e6) >= 5.0;
    fprintf('  [%s] Gain-Bandwidth Product: %.2f MHz (Target: >= 5 MHz)\n', ...
        pass_str(gbw_pass), params.GBW_Hz / 1e6);
    record_test('Full Model', 'GBW Target', pass_str(gbw_pass), sprintf('%.2f MHz', params.GBW_Hz / 1e6));

    % Metric 3: Power Consumption
    power_pass = params.Pdiss_est_uW <= 10.0;
    fprintf('  [%s] Power Dissipation: %.2f uW (Target: <= 10 uW)\n', ...
        pass_str(power_pass), params.Pdiss_est_uW);
    record_test('Full Model', 'Power Consumption Target', pass_str(power_pass), sprintf('%.2f uW', params.Pdiss_est_uW));

    % Metric 4: Stage 1 CMRR
    cmrr_pass = 20 * log10(params.CMRR1) >= 45.0;
    fprintf('  [%s] Stage 1 CMRR: %.2f dB (Target: >= 45 dB)\n', ...
        pass_str(cmrr_pass), 20 * log10(params.CMRR1));
    record_test('Differential Model', 'CMRR Target', pass_str(cmrr_pass), sprintf('%.2f dB', 20 * log10(params.CMRR1)));

    % Metric 5: Coulomb Blockade Room-Temp Criterion
    coulomb_pass = params.Ec_to_kBT_ratio >= 5.0;
    fprintf('  [%s] Room-Temp Coulomb Blockade Ratio Ec/kBT: %.2f (Target: >= 5.0)\n', ...
        pass_str(coulomb_pass), params.Ec_to_kBT_ratio);
    record_test('Integral Model', 'Coulomb Energy Ratio', pass_str(coulomb_pass), sprintf('%.2f', params.Ec_to_kBT_ratio));

    fprintf('\nValidation suite finished.\n');
    fprintf('=================================================================\n');

    function s = pass_str(b)
        if b, s = 'PASS'; else, s = 'FAIL'; end
    end

    function record_test(comp, tName, stat, detail)
        tEntry = struct('Component', comp, 'TestName', tName, 'Status', stat, 'Detail', detail);
        testSummary.tests{end+1} = tEntry;
    end
end
