{ jacobi ? import
    (fetchTarball {
      name = "jpetrucciani-2023-12-22";
      url = "https://github.com/jpetrucciani/nix/archive/6ffe4b6bda332269593a314d7d606d7c5ae02da5.tar.gz";
      sha256 = "01ba1y8v8my7s85wf36mmin29rln1lq1idhj88f0yn8fk7qg752i";
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
