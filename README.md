## Toolforge Build Service

In the effort to set up a viable buildpacks workflow, this repo houses necessary
manifests, code and values to deploy the actual build service itself.

There are components necessary to the healthy functioning of the service that
will likely not be included in this repository, such as custom webhooks, etc.

See also https://wikitech.wikimedia.org/wiki/Wikimedia_Cloud_Services_team/EnhancementProposals/Toolforge_Buildpack_Implementation


### Setup dev environment
#### Requirements
You will need to install:
* [docker](https://www.docker.com/) -> as the container engine for everything.
* [docker-compose](https://docs.docker.com/compose/) -> for harbor (docker registry).
* [minikube](https://minikube.sigs.k8s.io/docs/) -> as dev kubernetes installation.

#### Run harbor
You can install it with the helper script:
* `utils/get_harbor.sh`
After that you can use docker-compose to run the whole harbor system (see the output of the script for the exact command).

Once harbor is running, you will need to make sure that it's setup (user project created and such) so run:
- `utils/setup_harbor.py`

### Setup minikube
We will need to get a specific k8s version (1.21.6 is the current toolforge version when writing this, you might want to double check):
 - `minikube start --kubernetes-version=v1.21.6`

### Setup admission controller (optional)
If you want to do a full stack test, you'll need to deploy the buildpack admission controller too, for that follow the instructions [here](https://github.com/toolforge/buildpack-admission-controller).
**NOTE**: might be faster to build the buildpack admission controller image locally instead of pulling it.

### Deploying
If you want to check first what would be deployed, you can run:
- `kubectl kustomize deploy/devel | vim -`

Deploying this system can be done with:
- `./deploy.sh devel`

**NOTE**: in the past we have seen kustomize failing to apply the credentials at the same time that resources that use them, if that happens, try removing base-tekton from devel/kustomization.yaml and deploying base-tekton seperately first, before finally running `./deploy.sh devel`

to deploy to toolsbeta, log into the target toolsbeta control plane node as root (or as a cluster-admin user), with a checkout of the repo there somewhere (in a home directory is probably great), run:
`root@toolsbeta-k8s-control-1:# ./deploy.sh toolsbeta`

to deploy to tools, log into the target tools control plane node as root (or as a cluster-admin user), with a checkout of the repo there somewhere (in a home directory is probably great), run:
`root@tools-k8s-control-1:# ./deploy.sh tools`


### Run a pipeline
- `kubectl create -f example-user-manifests/pipelinerun.yaml`

### Debugging
At this point I recommend installing the [tekton cli](https://tekton.dev/docs/cli/), that makes it easier to inspect (otherwise you have a bunch of json to parse).


Getting the taskruns:
- `tkn -n image-build taskruns list`

Showing the details for them:
- `tkn -n image-build taskruns describe`

Seeing the logs live of a specific run:
- `tkn -n image-build taskruns logs -f minikube-user-buildpacks-pipelinerun-n8mbj-build-from-git-6r2hf`

Of course, you can get all that info too with kubectl directly, though it's quite more terse (though might help debugging tricky issues):
- `kubectl describe -n image-build taskruns.tekton.dev minikube-user-buildpacks-pipelinerun-n8mbj-build-from-git-6r2hf`


### Cleanup
If you want to remove everything you did to start from scratch, you can just:
- `minikube delete`

**NOTE**: this will delete the whole k8s cluster, if you are playing with other things in that same cluster, you might want want to delete each namespace/resource one by one instead.

#### If you installed harbor with this guide
This will not remove the volumes on harbor side, to do so you'll have to stop harbor:

- `docker-compose -f .harbor/harbor/docker-compose.yml down -v --remove-orphans`

And you'll need to delete the data directory (sudo is needed due to files created/modified inside the containers):
- `sudo rm -rf .harbor/harbor/data`

**NOTE**: For production, TBD
