{ jacobi ? import
    (fetchTarball {
      name = "jpetrucciani-2023-06-15";
      url = "https://github.com/jpetrucciani/nix/archive/88e5beefe6fd625bba224bc3e97bf29d009b634f.tar.gz";
      sha256 = "111vvzlckmiz1kfmxvyphlv6riss6690v3wkn89mmmym5n7148si";
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
