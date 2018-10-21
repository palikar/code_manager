# Abstract


# Installation

Currently the project is not on [PyPi](https://pypi.org/) so you have to clone the repo yourself and then use the `setup.py` file for a manual installation.

```sh
git clone https://github.com/palikar/code_manager
cd code_manager
sudo python setup.py install
code-manager --setup-only
```

*Suggestion:* You may want to install the utility as

```sh
sudo python setup.py install --record install_manifest.txt
```

so that later you can delete all of the associated files. The deletion can be performed with something like:

```sh
cat install_manifest.txt | xargs rm -rf
```


# Usage

The tool is pretty straight forward to use. The information for the packages that can be installed is give in the file `~/.config/code_manager/packages.json` and the configuration for the utility is in `~/.config/code_manager/conf`. Those two files are explained in the following two sections. Working with the command line interface is simple to use and it&rsquo;s also later explained.


## `conf` file

This files tell `code-manager` where to download and where to install the packages that should be downloaded and installed. An example of a `conf` file:

```conf
[Config]
        code = ${HOME}/core.d/code
        usr = ${HOME}/core.d/usr
```

To note is that the values of the fields can indeed contain environmental variables. Those will be expanded by the `code-manager`. Simple explanations:

| Var           | Description                                         |
| `Config.code` | The directory where the packages will be downloaded |
| `Config.usr`  | A directory that will be used as a installed        |
|               | prefix while installing the packages                |


## `packages.json`

```json
{
    "packages_list": [
        "<list of names for packages in group 0>",
        "<list of names for packages in group 1>",
            .
            .
            .
    ],
    "debian_packages":[
        "<list of names for debian packages>"
    ],
    "packages": {
        "<package name>": {
            "download": "git\curl\wget",
            "URL": "<url>",
            "install": "script\cmake\command",
            "script": "<script file>",
            "script_args": "",
            "command" : "<shell command>" ,
            "reinstall_command": "<shell command>",
            "cmake_args" : "<extra arguments for cmake>",
            "make_args" : "<extra arguments for make (for example -j4)>"
            "dependencies": "<list of other packages>",
            "deb_packages": "<list of debian packages>"
    },
            .
            .
            .
}

```


## Command line

A simple call of `code-mamanger --help` gives:

    usage: code-mamanger [-h] [--version] [--setup-only] [--list-packages]
                         [--clear-cache] [--install PACKAGES [PACKAGES ...]]
                         [--reinstall REINSTALL [REINSTALL ...]]
                         [--code-dir CODE_DIR] [--usr-dir USR_DIR]
                         [--packages-file PACKAGES_FILE]
                         [--install-all [INST_ALL]] [--reinstall-all [REALL]]
                         [--no-install]
    
    Installs system packages from the INTERNET!!
    
    optional arguments:
      -h, --help            show this help message and exit
      --version, -v         Print veriosn inormation
      --setup-only          Only copy the config files if needed
      --list-packages       List the available packages in the packages.json file
      --clear-cache         Clears the entries in the cach file
      --install PACKAGES [PACKAGES ...]
                            Packages to install
      --reinstall REINSTALL [REINSTALL ...]
                            Packages to reinstall
      --code-dir CODE_DIR   A folder to put the source of the packages
      --usr-dir USR_DIR     A folder to install the packages
      --packages-file PACKAGES_FILE
                            File to read the packages from
      --install-all [INST_ALL]
                            Install all packages in --packages from the given
                            group
      --reinstall-all [REALL]
                            Reinstall all packages in --packages from the given
                            group
      --no-install          If present, packages will only be downloaded

The majority of the arguments are self-explanatory. The following table presents explanations for some of the other ones.

| Argument        | Description |
| `--install`     |             |
| `--install-all` |             |
|                 |             |

`--reinstall` and `--reinstall-all` function analogously.
