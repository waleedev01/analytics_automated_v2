# test_import.py
try:
    from cwl_utils.parser import cwl_v1_2
    print("Import successful")
except ModuleNotFoundError as e:
    print(f"Import failed: {e}")
