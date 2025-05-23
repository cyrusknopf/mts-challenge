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

                    # nvidia-docker
                    # nvidia-container-toolkit
                    bun

                    postgresql_17

                    go 
                    gopls

                    protobuf

                    tree
                    cbonsai

                    pyright
                    (python3.withPackages(p : with p; [
                      requests
                      python-lsp-server
                      numpy
                      tabulate
                      numpy
                      aiohttp
                      tabulate
                      python-lsp-server
                      python-lsp-jsonrpc
                      python-lsp-black
                      python-lsp-ruff
                      pyls-isort
                      pyls-flake8
                      flake8
                      faker
                      isort
                      black
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
