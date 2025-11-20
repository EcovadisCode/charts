{{/* vim: set filetype=mustache: */}}
{{/*
Expand the name of the chart.
*/}}
{{- define "charts-cron-job.name" -}}
{{- default .Chart.Name .Values.global.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
Usage for cronjob-specific name: include "charts-cron-job.fullname" (dict "root" . "cronjob" $cronjob "index" $index)
Usage for global name only: include "charts-cron-job.fullname" .
*/}}
{{- define "charts-cron-job.fullname" -}}
{{- if .root }}
  {{- /* Mode 1: Called with particular cronjob context */ -}}
  {{- $root := .root }}
  {{- $cronjob := .cronjob | default dict }}
  {{- $index := .index }}
  {{- $fullnameOverride := $cronjob.fullnameOverride | default $root.Values.global.fullnameOverride }}
  {{- $nameOverride := $cronjob.nameOverride | default $root.Values.global.nameOverride }}
  {{- $baseName := default $root.Chart.Name $root.Values.global.nameOverride }}
  {{- if $fullnameOverride }}
    {{- $fullnameOverride | trunc 63 | trimSuffix "-" }}
  {{- else if $nameOverride }}
    {{- if contains $baseName $root.Release.Name }}
      {{- printf "%s-%s" $root.Release.Name $nameOverride | trunc 63 | trimSuffix "-" }}
    {{- else }}
      {{- printf "%s-%s-%s" $root.Release.Name $baseName $nameOverride | trunc 63 | trimSuffix "-" }}
    {{- end }}
  {{- else }}
    {{- if contains $baseName $root.Release.Name }}
      {{- printf "%s-%d" $root.Release.Name $index | trunc 63 | trimSuffix "-" }}
    {{- else }}
      {{- printf "%s-%s-%d" $root.Release.Name $baseName $index | trunc 63 | trimSuffix "-" }}
    {{- end }}
  {{- end }}
{{- else }}
  {{- /* Mode 2: Called with global cronjob context */ -}}
  {{- $root := . }}
  {{- if $root.Values.global.fullnameOverride }}
    {{- $root.Values.global.fullnameOverride | trunc 63 | trimSuffix "-" }}
  {{- else }}
    {{- $name := default $root.Chart.Name $root.Values.global.nameOverride }}
    {{- if contains $name $root.Release.Name }}
      {{- $root.Release.Name | trunc 63 | trimSuffix "-" }}
    {{- else }}
      {{- printf "%s-%s" $root.Release.Name $name | trunc 63 | trimSuffix "-" }}
    {{- end }}
  {{- end }}
{{- end }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "charts-cron-job.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
Usage for cronjob-specific labels: include "charts-cron-job.labels" (dict "root" . "cronjob" $cronjob)
Usage for global labels only: include "charts-cron-job.labels" .
*/}}
{{- define "charts-cron-job.labels" -}}
{{- if .root }}
  {{- /* Mode 1: Called with particular cronjob context */ -}}
  {{- $root := .root }}
  {{- $cronjob := .cronjob | default dict }}
helm.sh/chart: {{ include "charts-cron-job.chart" $root }}
{{ include "charts-cron-job.selectorLabels" $root }}
{{- if $root.Chart.AppVersion }}
app.kubernetes.io/version: {{ $root.Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ $root.Release.Service }}
{{- if ($cronjob.additionalLabelsEnabled | default $root.Values.global.additionalLabelsEnabled) }}
{{ toYaml ($cronjob.additionalLabels | default $root.Values.global.additionalLabels) }}
{{- end }}
{{- else }}
  {{- /* Mode 2: Called with global cronjob context*/ -}}
  {{- $root := . }}
helm.sh/chart: {{ include "charts-cron-job.chart" $root }}
{{ include "charts-cron-job.selectorLabels" $root }}
{{- if $root.Chart.AppVersion }}
app.kubernetes.io/version: {{ $root.Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ $root.Release.Service }}
{{- if $root.Values.global.additionalLabelsEnabled }}
{{ toYaml $root.Values.global.additionalLabels }}
{{- end }}
{{- end }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "charts-cron-job.selectorLabels" -}}
app.kubernetes.io/name: {{ include "charts-cron-job.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Create the name of the service account to use
Usage for cronjob-specific SA: include "charts-cron-job.serviceAccountName" (dict "root" . "cronjob" $cronjob "index" $index)
Usage for global SA only: include "charts-cron-job.serviceAccountName" .
*/}}
{{- define "charts-cron-job.serviceAccountName" -}}
{{- if .root }}
  {{- /* Mode 1: Called with particular cronjob context */ -}}
  {{- $root := .root }}
  {{- $cronjob := .cronjob | default dict }}
  {{- $index := .index }}
  {{- if $cronjob.serviceAccount }}
    {{- if $cronjob.serviceAccount.create }}
      {{- default (include "charts-cron-job.fullname" (dict "root" $root "cronjob" $cronjob "index" $index)) $cronjob.serviceAccount.name }}
    {{- else }}
      {{- default "default" $cronjob.serviceAccount.name }}
    {{- end }}
  {{- else if $root.Values.global.serviceAccount.create }}
    {{- default (include "charts-cron-job.fullname" $root) $root.Values.global.serviceAccount.name }}
  {{- else }}
    {{- default "default" $root.Values.global.serviceAccount.name }}
  {{- end }}
{{- else }}
  {{- /* Mode 2: Called with global cronjob context */ -}}
  {{- $root := . }}
  {{- if $root.Values.global.serviceAccount.create }}
    {{- default (include "charts-cron-job.fullname" $root) $root.Values.global.serviceAccount.name }}
  {{- else }}
    {{- default "default" $root.Values.global.serviceAccount.name }}
  {{- end }}
{{- end }}
{{- end }}
