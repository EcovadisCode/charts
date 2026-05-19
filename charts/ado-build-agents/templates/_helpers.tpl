{{/*
  anyEnabled:
  -----------
  This helper checks the `.enabled` field of each entry in a map (for example,
  `.Values.linuxSidecarContainers`) and returns the string "true" if *any* entry has
  `enabled: true`.

  Rationale
  -----------------------------------------
  If you enable any sidecar container in your values like:
    linuxSidecarContainers:
        docker:
            enabled: true
  it will conditionally add field initContainers: in template.
  It enables support for both cases, if your deployment require sidecars
  and deployment without them
*/}}
{{- define "anyEnabled" -}}
{{- $enabled := false -}}
{{- range $k, $v := . -}}
  {{- if $v.enabled }}{{- $enabled = true }}{{- end -}}
{{- end -}}
{{- if $enabled }}true{{ else }}false{{ end -}}
{{- end -}}