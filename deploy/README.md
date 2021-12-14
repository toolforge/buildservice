## Admin Manifests

These manifests are meant to be run during deployment and update by admins of
the Toolforge system, not by users. The top level auth.yaml file is just a
template of the secret that must be added to log into the docker registry.

In order to deploy this, first, apply the manifests in the tekton-manifests
directory to set up Tekton Pipelines. Once that is up, run, from this directory
`kubectl apply -k deploy` to apply most of the necessary system and populate
the `image-build` namespace. At that point, you will need to create a proper
secret manifest and apply that as well before you try building anything.
