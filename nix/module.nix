{ config, pkgs, lib, ...}:
let
    cfg = config.services.wiresbot;
    inherit (lib)
        types
        mkEnableOption
        mkIf
        mkOption
        getExe
    ;
in
{
    options.services.wiresbot = {
        enable = mkEnableOption "wires bot";
        package = mkOption {
            type = types.package;
        };
        config = mkOption {
            type = types.str;
            description = "A non-nix store path to the TOML configuration";
        };
    };


    # Heavily based off of 
    # https://github.com/viperML/nixos-discord-bot/blob/bb0ef7f12a3f544ed85ce36d351e8523134131d7/nixos-module.nix
    config.systemd.services.wires = mkIf cfg.enable {
        reloadTriggers = [ cfg.package ];
        requires = [ "network.target" ];
        wantedBy = [ "multi-user.target" ];
        serviceConfig = {
            ExecStart = getExe cfg.package;
            LoadCredential = "configuration:${cfg.config}"; 
            DynamicUser = true;

            # hardening
            CapabilityBoundingSet = "";
            LockPersonality = true;
            MemoryDenyWriteExecute = true;
            PrivateDevices = true;
            PrivateUsers = true;
            ProcSubset = "pid";
            ProtectClock = true;
            ProtectControlGroups = true;
            ProtectHome = true;
            ProtectHostname = true;
            ProtectKernelLogs = true;
            ProtectKernelModules = true;
            ProtectKernelTunables = true;
            ProtectProc = "invisible";
            RestrictAddressFamilies = ["AF_INET" "AF_INET6"];
            RestrictNamespaces = true;
            RestrictRealtime = true;
            SystemCallArchitectures = "native";
            SystemCallFilter = "@network-io @system-service";
            UMask = "0077";
            DeviceAllow = "";
        };
    };

}
