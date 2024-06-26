cwlVersion: v1.0
class: CommandLineTool
baseCommand: run_analysis
inputs:
  config:
    type: File
    inputBinding:
      position: 1
  data:
    type: File
    inputBinding:
      position: 2
  optional_param:
    type: string?
    inputBinding:
      position: 3
outputs:
  report:
    type: stdout
stdout: report.txt
requirements:
  - class: EnvVarRequirement
    envDef:
      - envName: ANALYSIS_MODE
        envValue: "advanced"
  - class: InitialWorkDirRequirement
    listing:
      - entryname: "config_copy.txt"
        entry: $(inputs.config.path)
successCodes: [0]
temporaryFailCodes: [1]
permanentFailCodes: [2]
