#Job Helm Chart
Render templates locally

helm dependency build
helm template .

## Values

The three keys below are opt-in. When unset, they render nothing.

- `global.keda.rollout`: the ScaledJob `spec.rollout`. `strategy: gradual` keeps running jobs when the ScaledJob changes; the KEDA default deletes them.
- `global.podAnnotations`: annotations on the job pods, e.g. `cluster-autoscaler.kubernetes.io/safe-to-evict: "false"`.
- `global.terminationGracePeriodSeconds`: seconds a job pod gets after SIGTERM, on node drain too. The Kubernetes default is 30.
