Build status:
    [![Build Status](https://travis-ci.org/palikar/code_manager.svg?branch=master)](https://travis-ci.org/palikar/code_manager)
    [![Build Status](https://pyup.io/repos/github/palikar/code_manager/shield.svg)](https://pyup.io/repos/github/palikar/code_manager)
    [![Build Status](https://pyup.io/repos/github/palikar/code_manager/python-3-shield.svg)](https://pyup.io/repos/github/palikar/code_manager/)
    [![Coverage Status](https://coveralls.io/repos/github/palikar/code_manager/badge.svg?branch=master)](https://coveralls.io/github/palikar/code_manager?branch=master)


# Code Manager


## Abstract

This is my personal tool now for managing my github repositories, some system software that I use and pretty much everything that can be downloaded, compiled locally and then installed on a Debian based Linux system. Through this utility one can quickly download and install random things from all over the internet. I&rsquo;ve always wanted some small program that would allow me to quickly bring my github repositories on my local machine so I end it up writing this in my spare time. The program is focused on automation but also on flexibility in the installation process. A lot of software is compiled and installed in some standard way but there are also things that are a little bit trickier. The utility - named appropriately `code_manager` - aims to provide a unified interface for the installation process of all types of software &#x2013; the trickier kind included.

Currently the project is not on [PyPi](https://pypi.org/) so you have to clone the repo yourself and then use the `setup.py` file for a manual installation.


## Installation

The installation from source is possible through this repository.

```sh
git clone https://github.com/palikar/code_manager
cd code_manager
sudo python setup.py install
code-manager -setup-only
```

*Suggestion:* You may want to install the tool as

```sh
sudo python setup.py install --record install_manifest.txt
```

so that later you can delete all of the associated files. The deletion can be performed with something like:

```sh
cat install_manifest.txt | xargs rm -rf
```


## Usage

The tools requires a minimal configuration in order to be used. The information for the packages that can be installed is given in the file `~/.config/code_manager/packages.json` and the configuration for the application itself is in `~/.config/code_manager/conf`. If those file do not exist on your system, the will be created with the first run of `code_manger`. Alternatively, you can run it like:

```sh
code_manger --setup-only
```

in order to only create the configuration files at the right places. The files are explained in the following two sections.


### `conf` file

As the name suggests, the file contains some basic configuration. The default `conf` file is given in the following snippet.

```conf
[Config]
        code = ${HOME}/core.d/code
        usr = ${HOME}/core.d/usr
        debug = true

[Download]
        git_ssh = true
        
[Cache]
        cache = ${HOME}/.config/code_manager/cache

[Logging]
        directory = /home/arnaud/.config/code_manager/logs
```

To note is that the values of the fields can indeed contain environmental variables. Those will be expanded by the `code_manager`.



All of the possible field are given in the table bellow

| Field               | Description                                                                                                          |
| `Config.code`       | The directory where the packages will be downloaded                                                                  |
| `Config.usr`        | Installation directory for the packages. <br> Think of it as the /usr directory in linux systems                     |
| `Download.git_ssh`  | If true, `git clone`  will always be called <br> with the ssh link of the given URL.                                 |
| `Cache.cache`       | A path to a file that will be used as cache, <br> where `code_manger` keeps information about<br> installed packages |
| `Logging.directory` | A path to a directory where `code_manager` will save logging information for each run.                               |


### `packages.json`

The file contains all of the relevant information needed to install a certain package. It is a *JSON*-file and in it there are several lists of packages together with download/compilation/installation information for each package. An example skeleton of the file is:

```json
{
    "vars" : {
        "base": "git@github.com:palikar"
    },

    "packages_list": [
        "group_1" : ["package_1_1", "package_2_1"],
        "group_2" : ["package_1_2", "package_2_2"]
    ],

    "debian_packages": [
        "group_1" : ["deb_package_1_1", "deb_package_2_1"],
        "group_2" : ["deb_package_1_2", "deb_package_2_2"]
    ],

    "packages": {
        "package_1_1": {
            "fetch": "git",
            "git": {
                "url" : "...."
            },
            "install" : ["cmake", "command", "make"],
            "make_args": "-j4"
            "make_extra_targets": [],
            "command" : "echo Ruuning some command"
    },

}
```

At the start of the file, the `vars` node defines several &ldquo;variables&rdquo; that later can be used anywhere in the file. Upon loading, `code_manger` will scan every field and key and will replace `@var_name` with the value of variable as defined in the `vars` node. In the example above, `@base` will be replaced with `git@github.com:palikar`. The expansion will not occur within the `vars` node. This means that a variable cannot be used for the definition of another variable.



`packages_list` contains several lists of names of packages. The idea for the node is to group several packages in a &ldquo;group&rdquo;. The packages of a certain group can later be easily installed together through the CLI. The obvious question: why group definition in the beginning instead of a tagging based system? Well&#x2026; early design decision and I am now too lazy to fix. Every package that is later defined, must be in at least one group.



`debian_packagese` has the same structure as `packages_list`. Here the groups contain packages that can be installed through `apt-get install` on Debian-based systems. Debian packages can be used as dependencies fo `code_manger` packages. For convenience I&rsquo;ve decided that it may be helpful to be able to install a whole bunch of debian packages through `code_manager`. For this reason, the `debian_packages` node, defines what can be installed.



`packages` is a node with detailed definition of every package that can be installed. Every object in the node must be a package-object. The name of every object in the node must also be present in on of the group in the `packages_list` node. The possible fields of each package objects are explained in the next paragraphs.



`fetch` - the fetching method for the package or how it will be downloaded. the field can be either a string or a list of strings. Possible string values are `git` \\ `curl`. These can also be given in a list. `code_manger` will execute each fetcher in the list or the single fetcher given a string. If the `git` fetcher is executed, the package object must also contain a `git` node:

```json
"git" : {
    "url" : "url for the git clone command",
    "checkout": "optional commit ID that will be checked out to"
    "args" : "optional extra artuments for the git clone command"
} 
```

If `curl` is executed the package object must contain a curl node:

```json
"curl" : {
    "url": "url for the curl command",
    "output": "optional file name for the curl command (given as -o)",
    "args": "optional extra artuments for the curl command"
}
```



`extract` - if set to true, `code_manger` will extract any archive files that were fetched.



`install` - this can be either a string or a list of strings. The specifies an installer(s) to be executed by `code_manger`. `code_manger` supports several ones the those are described in the next subsection.



`dependencies` - a list of other `code_manager` packages that should be installed prior to installing the package of the current package object.



`deb_dependencies` - a list of Debian packages that should be installed prior to installing the package of the current package object.

1.  Installers

    For now the supported installation methods are:
    
    -   `cmake` - executes the standard procedure for CMake project in the root directory of the package. It&rsquo;s like running:
    
    ```sh
    mkdir build
    cd build
    cmake .. <cmake_args>
    ```
    
    -   `command` - executes a given shell command in the root directory of the package
    
    -   `script` - executes a given shell script in the root directory of the package
    
    -   `setup.py` - installs the package by calling `python setup.py install` in the root directory.
    
    -   `emacs` - (`~/.emacs` or `~/.emacs.d/init.el`)
    
    -   `make` - executes one or several specified make targets in the build directory of the package.

2.  Installer requirements.

    Some installers require specific field to be present in the package object node. This section summarizes these requirements.
    
    -   `"install" : "command"` **Requirements:**
        -   `command` : a string or a list of strings. If the value is a string, it will be treated as a single command to be executed in a shell inside of the root directory of the package. If the value is a list, each string will be treated as a part of a shell command. The whole list still specifies one shell command.
    
    -   `"install" : "setup.py"` **Requirements:**
        -   `setup_args` : a list of strings. Each string specifies and extra argument to be passed to the `python setup.py install` command.
    
    -   `"install" : "cmake"` **Requirements:**
        -   `cmake_args` : optional list of strings. Each string will be treated as an extra argument for the cmake command.
    
    -   `"install" : "emacs"` **Requirements:**
        -   `el_files` : a list of strings. Each string specifies an emacs-lisp file that should be included in your Emacs startup script.
    
    -   `"install" : "make"` **Requirements:**
        -   `make_extra_targets` : optional list of strings. Each string specifies a make target to be executed.
        -   `make_args` : optional list of strings. Each string specifies an extra argument to be passed to the make command while executing each one of the targets
    
    -   `"install" : "script"` **Requirements:**
        -   `script` : a string that specifies which installation script should be executed in the root directory of the package. The script must be present in the `~/.config/code_manager/install_scripts`
        -   `script_args` : optional list of strings. Each string specifies and extra argument to be passed to the executed script.
    
    To note again, all required or optional fields for the installers are given in the package object node. The next snippet demonstrates a package using the cmake, make and command installers.
    
    ```json
    "example": {
        "fetch": "git",
        "git":{
            "url" :  "https://github.com/palikarexample"
        },
        "install": ["cmake", "make", "command"],
        "cmake_args" : [],
        "make_args" : "-j4",
        "make_extra_targets": ["build", "install"],
        "command" : "echo 'Installing of example was successful'"
    }
    ```


### Command line interface

The main (and for one only one) interface for the utility is the command line program `code-mamanger`. A simple call of `code-mamanger --help` gives:

    

The majority of the arguments are self-explanatory. The following table presents explanations for some of the other ones.

| Argument                | Description                                                                                                                       |
|----------------------- |--------------------------------------------------------------------------------------------------------------------------------- |
| `--install <packages>`  | A list of packages to be installed by the utility.<br> Each package must be present in proper format in the `pacakges.json` file. |
| `--install-all <group>` | A group number (as specified in `pacakges.json`). All of the packages in the coresponding group will be installed.                |

`--reinstall` and `--reinstall-all` function analogously.


## Installation scripts

If the installation type of a package is set to `script`, a custom user-defined script will be used for the compilation/installation of a package. All of the install scripts must be put in the `~/.config/code_manager/install_scripts` folder. Those custom install scripts are a nice way making the whole utility as flexible as possible. If the specific piece of software you want to manage through `code-manager` has a long and tedious non-standard way of compiling/installing, you can abstract all of that away in a shell-script file. After downloading (or cloning) the given URL, the specified script will be executed at the root directory of the package. If the package is to be installed at a specific prefix, `-p <prefix>` will be passed to the script. If the package is being reinstalled, `-r` will be passed to the script. A nice template for a installation script can be:

```sh
#!/bin/bash
usage() { echo "Usage: $0 [-r] [-p preffix]" 1>&2; exit 1; }

while getopts ":rp:" o; do
    case "${o}" in
        r) reinstall=true;;
        p) prefix=${OPTARG};;
        *) usage;;
    esac
done
shift $((OPTIND-1))


[ -z ${reinstall+x} ] && reinstall=false
[ -z ${prefix+x} ] && prefix="/usr/local"

echo "###########################"
echo "### Script for <module> ###"
echo "###########################"

if [ $reinstall = "false" ] ; then
    echo "Installing."
else
    echo "Reinstalling."
fi

echo "Install prefix: ${prefix}"
echo "Script finished"
```
