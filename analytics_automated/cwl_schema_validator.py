import os
from cwltool.load_tool import fetch_document, resolve_and_validate_document
from cwltool.context import LoadingContext

class CWLSchemaValidator:
    def __init__(self):
        self.loading_context = LoadingContext()

    def validate_cwl(self, cwl_path):
        try:
            # Fetch the CWL document
            self.loading_context, workflowobj, uri = fetch_document(cwl_path, self.loading_context)

            # Validate the CWL document
            loading_context, uri = resolve_and_validate_document(
                self.loading_context,
                workflowobj,
                uri,
                preprocess_only=False
            )

            return True, "CWL file is valid."

        except Exception as e:
            return False, f"Validation failed: {str(e)}"
