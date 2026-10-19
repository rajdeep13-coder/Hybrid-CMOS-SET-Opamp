%% run_all_simulations.m
% Executes simulation testbenches for all three Hybrid CMOS-SET Op-Amp models:
% 1. Standalone Integral Section (Hybrid_OpAmp_Integral)
% 2. Standalone Differential Stage (Hybrid_OpAmp_Differential)
% 3. Complete Hybrid CMOS-SET Op-Amp (Hybrid_OpAmp_Full)

function simResults = run_all_simulations()
    fprintf('=================================================================\n');
    fprintf('  RUNNING HYBRID CMOS-SET OP-AMP SIMULATION SUITE                \n');
    fprintf('=================================================================\n\n');

    % Check environment
    env = check_environment();
    if ~env.simulinkInstalled || ~env.simulinkLicensed
        warning('Simulink is not licensed or installed. Simulation in MATLAB cannot proceed.');
        simResults = struct('status', 'skipped_no_simulink');
        return;
    end

    % Configure and load parameters
    params = derive_or_configure_parameters('room_temp');
    assignin('base', 'OpAmpParams', params);

    projectRoot = fileparts(fileparts(mfilename('fullpath')));
    modelsDir = fullfile(projectRoot, 'models');
    addpath(modelsDir);

    simResults = struct();
    models = {'Hybrid_OpAmp_Integral', 'Hybrid_OpAmp_Differential', 'Hybrid_OpAmp_Full'};

    for i = 1:length(models)
        mName = models{i};
        fprintf('Simulating model: %s...\n', mName);
        try
            load_system(mName);
            % Run simulation
            simOut = sim(mName, 'ReturnWorkspaceOutputs', 'on');
            simResults.(mName).simOut = simOut;
            simResults.(mName).status = 'SUCCESS';
            fprintf('[OK] Simulation completed for %s.\n', mName);
        catch ME
            simResults.(mName).status = 'FAILED';
            simResults.(mName).error = ME.message;
            fprintf('[FAIL] Simulation failed for %s: %s\n', mName, ME.message);
        end
    end

    % Save results
    resultsDir = fullfile(projectRoot, 'results');
    if ~exist(resultsDir, 'dir')
        mkdir(resultsDir);
    end
    save(fullfile(resultsDir, 'simulation_data.mat'), 'simResults');
    fprintf('\nAll model simulation runs processed. Results saved to results/simulation_data.mat\n');
end
