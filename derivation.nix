{ lib, python3Packages }:
with python3Packages;
buildPythonApplication {
  pname = "cs158b-project";
  version = "1.0";

  propagatedBuildInputs = [ ping3 flask psutil jinja2 prometheus-client ];

  src = ./.;
}
