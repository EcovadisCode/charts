{{/* vim: set filetype=mustache: */}}
{{/*
Expand the name of the chart.
*/}}
{{- define "charts-dotnet-core.name" -}}
{{- default .Chart.Name .Values.global.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "charts-dotnet-core.fullname" -}}
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
{{- define "charts-dotnet-core.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "charts-dotnet-core.labels" -}}
helm.sh/chart: {{ include "charts-dotnet-core.chart" . }}
{{ include "charts-dotnet-core.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- if .Values.global.additionalLabelsEnabled }}
{{ toYaml .Values.global.additionalLabels }}
{{- end }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "charts-dotnet-core.selectorLabels" -}}
app.kubernetes.io/name: {{ include "charts-dotnet-core.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Create the name of the service account to use
*/}}
{{- define "charts-dotnet-core.serviceAccountName" -}}
{{- if .Values.global.serviceAccount.create }}
{{- default (include "charts-dotnet-core.fullname" .) .Values.global.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.global.serviceAccount.name }}
{{- end }}
{{- end }}