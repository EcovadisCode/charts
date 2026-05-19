{{/*
Expand the name of the chart.
*/}}
{{- define "chart.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "chart.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "chart.labels" -}}
helm.sh/chart: {{ include "chart.name" . }}
{{ include "chart.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "chart.selectorLabels" -}}
app.kubernetes.io/name: {{ include "chart.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
This allows us to not have image: .Values.xxxx.ssss/.Values.xxx.xxx:.Values.ssss
in every single template.
*/}}
{{- define "broker.image" -}}
{{- .Values.broker.image -}}
{{- end -}}

{{/*
Return the Database Secret Name
*/}}
{{- define "broker.databaseSecretName" -}}
{{- if .Values.database.auth.existingSecret }}
    {{- .Values.database.auth.existingSecret -}}
{{- end -}}
{{- end -}}

{{/*
Return the databaseSecret key to retrieve credentials for database
*/}}
{{- define "broker.databaseSecretKey" -}}
{{- if .Values.database.auth.existingSecret -}}
    {{- .Values.database.auth.existingSecretPasswordKey -}}
{{- end -}}
{{- end -}}

{{/*
Create the name of the service account to use
*/}}
{{- define "broker.serviceAccountName" -}}
{{- if .Values.serviceAccount.create -}}
    {{ default (include "chart.fullname" .) .Values.serviceAccount.name }}
{{- else -}}
    {{ default "default" .Values.serviceAccount.name }}
{{- end -}}
{{- end -}}
