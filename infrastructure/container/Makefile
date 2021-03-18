LOCAL_IMAGE_NAME=warehouse-loader

# import deploy config
# You can change the default deploy config with `make dpl="deploy_special.env" release`
dpl ?= deploy.env
include $(dpl)
export $(shell sed 's/=.*//' $(dpl))

# HELP
# This will output the help for each task
# thanks to https://marmelab.com/blog/2016/02/29/auto-documented-makefile.html
.PHONY: help

help: ## This help.
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

.DEFAULT_GOAL := help

build: ## Build the container
	docker build -t $(LOCAL_IMAGE_NAME) .

build-nc: ## Build the container without caching
	docker build --no-cache -t $(LOCAL_IMAGE_NAME) .

publish: repo-login publish-prod

publish-prod:
	@echo 'publish latest to $(DOCKER_REPO)'
	test -n "$(STACK)" # $$STACK
	docker push $(DOCKER_REPO)/warehouse-$(STACK)-pipeline:prod

tag: ## Generate container prod tag for the container for $STACK
	@echo 'create tag prod'
	test -n "$(STACK)" # $$STACK
	docker tag $(LOCAL_IMAGE_NAME) $(DOCKER_REPO)/warehouse-$(STACK)-pipeline:prod

# login to AWS-ECR
repo-login: ## Auto login to AWS-ECR unsing aws-cli
	aws ecr get-login-password --region eu-west-2 | docker login --username AWS --password-stdin $(DOCKER_REPO)