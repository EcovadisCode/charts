# **Pact-Broker Helm chart**
This is an EcoVadis's implementation of Pact-Broker Helm chart. Basically it does two things - deploys Pact-Broker to your kubernetes cluster and exposes your deployment. Nothing excess or complex. Optionally you are able to enable Traefik ingress routes if you have Traefik as a reverse proxy.

What is [Helm](https://helm.sh/)?

What is [Pact (contract testing)](https://pact.io/)?

What is [Pact-Broker](https://github.com/pact-foundation/pact_broker)?

What is [Traefik](https://traefik.io/)?

## **Chart structure**

- templates/
  - _helpers.tpl
  - deployment.yaml
  - env-configmap.yaml
  - env-secret.yaml
  - ingress.yaml
  - service.yaml
  - serviceaccount.yaml
- Chart.yaml
- values.yaml

## **Description**

### **Broker config values**

Pact-Broker configuration is loaded into a container through environment variables of 2 types - general config and secret config. Both done with configmaps (secret config is base64 encrypted). General configuration section is represented by envVars section in `values.yaml`, secret configuration - secEnvVars section in `values.yaml`.

### **Database**
SQL adapter `postgres` is used by default as an adapter which is recommended by Pact-Broker team.

### **Exposing Pact-Broker to the outside of cluster**
Pact-Broker deployment is exposed by `ClusterIP` type service to port 80 by default.

If you have Traefik as reverse proxy - there is an ability to expose your installation of Pact-Broker with set of Traefik IngressRoute CRD resources. You should set `ingress.enabled` to 'true' in order to enable creation of any Traefik resources. 

You have next options for creating routes:
- Create HTTP route
- Create HTTPS route
- Create HTTP to HTTPS redirection with Traefik middleware resource

Only HTTP route is created by default. You can create single route - HTTP or HTTPS, but if you want to enable redirecting with middleware you should enable both routes, so you will have both non-TLS and TLS 'listeners' on Traefik entrypoints.

### **Tokens in values.yaml**
You may notice that there are many tokens like `#{variable}#` in `values.yaml` file. They are intended specially for token replacement tasks which exist in different CI/CD platforms. Sometimes it is more convenient to store configuration values in variables and not in the your own `values.yaml` file.

### **Dockerhub pull secret**

There is a special entry at `image.pullSecrets` in v`alues.yaml` file that passes secret name to k8s Deployment. This secret should contain your docker.io credentials to authenticate against docker hub registry.

It is recommended to [create](https://kubernetes.io/docs/tasks/configure-pod-container/pull-image-private-registry/) and use this secret and not to use anonymous image pulling because there is an issue with dockerhub repos when you may face image pull errors from public repos.

To disable imagePullSecrets:
```
image:
  pullSecrets: []
```
or
```
helm upgrade xxx --set image.PullSecrets=""
```