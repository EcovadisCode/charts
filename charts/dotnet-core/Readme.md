# Dotnet Core Helm Chart

Kubernetes is a system for automating deployment and management of applications.
As with each system it comes up with its infrastructure and object definitions. Those objects defintions can be supplied in either *yaml* or *json* files. Furthermore, those objects can be separated into multiple categories.
One of those categories can be the source of the object - it can be either built-in Kubernetes, or user created one (custom resource definition like Traefik's IngressRoute for example).

There are many ways to deploy application to Kubernetes, however we have decided to use Helm as a templating language.
It has the widest community and its CLI offers a lot of functionalities which enable teams to implement CD process in different ways.
To see what Helm 3 has to offer, check out [this site](https://helm.sh/blog/helm-3-released/).

## Chart structure

As you can see in this repository, each chart must consist of a directory which represents its name.
Every yaml file which is located within this directory is taken into consideration during the deployment.
I have written *taken into consideration* because there are few special files, which steer what will be deploy and what represents what.
Those files / groups of files are:
 - *Chart.yaml*
 - *values.yaml*
 - *CRD* - directory
 - *tests* - directory
 - *_helpers.tpl*
 - *.yaml files*

*Chart.yaml* - contains general information about the chart like its name, version, description and dependencies. More information can be found [here](https://helm.sh/docs/topics/charts/). Note, after updating anything in this repository, you **MUST** update *version* according to semantic versioning 2.0 standard.

*values.yaml* - placeholder for actual values that should be into the chart. Depending on its content, different objects will be created by Helm. 
Data from this file can be accessed in .yaml files by referencing namesmace *.Values*. For example, if in values.yaml file we have section
```
autoscaling:
  enabled: false
```
Then, in any yaml file you can refer to this variable with `{{ .Values.autoscaling.enabled }}` - this is how we manipulate which object should be created.

*.yaml files* - everything which will be put into templates directory will be taken into consideration during templating process. By everything, I mean built-in Kubernetes objects like: pods, deployments, statefulsets, replicacontrollers, service-accounts, etc.

*CRD* - in Kubernetes it is also possible to define your own objects and use them within you application. In order to create them with Helm, they must be put inside CRD directory. So, for example all IngressRoutes, MiddleWares, PrometheusRules will go there.

*tests* - it is also possible todefine smoke tests for helm charts. The files that reside in the *tests* directory will be created after someone calls command `helm test <release-name>` on already installed helm chart.

*_helpers.tpl* - a file which contains a set of "functions" which usually implement common functionalities. Not required file, but helps to keep chart cleaner. 

## Process

We would like to implement a solution that will be general and can be used among many projects which are using similar technology.
That is why, we have created a "general" helm chart for all dotnet core applications. It was written in such a way, that we will be able just to overwrite some entries in *values.yaml* file and then deploy it to AKS.

### Chart CI/CD and versioning

As mentioned, we want to follow semantic versioning standard and that is why, whenever there is a change in templates, there also must be a change in *Chart.yaml* file. Otherwise a chart will not be released after the merge is done. A build definition has CI enabled, but only when there was a change in *Chart.yaml* file. Once the build is completed, release is automatically created.

The steps in release pipeline:
 - check last deployed version of helm chart (by comparing variable)
 - run basic helm checks - `helm lint` and `helm template` (to be improved by unit testing and smoke tests in the future)
 - save versioned chart and push it to ACR
 - update version variable in release
 - push helm chart with tag "latest" to ACR if approved 
