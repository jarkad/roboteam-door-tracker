{ ... }:

{

  ## Scripts

  scripts.django.exec = ''
    cd $DEVENV_ROOT/door_tracker
    ./manage.py "$@"
  '';

  scripts.dev.exec = ''
    django runserver
  '';

  scripts.makemigrations.exec = ''
    django makemigrations
  '';

  scripts.migrate.exec = ''
    django migrate
  '';

  ## Languages

  languages.python = {
    enable = true;
    uv.enable = true;
    uv.sync.enable = true;
  };

  enterShell = ''
    export PATH="$UV_PROJECT_ENVIRONMENT/bin''${PATH+:}$PATH"
  '';

  ## Tests

  tasks."django:test" = {
    exec = ''
      uv run door_tracker/manage.py test
    '';
    before = [ "devenv:enterTest" ];
  };

}
