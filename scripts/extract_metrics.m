%% extract_metrics.m
% Extracts key operational amplifier performance metrics from simulation outputs.
% Metrics: Open-Loop Gain (Adc), Gain-Bandwidth Product (GBW), Phase Margin (PM),
% Slew Rate (SR), and Power Dissipation.

function metrics = extract_metrics(simOut)
    % Initialize output struct
    metrics = struct();
    
    if nargin < 1
        % If no simulation object provided, inspect workspace
        if evalin('base', 'exist(''out'', ''var'')')
            simOut = evalin('base', 'out');
        else
            fprintf('No simulation output provided or found in base workspace.\n');
            return;
        end
    end
    
    fprintf('Extracting Op-Amp metrics...\n');
    
    % Example extraction logic for frequency/transient response signals
    % Users can customize signal names based on testbench logging
    try
        % Placeholder extraction template
        metrics.Adc_dB = NaN;      % DC Gain in dB
        metrics.GBW_Hz = NaN;      % Gain Bandwidth Product in Hz
        metrics.PhaseMargin_deg = NaN; % Phase Margin in degrees
        metrics.SlewRate_V_us = NaN;   % Slew rate in V/us
        metrics.Power_uW = NaN;        % Power dissipation in uW
        
        fprintf('Metric extraction completed.\n');
    catch ME
        warning('Error during metric extraction: %s', ME.message);
    end
end
