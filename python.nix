{
  inputs,
  lib,
  pkgs,
  ...
}:

let

  python = pkgs.python3;

  workspace = inputs.uv2nix.lib.workspace.loadWorkspace {
    workspaceRoot = ./door_tracker;
  };

  overlay = workspace.mkPyprojectOverlay {
    sourcePreference = "wheel";
  };

  # hacks = pkgs.callPackage inputs.pyproject-nix.build.hacks { };
  pyprojectOverrides = _pypkgs: _prev: {
  };

  baseSet = pkgs.callPackage inputs.pyproject-nix.build.packages { inherit python; };
  pythonSet = baseSet.overrideScope (
    lib.composeManyExtensions [
      inputs.pyproject-build-systems.overlays.default
      overlay
      pyprojectOverrides
    ]
  );

  venv = pythonSet.mkVirtualEnv "rfid-tracker-env" workspace.deps.default;

in

venv
