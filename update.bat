@echo off
del /Q "%INST_MC_DIR%\mods\*.jar"
"%INST_JAVA%" -jar "%INST_MC_DIR%\packwiz-installer-bootstrap.jar" https://raw.githubusercontent.com/xJP8/BlockTopia-3/main/pack.toml