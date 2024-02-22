{
  description = "A very basic flake";
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs";
  };

  outputs = { self, nixpkgs}: let
    eachSystem = f:
    nixpkgs.lib.genAttrs [ "x86_64-linux" ]
    (system: f { pkgs = nixpkgs.legacyPackages.${system}; });
  in {
    packages = eachSystem ({ pkgs }: let
      python = pkgs.python311Packages; 
    in {
      default = python.buildPythonPackage {
        name = "wiresbot";
        pyproject = true;
        strictDeps = true;
        src = ./.;
        build-system = [ python.setuptools-scm ];
        dependencies = (builtins.attrValues {
          inherit (python) discordpy pillow jishaku;
          discord-py-paginators = python.callPackage ./nix/dpy-paginator.nix { };
        });
        meta.mainProgram = "bot";
      };
    });
  };
}
