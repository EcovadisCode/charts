#Dotnet Core Helm Chart

Kubernetes is a system for automating deployment and management of applications.
As with each system it comes up with its infrastructure and object definitions. Those objects defintions can be supplied in either *yaml* or *json* files. Furthermore, those objects can be separated into multiple categories.
One of those categories can be the source of the object - it can be either built-in Kubernetes, or user created one (custom resource definition like Traefik's IngressRoute for example).

There are many ways to deploy application to Kubernetes, however we have decided to use Helm as a templating language.
It has the widest community and its CLI offers a lot of functionalities which enable teams to implement CD process in different ways.
To see what Helm 3 has to offer, check out [this site](https://helm.sh/blog/helm-3-released/).

##Chart structure

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

##Process

We would like to implement a solution that will be general and can be used among many projects which are using similar technology.
That is why, we have created a "general" helm chart for all dotnet core applications. It was written in such a way, that we will be able just to overwrite some entries in *values.yaml* file and then deploy it to AKS.

###Chart CI/CD and versioning

As mentioned, we want to follow semantic versioning standard and that is why, whenever there is a change in templates, there also must be a change in *Chart.yaml* file. Otherwise a chart will not be released after the merge is done. A build definition has CI enabled, but only when there was a change in *Chart.yaml* file. Once the build is completed, release is automatically created.

The steps in release pipeline:
 - check last deployed version of helm chart (by comparing variable)
 - run basic helm checks - `helm lint` and `helm template` (to be improved by unit testing and smoke tests in the future)
 - save versioned chart and push it to ACR
 - update version variable in release
 - push helm chart with tag "latest" to ACR if approved 

Build definition: [link](https://azuredevops.ecovadis.com/EcoVadisApp_TeamProjectCollection/EcoVadisOps/_apps/hub/ms.vss-ciworkflow.build-ci-hub?_a=edit-build-definition&id=854&view=Tab_Triggers)
Release definition: [link](https://azuredevops.ecovadis.com/EcoVadisApp_TeamProjectCollection/EcoVadisOps/_releaseDefinition?definitionId=121&_a=environments-editor-preview)

###Unit testing helm chart
In order to minimize probability of faulty helm chart being deployed to ACR we have written set of unit tests which are being run during PRs. We are using python 3.9.1 and pyTest. To run the unit tests locally install needed packages with pip.

Run python --version to check version of your python and make sure it is 3.9.1
If not - uninstall different versions:)

`pip install -r requirements.txt` - run this command in tests directory.

Then run in charts-dotnet-core directory command:

`pytest`

And see the results for yourself.

###Application deployment

####Build
During the build phase, we are traditionally running build process (we are not running powershell scripts / dotnet commmands within container).
Afterwards, we have created a task group called ["Docker - build, scan and push"](https://azuredevops.ecovadis.com/EcoVadisApp_TeamProjectCollection/EcoVadisApp/_taskgroup/472257c6-3652-462e-9cf3-bc7099c784f0). The name is pretty self-explainatory, but in short it builds an image, runs Trivy Vulnerability scan and pushes the image to the ACR. After that, we are creating artifact with only config files (e.g. appsettings.json). The crucial point here is the name of the artifact - the image tag and config files are named the same.

####Release
During the release process we are benefiting from the fact, that the config files and image tag is the same. With this knowledge, we can always use proper image from ACR. First, we pull helm chart and export it. Then is the part that will be decided soon, either we will use Azure App Configuration or base on traditional values.yaml files, but we are somehow supplying the configuration for the app. Then we copy application's json files to the chart directory and replace tokens. Finally, we are installing the chart with `helm upgrade --install` command.

Note:
We do not want to use `--create-namespace` flag. We want to have a separate release, which will create namespace, set-up image-pull-secrts and other infrastructure that will be used.