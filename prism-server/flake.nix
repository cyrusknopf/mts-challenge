{
  inputs.nixpkgs.url = "github:nixos/nixpkgs/nixos-unstable";

  outputs = { nixpkgs, ... }:
    let
      forSystem = nixpkgs.lib.genAttrs [
        "x86_64-linux"
        "aarch64-darwin"
      ];
      pkgsFor = forSystem (system :
        import nixpkgs { inherit system; }
      );
    in
    {
      devShells = forSystem
        (system:
          let
            pkgs = pkgsFor."${system}";
          in
            {
              default = pkgs.mkShell {
                buildInputs = with pkgs;
                  [
                    zsh

                    go 
                    gopls

                    protobuf

                    tree
                    cbonsai

                    (python3.withPackages(p : with p; [
                      requests
                    ]))
                  ];
                shellHook = ''
                    export PATH=${pkgs.zsh}/bin:$PATH
                    export SHELL=${pkgs.zsh}/bin/zsh
                    export NIX_FLAKE_PROMPT="(fenrir)"  # Change this per flake!
                    exec ${pkgs.zsh}/bin/zsh --login
                '';
              };
            }
        );
    };
}
