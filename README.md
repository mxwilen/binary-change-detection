# Version comparison classification

A pipeline for classification of Ghidriff output data. Uses syntax matching against functions and their parents/neighbors to categorize changes.

## Prerequisite
Ghidra requires JDK to run, so make sure Java Development Kit (JDK) 17 or higher is available.
```bash
pip install -r requirements.txt
```

### Install Ghidra
> Ghidra is a software reverse engineering (SRE) framework developed by the National Security Agency (NSA). It helps analyze compiled code on various platforms including Windows, macOS, and Linux.

#### Using homebrew
```bash
brew install --cask ghidra
```

#### Using Chocolatey
```bash
choco install ghidra
```

Then verify setup by running `ghidraRun`.

### Setup Ghidriff
> `ghidriff` provides a command-line binary diffing capability with a fresh take on diffing workflow and results. This project, developed over the course of a year, leverages the power of Ghidra's ProgramAPI and FlatProgramAPI to find the _added_, _deleted_, and _modified_ functions of two arbitrary binaries. It is written in Python3 using pyhidra to orchestrate Ghidra and `jpype` as the Python to Java interface to Ghidra. 
> For more info, see [Ghidriff repo](https://github.com/clearbluejar/ghidriff)

*Already installed through `requirements.txt` using pip.*

#### Set paths in `.env`
Change this path in the environment file.

```bash
GHIDRA_INSTALL_DIR=<path_to_here>/ghidra/XX.X-XXXXXXXX/ghidra_XX.X_PUBLIC/
```


## Run

### Windows
```bash
./run.bat
```

### Linux / Mac
```bash
sh run.sh
```

