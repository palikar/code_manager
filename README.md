Build status: [![Build Status](https://travis-ci.org/palikar/code_manager.svg?branch=master)](https://travis-ci.org/palikar/code_manager)


# Abstract

This is my personal tool now for managing my github repositories, some system software that I use and pretty much everything that can be downloaded, compiled locally and then installed on a Debian based Linux system. Through this utility one can quickly download and install random things from all over the internet. I&rsquo;ve always wanted some small program that would allow me to quickly bring my github repositories on my local machine so I end it up writing this in my spare time. The program is focused on automation but also on flexibility in the installation process. A lot of software is compiled and installed in some standard way but there are also things that are a little bit trickier. The utility - named appropriately `code_manager` aims to provide a unified interface for the installation process of all types of software &#x2013; the trickier kind included.


# Installation

Currently the project is not on [PyPi](https://pypi.org/) so you have to clone the repo yourself and then use the `setup.py` file for a manual installation.

```sh
git clone https://github.com/palikar/code_manager
cd code_manager
sudo python setup.py install
code-manager -setup-only
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

| Field         | Description                                                                            |
|------------- |-------------------------------------------------------------------------------------- |
| `Config.code` | The directory where the packages will be downloaded                                    |
| `Config.usr`  | A directory that will be used as a installed <br> prefix while installing the packages |


## `packages.json`

The file contains all of the relevant information needed to install a certain package. As the name suggests this is a *JSON*-file and in it there are several list of packages together with download/compilation/installation information for each package. An example skeleton of the file is:

```json
{
    "packages_list": [
        "<list of names of packages in group 0>",
        "<list of names of packages in group 1>",
    ],
    "debian_packages":[
        "<list of names for debian packages>"
    ],
    "packages": {
        "<package name>": {
            "download": "<git\\curl\\wget>",
            "URL": "<url>",
            "install": "<script\cmake\command>",
            "script": "<script file>",
            "script_args": "extra arguments for the script>",
            "command" : "<shell command>" ,
            "reinstall_command": "<shell command>",
            "cmake_args" : "<extra arguments for cmake>",
            "make_args" : "<extra arguments for make (for example \"-j4\")>",
            "dependencies": "<list of other packages>",
            "deb_packages": "<list of debian packages>"
    },
}
```

-   `packages_list` is a list of lists of `code-manager`-packages. The sub-lists are to be seen as groups of packages. Every single package that can be installed with the `code-manager` must be in one of the groups.
-   `debian_packages` is a list of lists of [Debian](https://www.debian.org/distrib/packages)-packages. <span class="underline">Not used for now</span>.
-   `packages` every object in this node must be a package-object. The name of every object in the node must also be present in the `packages_list`.
-   *package-object* - a node in the `packages` with name the name of the package and contents describing the package itself. The fields in the object can be the following:

| Field               | Description                                                                                                                              |
|------------------- |---------------------------------------------------------------------------------------------------------------------------------------- |
| `download`          | Download method <br> This could be `git` \\ `curl` \\ `wget`                                                                             |
| `URL`               | A URL that should be either a git repository or some sort <br> of a file depending on the download method.                               |
| `install`           | Compilation\Installation method <br> This could be `cmake` \\ `command` \\ `script` \\ <br> `setup.py` \\ `emacs`                        |
| `script`            | The script must be available <br> in `~/.config/code_manager/install_scripts`                                                            |
| `script_args`       | Command line arguments that will be given to the script <br> while executed.                                                             |
| `command`           | A shell command to be executed to install the <br> package. The command will be executed in the <br> root folder of the package.         |
| `reinstall_command` | A shell command to be executed to<br>reinstall the package. The command will be executed in the <br> root folder of the package.         |
| `cmake_args`        | Command line arguments that will be added to the `cmake` <br> command.                                                                   |
| `make_args`         | Command line arguments that will be added to the `make` <br> command.                                                                    |
| `setup_args`        | Command line arguments that will be added to the `python setup.py install` <br> command.                                                 |
| `el_files`          | `.el` files to be included in your Emacs configuration.                                                                                  |
| `dependencies`      | A list of other packages that are required for the<br> current package. Those will be installed <br> before the package is installed.    |
| `deb_packages`      | A list of Debian packages that are required for the  <br>  current package Those will be installed before <br> the package is installed. |

The `install` field specifies the compilation\installation type for the project. For now the supported methods are:

-   `cmake` - executes the standard cmake procedure in the root directory of the package.

```sh
mkdir build
cd build
cmake .. <cmake_args>
make <make_args>
sudo make install
cd ..
```

-   `command` - just execute the shell command given in the `command` field.
-   `script` - execute the install script given in `script`. Explanation on install scripts can be found in the last section.
-   `setup.py` - installs the project with calling `python setup.py install` in the root directory.
-   `emacs` - this will find your Emacs init file (`~/.emacs` or `~/.emacs.d/init.el`) and will include e separate file in it. The new file will on its side include the files from every package installed by `the code_manager`. The files from the package to be included are specified with the field `el_files`.


### Installation type specific fields

As seen above, some of the installation types require some additional fields to be present in the package object. Here we conveniently specify them all.

-   `cmake`
    -   `cmake_args` - Optional
    -   `make_args` - Optional
-   `emacs`
    -   `el_files` - Optional
-   `setup.py`
    -   `setup_args` - Optional
-   `script`
    -   `script_args` - Optional
-   `command`


### Examples


## Command line

The main (and for one only one) interface for the utility is the command line program `code-mamanger`. A simple call of `code-mamanger --help` gives:

    usage: code-mananger [-h] [--version] [--setup-only] [--list-packages]
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

| Argument                | Description                                                                                                                       |
|----------------------- |--------------------------------------------------------------------------------------------------------------------------------- |
| `--install <packages>`  | A list of packages to be installed by the utility.<br> Each package must be present in proper format in the `pacakges.json` file. |
| `--install-all <group>` | A group number (as specified in `pacakges.json`). All of the packages in the coresponding group will be installed.                |

`--reinstall` and `--reinstall-all` function analogously.


# Installation scripts

If the installation type of a package is set to `script`, a custom user defined script will be used for the compilation/installation of a package. All of the install scripts must be put in the `~/.config/code_manager/install_scripts` folder. Those custom install scripts are a nice way making the whole utility as flexible as possible. If the specific piece of software you want to manage through `code-manager` has a long and tedious non standard way of compiling/installing, you can abstract all of that away in a shell-script file. After downloading (or cloning) the given URL, the specified script will be executed at the root of the package&rsquo;s folder. If the package is to be installed at a specific prefix, `-p <prefix>` will be passed to the script. If the package is being reinstalled, `-r` will be passed to the script. A nice template for a installation script can be:

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
