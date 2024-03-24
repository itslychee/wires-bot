{
  description = "A very basic flake";
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs";
    fruitpkgs.url = "github:itslychee/fruitpkgs?ref=patch/jishaku-bin-bash";
  };

  outputs = { self, nixpkgs, fruitpkgs}: let
    eachSystem = f: nixpkgs.lib.genAttrs [ "x86_64-linux" ] (system: f { pkgs = nixpkgs.legacyPackages.${system}; });
    inherit (nixpkgs.lib) fileset sources;
  in {
    packages = eachSystem ({ pkgs }: let
      python = pkgs.python311Packages; 
    in {
      default = python.buildPythonPackage {
        name = "wiresbot";
        pyproject = true;
        strictDeps = true;
        src = fileset.toSource {
          root = ./.;
          fileset = fileset.unions [
            ./pyproject.toml
            ./wires
          ];
        };
        build-system = [ python.setuptools-scm ];
        dependencies = (builtins.attrValues {
          inherit (python) discordpy pillow;
          inherit (fruitpkgs.legacyPackages.${pkgs.system}.python311Packages) jishaku;
          discord-py-paginators = python.callPackage ./nix/dpy-paginator.nix { };
        });
        meta.mainProgram = "wires";
      };
    });
    nixosModule = import ./nix/module.nix;
  };
}
