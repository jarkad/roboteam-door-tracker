{ pkgs, ... }:

{
  packages = [ pkgs.uv ];

  env.PATH = "$DEVENV_ROOT/.venv/bin:$PATH";
}
