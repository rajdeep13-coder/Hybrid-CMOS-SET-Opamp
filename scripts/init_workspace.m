%% init_workspace.m
% Initializes the MATLAB/Simulink workspace for Hybrid CMOS-SET Op-Amp simulation.

fprintf('Initializing Hybrid CMOS-SET Op-Amp project workspace...\n');

% Identify project root directory
projectRoot = fileparts(fileparts(mfilename('fullpath')));

% Add relevant project folders to MATLAB search path
addpath(fullfile(projectRoot, 'simulink', 'models'));
addpath(fullfile(projectRoot, 'simulink', 'data'));
addpath(fullfile(projectRoot, 'simulink', 'testbenches'));
addpath(fullfile(projectRoot, 'scripts'));

% Load default parameter file if present
paramFile = fullfile(projectRoot, 'simulink', 'data', 'set_parameters.mat');
if exist(paramFile, 'file') == 2
    try
        load(paramFile);
        fprintf('Loaded parameters from: %s\n', paramFile);
    catch ME
        warning('Failed to load %s: %s', paramFile, ME.message);
    end
else
    fprintf('Note: set_parameters.mat not found. Initializing default SET parameter structure.\n');
    % Example default Single-Electron Transistor parameters
    SET_Params.C1 = 1e-18;       % Junction 1 capacitance (F)
    SET_Params.C2 = 1e-18;       % Junction 2 capacitance (F)
    SET_Params.Cg = 2e-18;       % Gate capacitance (F)
    SET_Params.R1 = 1e5;         % Junction 1 tunnel resistance (Ohm)
    SET_Params.R2 = 1e5;         % Junction 2 tunnel resistance (Ohm)
    SET_Params.Temp = 4.2;       % Temperature in Kelvin
    assignin('base', 'SET_Params', SET_Params);
end

fprintf('Workspace initialization complete.\n');
