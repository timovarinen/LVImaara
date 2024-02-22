import ifcopenshell
import ifcopenshell.util.element


def read_file():
    """
    Read user defined IFC-file.
    
    returns openned IFC-file if successful.
    """
    while True:
        filePath = input("Enter path to IFC-file (or drag-and-drop) (c to cancel): ")

        if filePath == "c":
            return None

        try:
            model = ifcopenshell.open(filePath)
            return model
        except IOError:
            print("Could not open ", filePath)
            continue

def pipe_meters(model):
    """
    Read and count pipe meters form model

    Parameters:
        model: model to be read

    Returns:
        dict: quantity of pipes as {type : {DN : qty}}
    """

    pipes = model.by_type("IfcPipeSegment")
    qty = {}

    for pipe in pipes:
        
        name = pipe.Name
        DN = ifcopenshell.util.element.get_pset(pipe, "FI_Geometria", prop="Koko (DN)")
        length = ifcopenshell.util.element.get_pset(pipe, "FI_Geometria", prop="Pituus") / 1000

        if name in qty:
            if DN in qty[name]:
                newLength = length + qty[name][DN]
                qty[name].update({DN : newLength})
            else:
                qty[name].update({DN : length})
        else:
            qty.update({name : {DN : length}})

    return qty

def ui():
    """
    Simple ui for testing of functions during development.
    """
    print("LVI-määrälaskenta IFC-mallista, dev.")
    model = read_file()
    if model == None:
        print("Mallia ei ole avattu, lopetetaan sovellus.")
        return
    
    pipeQty = pipe_meters(model)

    for type in pipeQty:
        print(type)
        for DN in pipeQty[type]:
            print("- DN" , DN, "{:.2f}".format(pipeQty[type][DN]), "m.")

    

ui()