%% check_environment.m
% Inspects and validates the host MATLAB and Simulink runtime environment.
% Checks installed toolboxes, licenses, batch-mode capability, and block libraries.

function envStatus = check_environment()
    fprintf('=================================================================\n');
    fprintf('  HYBRID CMOS-SET OP-AMP SIMULATION: ENVIRONMENT DIAGNOSTICS      \n');
    fprintf('=================================================================\n\n');

    envStatus = struct();
    envStatus.timestamp = datestr(now, 'yyyy-mm-dd HH:MM:SS');
    
    % 1. MATLAB Information
    v = ver('matlab');
    if ~isempty(v)
        envStatus.matlabAvailable = true;
        envStatus.matlabVersion = v.Version;
        envStatus.matlabRelease = v.Release;
        fprintf('[OK] MATLAB detected: Version %s (%s)\n', v.Version, v.Release);
    else
        envStatus.matlabAvailable = false;
        envStatus.matlabVersion = 'Unknown';
        envStatus.matlabRelease = 'Unknown';
        fprintf('[WARN] MATLAB core version could not be queried via ver().\n');
    end

    % 2. Simulink License and Installation
    hasSimulink = ~isempty(ver('simulink'));
    hasSimulinkLic = license('test', 'Simulink');
    envStatus.simulinkInstalled = hasSimulink;
    envStatus.simulinkLicensed = (hasSimulinkLic == 1);
    
    if hasSimulink && envStatus.simulinkLicensed
        fprintf('[OK] Simulink is installed and licensed.\n');
    elseif hasSimulink
        fprintf('[WARN] Simulink is installed but license test returned %d.\n', hasSimulinkLic);
    else
        fprintf('[FAIL] Simulink is NOT installed in this environment.\n');
    end

    % 3. Simscape & Simscape Electrical
    hasSimscape = ~isempty(ver('simscape'));
    hasSimscapeLic = license('test', 'Simscape');
    hasSimElectronics = ~isempty(ver('sps')) || ~isempty(ver('physmod'));
    
    envStatus.simscapeInstalled = hasSimscape;
    envStatus.simscapeLicensed = (hasSimscapeLic == 1);
    envStatus.simElectronicsInstalled = hasSimElectronics;

    fprintf('[INFO] Simscape: Installed=%d, Licensed=%d\n', hasSimscape, envStatus.simscapeLicensed);
    fprintf('[INFO] Simscape Electrical / Physmod: Installed=%d\n', hasSimElectronics);

    % 4. Block Library Accessibility Test
    envStatus.librariesAccessible = false;
    if hasSimulink
        try
            load_system('simulink');
            envStatus.librariesAccessible = true;
            fprintf('[OK] Core Simulink library successfully loaded into memory.\n');
        catch ME
            fprintf('[WARN] Core Simulink library load failed: %s\n', ME.message);
        end
    end

    % 5. Operational Mode Recommendation
    if envStatus.simulinkInstalled && envStatus.simulinkLicensed
        if envStatus.simscapeInstalled
            envStatus.recommendedMode = 'Simscape + Simulink Behavioural Hybrid';
        else
            envStatus.recommendedMode = 'Simulink Mathematical & State-Space Behavioural';
        end
    else
        envStatus.recommendedMode = 'Standalone Verification & Python Cross-Validation';
    end
    fprintf('\nRecommended Execution Mode: %s\n', envStatus.recommendedMode);
    fprintf('=================================================================\n\n');
end
