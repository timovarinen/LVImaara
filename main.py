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

def duct_meters(model):
    """
    Read and count duct meters form model

    Parameters:
        model: model to be read

    Returns:
        dict: quantity of ducts as {type : {diameter : qty}}
    """

    ducts = model.by_type("IfcDuctSegment")
    qty = {}

    for duct in ducts:
        
        name = duct.Name
        size = ifcopenshell.util.element.get_pset(duct, "FI_Geometria", prop="Koko (DU)")
        length = ifcopenshell.util.element.get_pset(duct, "FI_Geometria", prop="Pituus") / 1000

        if name in qty:
            if size in qty[name]:
                newLength = length + qty[name][size]
                qty[name].update({size : newLength})
            else:
                qty[name].update({size : length})
        else:
            qty.update({name : {size : length}})

    return qty

def numOfDuctParts(model):
    """
    Read and count number of different duct parts
    
    Parameters:
        model: model to be read
        
    Returns:
        dict: quantity of parts as {type (bends with angle) : {size : qty}}
    """
    parts = {}
    fittings = model.by_type("IfcDuctFitting")
    for item in model.by_type("IfcAirTerminal"):
        fittings.append(item)
    for item in model.by_type("IfcDuctSilencer"):
        fittings.append(item)
    for item in model.by_type("IfcFan"):
        fittings.append(item)
    for item in model.by_type("IfcDamper"):
        fittings.append(item)

    for fitting in fittings:
        name = fitting.Name
        if fitting.PredefinedType == "BEND":
            name = name + " " + ifcopenshell.util.element.get_pset(fitting, "FI_Geometria", prop="Kulma")
        size = ifcopenshell.util.element.get_pset(fitting, "FI_Geometria", prop="Liitoskoko (DU)")

        if name in parts:
            if size in parts[name]:
                parts[name][size] += 1
            else:
                parts[name].update({size : 1})
        else:
            parts.update({name : {size : 1}})
    
    return parts

def ui():
    """
    Simple ui for testing of functions during development.
    """
    print("LVI-määrälaskenta IFC-mallista, dev.")
    model = read_file()
    if model == None:
        print("Mallia ei ole avattu, lopetetaan sovellus.")
        return
    print("Komennot: 1 = näytä putkien pituudet, 2 = näytä kanavien pituudet, 3 = kanavaosat q = lopeta")
    
    while True:
        cmd = input("Komento: ")

        match cmd:
            case "1":   
                pipeQty = pipe_meters(model)

                for type in pipeQty:
                    print(type)
                    for DN in pipeQty[type]:
                        print("- DN", DN, "{:.2f}".format(pipeQty[type][DN]), "m")
            case "2":   
                ductQty = duct_meters(model)

                for type in ductQty:
                    print(type)
                    for size in ductQty[type]:
                        print("- koko", size, "mm {:.2f}".format(ductQty[type][size]), "m")
            case "3":
                ductParts = numOfDuctParts(model)

                for part in ductParts:
                    print(part)
                    for size in ductParts[part]:
                        print("- koko", size, ductParts[part][size], "kpl")
            case "q":
                return
            case _:
                print("Määrittelemätön komento")

ui()