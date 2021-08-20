## Toolforge Build Service

In the effort to set up a viable buildpacks workflow, this repo houses necessary
manifests, code and values to deploy the actual build service itself.

There are components necessary to the healthy functioning of the service that
will likely not be included in this repository, such as custom webhooks, etc.

See also https://wikitech.wikimedia.org/wiki/Wikimedia_Cloud_Services_team/EnhancementProposals/Toolforge_Buildpack_Implementation

### Deploying

Deploying this system can be done as simply as:
- `cd tekton-manifests`
- `kubectl sudo apply -f tekton-controller-rbac.yaml`
- `kubectl sudo apply -f tekton-pipelines.yaml`
- `cd ../admin-manifests`
- `kubectl sudo apply -k deploy`

At that point, you will need to create a secret object (an example is in admin-manifests/auth.yaml)
that has the robot account for Harbor. Then any Toolforge user can run a pipeline
if they have their project set up in Harbor.

