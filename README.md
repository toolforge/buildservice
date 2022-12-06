# Toolforge Build Service

In the effort to set up a viable buildpacks workflow, this repo houses necessary manifests,
code and values to deploy the actual build service itself.

There are components necessary to the healthy functioning of the service that will likely
not be included in this repository, such as custom webhooks, etc.

See also [the proposal doc here](https://wikitech.wikimedia.org/wiki/Wikimedia_Cloud_Services_team/EnhancementProposals/Toolforge_Buildpack_Implementation)

## Setup dev environment

### Requirements

You will need to install:

- [docker](https://www.docker.com/) -> as the container engine for everything.
- [docker-compose](https://docs.docker.com/compose/) -> for harbor (docker registry).
- [minikube](https://minikube.sigs.k8s.io/docs/) -> as dev kubernetes installation.

### Setup minikube

You need to specify the current Kubernetes version running on Toolforge.
At the time of writing, it's 1.21.8, although you might want to double check.

- `minikube start --kubernetes-version=v1.21.8`

### Setup Harbor

1. **Find you future local Harbor IP**

You will need to reach your local Harbor instance from inside minikube using an
IP (this is a limitation of Tekton that doesn't support hostnames for
self-signed certificates).

The IP to use will vary depending on your machine and OS, as we deploy harbor
with docker-compose this will be the IP where docker lives.

This is usually:

- `export HARBOR_IP=$(minikube ssh "grep host.minikube.internal /etc/hosts" | awk '{print $1}')`

But sometimes (ex. debian bullseye) you will need to use the external IP of your host:

- `export HARBOR_IP=$(hostname -I| awk '{print $1}')`


Once Harbor is up and running, you
can verify if the IP you chose works by curling to it:

```
$ curl -s http://$HARBOR_IP -o /dev/null && echo "works" || echo "does not work"
works
`

If it does not, use the alternative method, or select one of the different IPs
from your laptop (and/or ask for help!).``

**NOTE**: On some setups, notably macOS and minikube with docker
as the driver (the default setting), the HARBOR_IP in the `curl`
command above should be localhost. Same goes for accessing the
Harbor UI via your browser. The internal IP is still needed for
Tekton to communicate with Harbor, so don't skip that step.


2. **Install & Configure Harbor**
   You can install Harbor with the helper script:

- `utils/get_harbor.sh`

Spin up Harbor with docker-compose:

- `docker-compose -f .harbor/harbor/docker-compose.yml up -d`

If the docker-compose command exits with an error, try running it again
(there is a race condition that sometimes makes it fail on the first run).

Once Harbor is running, you will need to make sure that it's set up
(user project created and such) so run:

- `utils/setup_harbor.py`

### Setup admission controller (optional)

If you want to do a full stack test, you'll need to deploy the buildpack
admission controller too, for that follow the instructions
[here](https://github.com/toolforge/buildpack-admission-controller).

**NOTE**: might be faster to build the buildpack admission controller image locally instead of pulling it.

### Deploying

Deploying this system can be done with:

- `./deploy.sh devel`

to deploy to toolsbeta, log into the target toolsbeta control plane node as root (or as a cluster-admin user),
with a checkout of the repo there somewhere (in a home directory is probably great), run:
`root@toolsbeta-k8s-control-1:# ./deploy.sh toolsbeta`

to deploy to tools, log into the target tools control plane node as root (or as a cluster-admin user),
with a checkout of the repo there somewhere (in a home directory is probably great), run:
`root@tools-k8s-control-1:# ./deploy.sh tools`

### Run a pipeline

`sed "s/{{HARBOR_IP}}/$HARBOR_IP/" example-user-manifests/pipelinerun.yaml | kubectl create -f -`

($HARBOR_IP is the ip exported in one of the previous steps)

### Debugging

At this point, we recommend installing the [tekton cli](https://tekton.dev/docs/cli/).
This makes it easier to inspect (otherwise you have a bunch of json to parse).

Getting the taskruns:

- `tkn -n image-build taskruns list`

Showing the details for them:

- `tkn -n image-build taskruns describe`

Seeing the logs live of a specific run:

- `tkn -n image-build taskruns logs -f minikube-user-buildpacks-pipelinerun-n8mbj-build-from-git-6r2hf`

Of course, you can get all that info too with kubectl directly,
though it's quite more terse (though might help debugging tricky issues):

- `kubectl describe -n image-build taskruns.tekton.dev minikube-user-buildpacks-pipelinerun-n8mbj-build-from-git-6r2hf`

### Cleanup

If you want to remove everything you did to start from scratch, you can just:

- `minikube delete`

**NOTE**: this will delete the whole K8s cluster, if you are playing with other things in that
same cluster, you might want want to delete each namespace/resource one by one instead.

#### If you installed Harbor with this guide

This will not remove the volumes on the Harbor side, to do so you'll have to stop Harbor:

- `docker-compose -f .harbor/harbor/docker-compose.yml down -v --remove-orphans`

Then, delete the data directory (sudo is needed due to files created/modified inside the containers):

- `sudo rm -rf .harbor/harbor/data`

### Notes on setting up Harbor in production

In development, every component of Harbor is deployed via docker-compose. In production, we use an external database.
Currently, only PostgreSQL is supported by Harbor. This PostgreSQL db should be set up as a Trove instance with a Cinder volume.

To configure Harbor for use with an external db, you need to uncomment the
`external_database` section in `/srv/ops/harbor/harbor.yml`and fill in the
necessary information. For the config changes to take effect, you need to run the
`/srv/ops/harbor/install.sh` script afterwards.
Remember to also remove the db service from Harbor's `docker-compose.yml`.

On toolsbeta, Harbor is deployed on toolsbeta-harborweb-2. The configuration is
under `srv/ops/harbor`, and the data under `/srv/harbor`. Puppet code can be
found [in this puppet manifest](https://gerrit.wikimedia.org/r/plugins/gitiles/operations/puppet/+/refs/heads/production/modules/profile/manifests/toolforge/harbor.pp)
