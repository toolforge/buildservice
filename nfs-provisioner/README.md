# NFS subdir StorageClass provisioner

Passing the source code from the git clone task to the buildpacks-phases task
requires a volume (normally a persistent volume claim). Having a default storage
class in Kubernetes allows that to be a fairly simple process. The subdir
provisioner is very rudimentary, but it gets the job done.

Creation of these will need to also be restricted by webhook and will only be
allowed in the `image-build` namespace. It would make sense to switch to cinder
volumes if we implement the openstack cloud provider and the openstack APIs get
TLS.
