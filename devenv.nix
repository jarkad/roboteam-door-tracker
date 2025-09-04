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

  packages = [ pkgs.git ];

  ## Tests

  tasks."django:test" = {
    exec = "django test";
    before = [ "devenv:enterTest" ];
  };

  ## Packages

  outputs.static = pkgs.stdenv.mkDerivation {
    name = "static";
    src = ./door_tracker;

    dontConfigure = true;
    dontBuild = true;

    nativeBuildInputs = [ venv ];

    installPhase = ''
      export STATIC_ROOT=$out
      python manage.py collectstatic --no-input
    '';
  };

  outputs.serve = pkgs.writeShellApplication {
    name = "serve";
    runtimeInputs = [ venv ];
    runtimeEnv.DJANGO_STATIC_ROOT = config.outputs.static;
    text = ''
      DJANGO_SETTINGS_MODULE=door_tracker.settings django-admin migrate
      daphne -b 0.0.0.0 door_tracker.asgi:application
    '';
  };

  ## Containers

  containers.serve = {
    name = "rfid-tracker-serve";
    startupCommand = lib.getExe config.outputs.serve;
    copyToRoot = [ ];
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
