{{/*
Expand the name of the chart.
*/}}
{{- define "charts-core.name" -}}
{{- default .Chart.Name .Values.global.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "charts-core.fullname" -}}
{{- if .Values.global.fullnameOverride }}
{{- .Values.global.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.global.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "charts-core.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "charts-core.labels" -}}
helm.sh/chart: {{ include "charts-core.chart" . }}
{{ include "charts-core.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/name: {{ include "charts-core.name" . }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "charts-core.selectorLabels" -}}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Create the name of the service account to use
*/}}
{{- define "charts-core.serviceAccountName" -}}
{{- if .Values.global.serviceAccount.create }}
{{- default (include "charts-core.fullname" .) .Values.global.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.global.serviceAccount.name }}
{{- end }}
{{- end }}

{{/*
Construct Prometheus host with port
*/}}
{{- define "charts-core.prometheusServer" -}}
{{- printf "http://%s.%s:%s" .Values.global.monitoring.prometheusService .Values.global.monitoring.prometheusNamespace (.Values.global.monitoring.prometheusPort | toString) }}
{{- end }}

{{- define "defaultIngressRule" -}}
{{- $isCorrect := false -}}
{{- if .root.global.envVars -}}
{{ range $key, $val := .root.global.envVars }}
{{- if eq $key "ASPNETCORE_ENVIRONMENT"}}
{{- $isCorrect := true -}}
{{- if not $.sub.isStripprefixEnabled }}
{{- printf "Host(`%s.%s`)" ($val | lower) $.root.global.ingressRoutes.domain }}
{{- range $.sub.stripPrefixes }}
{{- printf " && PathPrefix(`%s`)" . }}
{{- end -}}
{{- else -}}
{{- printf "Host(`%s.%s`)" ($val | lower) $.root.global.ingressRoutes.domain -}}
{{- end -}}
{{ end -}}
{{ end -}}
{{- else -}}
{{- if kindIs "invalid" .sub.rule -}}
{{- fail ".Values.global.envVars must be enabled and not empty in order to create ingress rule" }}
{{- end }}
{{- end }}
{{- if $isCorrect -}}
{{- if kindIs "invalid" .sub.rule -}}
{{- fail ".Values.global.envVars is present, bud does not contain ASPNETCORE_ENVIRONMENT" }}
{{- end }}
{{- end }}
{{- end }}