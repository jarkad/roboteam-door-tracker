{ ... }:

{

  ## Languages

  languages.python = {
    enable = true;
    uv.enable = true;
    uv.sync.enable = true;
  };

  ## Tests

  tasks."django:test" = {
    exec = ''
      uv run door_tracker/manage.py test
    '';
    before = [ "devenv:enterTest" ];
  };

}
