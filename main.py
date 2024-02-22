import ifcopenshell


def read_file():
    """
    Read user defined IFC-file.
    
    returns openned IFC-file if successful.
    """
    filePath = input("Enter path to IFC-file (or drag-and-drop): ")

    try:
        model = ifcopenshell.open(filePath)
        return model
    except IOError:
        print("Could not open ", filePath)
        return 0
