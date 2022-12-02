{ jacobi ? import
    (fetchTarball {
      name = "jacobi-2022-12-01";
      url = "https://nix.cobi.dev/x/9945abecd74cb4fd8eac371a1d71ca06fb8dd690";
      sha256 = "1sa4m5sxvkg46bcmd1k5kl7r3jzlrbjfqbam3y7lc5a9n5nbhr3b";
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
        tox
      ]))
    ];
    scripts = [
      (writeShellScriptBin "prospector" ''
        ${prospector}/bin/prospector $@
      '')
    ];
  };

  env = jacobi.enviro {
    inherit name tools;
  };
in
env
