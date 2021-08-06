## Examples

The materials here should not be regarded as how the workflow will work for most
users. That said, this probably will work in the final product if people did it
from a bastion server. Users will have access to create pipelineruns and pvcs
in order to fire off a buildpack run manually (possibly via `webservice`).

The intent is to have these objects tightly controlled via validating webhook
and to mostly trigger them from events on the CI system.

An automated cleanup job is also called for.
