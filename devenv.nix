{
  config,
  inputs,
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

  scripts.repl.exec = ''
    django shell "$@"
  '';

  scripts.docker-login.exec = ''
    skopeo login docker.io -u roboteamtwente "$@"
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
    pkgs.curl
    pkgs.git
    pkgs.httpie
    pkgs.openssh
    pkgs.skopeo
  ];

  ## Tests

  tasks."django:test" = {
    exec = "django test";
    before = [ "devenv:enterTest" ];
  };

  ## Packages

  outputs.packages = {
    admin = pkgs.writeShellApplication {
      name = "admin";
      runtimeInputs = [ venv ];
      text = ''
        DJANGO_SETTINGS_MODULE=door_tracker.settings django-admin "$@"
      '';
    };

    static = pkgs.stdenv.mkDerivation {
      name = "static";
      src = ./door_tracker;

      dontConfigure = true;
      dontBuild = true;

      nativeBuildInputs = [ config.outputs.packages.admin ];

      installPhase = ''
        DJANGO_STATIC_ROOT=$out admin collectstatic --no-input
      '';
    };

    serve = pkgs.writeShellApplication {
      name = "serve";
      runtimeInputs = [
        config.outputs.packages.admin
        venv
      ];
      runtimeEnv.DJANGO_STATIC_ROOT = config.outputs.packages.static;
      text = ''
        admin migrate
        daphne -b 0.0.0.0 door_tracker.asgi:application
      '';
    };

    init = pkgs.writeShellApplication {
      name = "init";
      runtimeInputs = [ config.outputs.packages.admin ];
      text = ''
        admin migrate
        admin createsuperuser
      '';
    };
  };

  ## Containers

  outputs.containers = {
    serve = inputs.nix2container.packages.${pkgs.system}.nix2container.buildImage {
      name = "roboteamtwente/rfid-tracker-serve";
      tag = "latest";
      maxLayers = 125;
      copyToRoot = [
        config.outputs.packages.admin
        config.outputs.packages.init
        config.outputs.packages.serve
      ];
      config.Cmd = [ "/bin/serve" ];
    };
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
          label = "run script: ${name}";
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
      ++ lib.concatMap (name: [
        {
          label = "build container: ${name}";
          type = "shell";
          command = "$(devenv build outputs.containers.${lib.escapeShellArg name}.copyToDockerDaemon)/bin/copy-to-docker-daemon";
          group = "build";
        }
        {
          label = "upload container: ${name}";
          type = "shell";
          command = "$(devenv build outputs.containers.${lib.escapeShellArg name}.copyToRegistry)/bin/copy-to-registry";
          group = "build";
        }
      ]) (lib.attrNames config.outputs.containers)
      # packages
      ++ lib.mapAttrsToList (name: _: {
        label = "build package: ${name}";
        type = "shell";
        command = "devenv build outputs.packages.${lib.escapeShellArg name}";
        group = "build";
      }) config.outputs.packages;
  };

  ## Git hooks

  git-hooks.hooks = {
    actionlint.enable = true;
    check-executables-have-shebangs.enable = true;
    check-json.enable = true;
    check-merge-conflicts.enable = true;
    check-shebang-scripts-are-executable.enable = true;
    check-symlinks.enable = true;
    check-toml.enable = true;
    check-yaml.enable = true;
    deadnix.enable = true;
    detect-private-keys.enable = true;
    eclint.enable = true;
    end-of-file-fixer.enable = true;
    eslint.enable = true;
    fix-byte-order-marker.enable = true;
    hadolint.enable = true;
    markdownlint.enable = true;
    nixfmt-rfc-style.enable = true;
    prettier.enable = true;
    ripsecrets.enable = true;
    ruff.enable = true;
    ruff-format.enable = true;
    shellcheck.enable = true;
    shfmt.enable = true;
    taplo.enable = true;
    trim-trailing-whitespace.enable = true;
    uv-check.enable = true;
  };

}
