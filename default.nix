{ jacobi ? import
    (fetchTarball {
      name = "jpetrucciani-2023-03-06";
      url = "https://github.com/jpetrucciani/nix/archive/fbae576baf69718f4328f88a958b93e7784b0539.tar.gz";
      sha256 = "0kcc7rwfy4zdmfcv4rqllwmk9igx0v3mfz196q7k5j1nhhhlnnwj";
    })
    { }
}:
let
  name = "hubspot3";

  tools = with jacobi; {
    cli = [
      gnumake
      jq
      nixpkgs-fmt
    ];
    python = [
      (python310.withPackages (p: with p; [
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
    scripts = [
      (writeShellScriptBin "prospector" ''
        ${prospector}/bin/prospector $@
      '')
      (writeShellScriptBin "test_actions" ''
        export DOCKER_HOST=$(${jacobi.docker-client}/bin/docker context inspect --format '{{.Endpoints.docker.Host}}')
        ${jacobi.act}/bin/act --container-architecture linux/amd64 -r --rm
      '')
    ];
  };

  env = jacobi.enviro {
    inherit name tools;
  };
in
env
