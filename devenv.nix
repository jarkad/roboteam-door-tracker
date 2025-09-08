{
  config,
  lib,
  pkgs,
  ...
}@args:

let
  venv = import ./python.nix args;
in

{

  ## Scripts

  scripts.django.exec = ''
    cd $DEVENV_ROOT/door_tracker
    ./manage.py "$@"
  '';

  scripts.dev.exec = ''
    django migrate &&
    django runserver "$@"
  '';

  scripts.makemigrations.exec = ''
    django makemigrations "$@"
  '';

  scripts.migrate.exec = ''
    django migrate "$@"
  '';

  scripts.init.exec = ''
    django migrate &&
    django createsuperuser "$@"
  '';

  scripts.docker-login.exec = ''
    skopeo login docker.io
  '';

  ## Languages

  languages.python = {
    enable = true;
    uv.enable = true;
    uv.sync.enable = true;
    directory = "door_tracker";
  };

  enterShell = ''
    export PATH="$UV_PROJECT_ENVIRONMENT/bin''${PATH+:}$PATH"
  '';

  ## Devcontainer

  packages = [
    pkgs.git
    pkgs.skopeo
  ];

  ## Tests

  tasks."django:test" = {
    exec = "django test";
    before = [ "devenv:enterTest" ];
  };

  ## Packages

  outputs.admin = pkgs.writeShellApplication {
    name = "admin";
    runtimeInputs = [ venv ];
    text = ''
      DJANGO_SETTINGS_MODULE=door_tracker.settings django-admin "$@"
    '';
  };

  outputs.static = pkgs.stdenv.mkDerivation {
    name = "static";
    src = ./door_tracker;

    dontConfigure = true;
    dontBuild = true;

    nativeBuildInputs = [ config.outputs.admin ];

    installPhase = ''
      DJANGO_STATIC_ROOT=$out admin collectstatic --no-input
    '';
  };

  outputs.serve = pkgs.writeShellApplication {
    name = "serve";
    runtimeInputs = [
      config.outputs.admin
      venv
    ];
    runtimeEnv.DJANGO_STATIC_ROOT = config.outputs.static;
    text = ''
      admin migrate
      daphne -b 0.0.0.0 door_tracker.asgi:application
    '';
  };

  outputs.init = pkgs.writeShellApplication {
    name = "init";
    runtimeInputs = [ config.outputs.admin ];
    text = ''
      admin migrate
      admin createsuperuser
    '';
  };

  ## Containers

  containers.serve = {
    name = "rfid-tracker-serve";
    startupCommand = lib.getExe config.outputs.serve;
    copyToRoot = [
      config.outputs.admin
      config.outputs.init
    ];
    maxLayers = 42;
  };

  ## Config files

  files."ruff.toml".toml = {
    line-length = 80;
    format = {
      docstring-code-format = true;
      quote-style = "single";
    };
    lint.pycodestyle = {
      max-line-length = 100;
    };
  };

  files.".vscode/tasks.json".json = {
    # See https://go.microsoft.com/fwlink/?LinkId=733558
    # for the documentation about the tasks.json format
    version = "2.0.0";
    tasks =
      # scripts
      lib.mapAttrsToList (
        name: _:
        {
          label = "script: ${name}";
          type = "shell";
          command = name;
          group = "build";
        }
        // lib.optionalAttrs (name == "dev") {
          group.kind = "build";
          group.isDefault = name == "dev";
          runOptions.runOn = "folderOpen";
        }
      ) (lib.removeAttrs config.scripts [ "django" ])
      # containers
      ++ lib.mapAttrsToList (name: _: {
        label = "container: ${name}";
        type = "shell";
        command = "devenv container copy ${lib.escapeShellArg name}";
        group = "build";
      }) config.containers
      # outputs
      ++ lib.mapAttrsToList (name: _: {
        label = "package: ${name}";
        type = "shell";
        command = "devenv build outputs.${lib.escapeShellArg name}";
        group = "build";
      }) config.outputs;
  };

  ## Git hooks

  git-hooks.hooks = {
    check-json.enable = true;
    check-merge-conflicts.enable = true;
    check-python.enable = true;
    check-symlinks.enable = true;
    check-toml.enable = true;
    check-yaml.enable = true;
    deadnix.enable = true;
    detect-private-keys.enable = true;
    editorconfig-checker.enable = true;
    end-of-file-fixer.enable = true;
    fix-byte-order-marker.enable = true;
    nixfmt-rfc-style.enable = true;
    prettier.enable = true;
    ripsecrets.enable = true;
    ruff.enable = true;
    shellcheck.enable = true;
    shfmt.enable = true;
    taplo.enable = true;
    uv-check.enable = true;
  };

}
