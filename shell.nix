let
  nixpkgs = import
    (
      fetchTarball {
        name = "nixos-unstable-2021-08-31";
        url = "https://github.com/NixOS/nixpkgs/archive/cb021898fab2a19e75d4e10c10c1da69c4e9f331.tar.gz";
        sha256 = "1hxpp44bg1gwfzcd570wqfvd6am4vk52938zqcwy7mxwjmk6wbrh";
      }
    )
    { };
  pypiData =
    fetchTarball
      {
        name = "pypi-deps-db-src";
        url = "https://github.com/DavHau/pypi-deps-db/archive/6a8fd687982db22d0290360611567a5534ef23a5.tar.gz";
        sha256 = "1x0fh1h94vv7zr8xd96555aw8k81hh98abj25jswf8cyxznprgwj";
      };
  mach-nix = import
    (builtins.fetchGit {
      url = "https://github.com/DavHau/mach-nix/";
      ref = "refs/tags/3.3.0";
    })
    {
      inherit pypiData;
      pkgs = nixpkgs;
      python = "python39";
    };
in
mach-nix.mkPythonShell {
  requirements = ''
    ${builtins.readFile ./requirements.txt}
    ${builtins.readFile ./requirements-dev.txt}
  '';
}
