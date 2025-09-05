{ pkgs, ... }:

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

  devcontainer.enable = true;

  devcontainer.settings.customizations.vscode.extensions = [
    "jnoortheen.nix-ide"
    "mkhl.direnv"
    "ms-python.python"
  ];

  packages = [
    pkgs.git
    pkgs.nixfmt
    pkgs.shfmt
    pkgs.taplo
    pkgs.treefmt
  ];

  ## Tests

  tasks."django:test" = {
    exec = "django test";
    before = [ "devenv:enterTest" ];
  };

  ## Config files

  files."lychee.toml".toml = {
    exclude_path = [ "door_tracker/webui/templates/" ];
  };

  files."ruff.toml".toml = {
    format = {
      docstring-code-format = true;
      quote-style = "single";
    };
  };

  files."treefmt.toml".toml = {
    formatter.nixfmt = {
      command = "nixfmt";
      includes = [ "*.nix" ];
    };
    formatter.ruff = {
      command = "ruff";
      options = [ "format" ];
      includes = [ "*.py" ];
    };
    formatter.shfmt = {
      command = "shfmt";
      includes = [
        ".envrc"
        "*.sh"
      ];
    };
    formatter.taplo = {
      command = "taplo";
      options = [ "format" ];
      includes = [ "*.toml" ];
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
    lychee.enable = true;
    ripsecrets.enable = true;
    ruff.enable = true;
    shellcheck.enable = true;
    treefmt.enable = true;
    uv-check.enable = true;
  };

}
