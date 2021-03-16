# Warehouse loader Docker image

The Docker image source that runs the the warehouse pipeline scripts.

## Build and deploy

To build the image, you can use the commands defined in the `Makefile`
in this folder:

```shell
make build
```

After this you should have a `warehouse-loader` image locally.

To deploy the new image the the Elastic Container Registry for a given
stack (e.g. `prod`, ...).

First edit `deploy.env` to fill in the `DOCKER_REPO` variable's account
number and region information, as appropriate for the given warehouse
stack's ECR repositories.

After that run the tagging with the appropriate `STACK` value:

```shell
make -e STACK=... tag
```

which will create the appropriate `:prod` Docker image tag for the
given stack, from the previously built image.

To deploy/publish the relevant image, run:

```shell
make -e STACK=... publish
```

with the appropriate `STACK` value filled in here as well.
After this you should see the new image in the AWS console
for the appropriate ECR repository (and previous versions
being `<untagged>`).