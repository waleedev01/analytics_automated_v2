#!/bin/bash

set -e

WORK_DIR="/path/to/your/workdir"

cd "$WORK_DIR"

WORKFLOWS=(
    "workflow1.cwl"
    "workflow2.cwl"
)

INPUTS=(
    "input1.json"
    "input2.json"
)

for i in "${!WORKFLOWS[@]}"; do
    WORKFLOW="${WORKFLOWS[$i]}"
    INPUT="${INPUTS[$i]}"

    if [ -z "$WORKFLOW" ] || [ -z "$INPUT" ]; then
        echo "empty, pass"
        continue
    fi

    echo "Executed cwltool comman： cwltool $WORKFLOW $INPUT"
    cwltool "$WORKFLOW" "$INPUT"
done

echo "All cwltool finish"
