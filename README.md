# Use Case 3
<!-- markdownlint-disable MD034 MD028 -->

App for the MarketPlace Project's use case 3.

## Installation

This Jupyter-based app is intended to be run with [AiiDAlab](https://www.materialscloud.org/aiidalab).

### Development installation instructions

#### Project Access Token

If you know the Project Access Token (PAT) available to get read access to the AiiDA plugin repository on the Fraunhofer GitLab instance for the MarketPlace project, this approach is for you.

Store the PAT in a file called `.mp_gitlab_token` in the root of this repository locally.

Now you have two options:

1. Use the custom [`Dockerfile`](Dockerfile), or
2. Use the standard AiiDAlab Docker stack from Docker Hub.

For the first option, run the following command:

```shell
docker build --secret id=mp_gitlab_token,src=.mp_gitlab_token -t aiidalab_mp_uc3 .
```

> **Note** If you see the following message:
> ``the --mount option requires BuildKit``
> You must run with the following instead:
> ``DOCKER_BUILDKIT=1 docker build --secret id=mp_gitlab_token,src=.mp_gitlab_token -t aiidalab_mp_uc3 .``
> See https://docs.docker.com/develop/develop-images/build_enhancements/#to-enable-buildkit-builds for more information

Now, you can jump to the [Running AiiDAlab](#running-aiidalab) section below.

Otherwise, for the second option, skip building a local Docker image altogether, and also skip the [Running AiiDAlab](#running-aiidalab) section and instead run the following:

```shell
docker run --rm -d -p 8888:8888 --name aiidalab_mp_uc3 -v ${PWD}:/marketplace/aiidalab-mp-uc3 aiidalab/aiidalab-docker-stack:latest
```

Then, once the AiiDAlab instance has started, you can open it, open a terminal in it and run the following command:

```shell
aiidalab install aiidalab-mp-uc3@file:///marketplace/aiidalab-mp-uc3
```

#### SSH

The app requires access to the Fraunhofer GitLab instance for the MarketPlace project.
If you do not have an SSH connection setup for this, please set that up now by following the documentation from GitLab [here](https://docs.gitlab.com/ee/user/ssh.html).

Ensure the relevant SSH key is added to your current SSH Agent by running

```shell
ssh-add -L
```

If you do not see the relevant SSH key in this list, please add it by running

```shell
ssh-add PATH/TO/PRIVATE/SSH/KEY
```

> **Note**: For Linux systems only - if the SSH Agent is not running in the first place, you can run
>
> ```shell
> eval $(ssh-agent -s)
> ```
>
> Indeed, you should add this line to your `~/.bashrc` file in order to have a running SSH Agent always when you open a terminal.

> **Note** If you see the following message:
> ``the --mount option requires BuildKit``
> You must run with the following instead:
> ``DOCKER_BUILDKIT=1 docker build --ssh default -t aiidalab_mp_uc3 -f Dockerfile_SSH .``
> See https://docs.docker.com/develop/develop-images/build_enhancements/#to-enable-buildkit-builds for more information

Now you can build the Docker image locally from the [Dockerfile](Dockerfile):

```shell
docker build --ssh default -t aiidalab_mp_uc3 -f Dockerfile_SSH .
```

> **Note**: If this build fails, you most likely have not setup the SSH properly _or_ you do not have access to the [Daniel.Marchand/aiida-marketusercase3](https://gitlab.cc-asp.fraunhofer.de/Daniel.Marchand/aiida-marketusercase3) repository on the Fraunhofer GitLab.

#### Running AiiDAlab

Finally, you can run the development AiiDAlab instance in two ways: Either with a copied version of the app or a "dynamic" version.
During development, and for persistence reasons, we recommend the second version.
Ensure you are currently in the root of this repository, then (on Linux) run:

```shell
docker run --rm -d -p 8888:8888 --name aiidalab_mp_uc3 -v ${PWD}:/home/aiida/apps/aiidalab-mp-uc3 aiidalab_mp_uc3
```

On Windows (PowerShell):

```powershell
docker run --rm -d -p 8888:8888 --name aiidalab_mp_uc3 -v C:\path\to\aiidalab-mp-uc3:/home/aiida/apps/aiidalab-mp-uc3 aiidalab_mp_uc3
```

### Original installation instructions

Note, these instructions are currently not relevant, but are left here for future reference.

Assuming that the app was registered, you can install it directly via the app store in AiiDAlab or on the command line with:

```shell
aiidalab install mp-uc3
```

Otherwise, you can also install it directly from the repository:

```shell
aiidalab install mp-uc3@https://gitlab.cc-asp.fraunhofer.de/MarketPlace/apps/uc3-aiidalab.git
```

## Usage

Here may go a few sreenshots / animated gifs illustrating how to use the app.

## License

MIT

## Contact

Casper Welzel Andersen, SINTEF (casper.w.andersen@sintef.no)  
Daniel Marchand, SINTEF (daniel.marchand@sintef.no)  
Bjørn Tore Løvfall, SINTEF (bjorntore.lovfall@sintef.no)
