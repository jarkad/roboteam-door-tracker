{ ... }:

{

  ## Languages

  languages.python = {
    enable = true;
    uv.enable = true;
    uv.sync.enable = true;
  };

  enterShell = ''
    export PATH="$DEVENV_ROOT/.venv/bin''${PATH+:}$PATH"
  '';

  ## Tests

  tasks."django:test" = {
    exec = ''
      uv run door_tracker/manage.py test
    '';
    before = [ "devenv:enterTest" ];
  };

}
