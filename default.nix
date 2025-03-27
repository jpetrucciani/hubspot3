{ pkgs ? import
    (fetchTarball {
      name = "jpetrucciani-2025-03-27";
      url = "https://github.com/jpetrucciani/nix/archive/83eb90f14b4c3343c7ed98d461e094087504f757.tar.gz";
      sha256 = "0df6grw1i5p2hpxlbws4lzqay1b44dmsqg02gwvi4fzz42jin1cv";
    })
    { }
}:
let
  name = "hubspot3";

  tools = with pkgs; {
    cli = [
      gnumake
    ];
    python = [
      (python311.withPackages (p: with p; [
        fire

        # testing
        black
        mypy
        pytest
        pytest-cov
        setuptools
        tox
      ]))
    ];
    scripts = pkgs.lib.attrsets.attrValues scripts;
  };

  scripts = with pkgs; {
    test_actions = writeShellScriptBin "test_actions" ''
      export DOCKER_HOST=$(${docker-client}/bin/docker context inspect --format '{{.Endpoints.docker.Host}}')
      ${act}/bin/act --container-architecture linux/amd64 -r --rm
    '';
  };
  paths = pkgs.lib.flatten [ (builtins.attrValues tools) ];
  env = pkgs.buildEnv {
    inherit name paths; buildInputs = paths;
  };
in
(env.overrideAttrs (_: {
  inherit name;
  NIXUP = "0.0.9";
})) // { inherit scripts; }
