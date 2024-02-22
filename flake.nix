{
  description = "A very basic flake";

  inputs = {
    # Pull from my jishaku branch as it's not in upstream yet
    jishaku.url =  "github:itslychee/fruitpkgs?ref=package/python/jishaku";
  };

  outputs = { self, nixpkgs, jishaku }: let
    eachSystem = f:
    nixpkgs.lib.genAttrs [ "x86_64-linux" ]
    (system: f { pkgs = nixpkgs.legacyPackages.${system}; });
  in {
    packages = eachSystem ({ pkgs }: let
      python = pkgs.python311Packages; 
      jsk = jishaku.legacyPackages.${pkgs.system}.python311Packages.jishaku;
    in {
      default = python.buildPythonApplication {
        name = "wiresbot";
        pyproject = true;
        src = ./.;
        doCheck = false;
        dependencies = (builtins.attrValues {
          jishaku = jsk;
          inherit (python) discordpy pillow;
          discord-py-paginators = python.callPackage ./nix/dpy-paginator.nix { };
        });

      };
    });
  };
}
