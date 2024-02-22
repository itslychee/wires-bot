{
  lib,
  buildPythonPackage,
  fetchPypi,
  discordpy,
  setuptools
}:
buildPythonPackage rec {
  pname = "discord-py-paginators";
  version = "0.0.1";
  pyproject = true;
  src = fetchPypi {
    inherit pname version;
    hash = "sha256-mPC/Fzr0kubnDXKRD/VZpga8Oq/OW4b+BJ7vOej1RlA=";
  };
  build-system = [ setuptools ];
  dependencies = [ discordpy ];
}
