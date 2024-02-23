import ifcopenshell
import ifcopenshell.util.element
import csv


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

def numOfPipeParts(model):
    """
    Read and count number of different pipe parts
    
    Parameters:
        model: model to be read
        
    Returns:
        dict: quantity of parts as {type (bends with angle) : {size : qty}}
    """
    parts = {}
    fittings = model.by_type("IfcPipeFitting")
    for item in model.by_type("IfcWasteTerminal"):
        fittings.append(item)
    for item in model.by_type("IfcSanitaryTerminal"):
        fittings.append(item)
    for item in model.by_type("IfcPump"):
        fittings.append(item)
    for item in model.by_type("IfcValve"):
        fittings.append(item)

    for fitting in fittings:
        name = fitting.Name
        if fitting.PredefinedType == "BEND":
            name = name + " " + ifcopenshell.util.element.get_pset(fitting, "FI_Geometria", prop="Kulma")
        size = ifcopenshell.util.element.get_pset(fitting, "FI_Geometria", prop="Liitoskoko (DN)")

        if name in parts:
            if size in parts[name]:
                parts[name][size] += 1
            else:
                parts[name].update({size : 1})
        else:
            parts.update({name : {size : 1}})
    
    return parts

def csvWriter():
    print("LVI-määrälaskenta IFC-mallista, dev.")
    model = read_file()
    if model == None:
        print("Mallia ei ole avattu, lopetetaan sovellus.")
        return
    
    pipeQty = pipe_meters(model)
    ductQty = duct_meters(model)
    ductParts = numOfDuctParts(model)
    pipeParts = numOfPipeParts(model)

    with open("quantities.csv", "w", newline="") as csvFile:
        writer = csv.writer(csvFile, delimiter=";")
        writer.writerow(["Tyyppi", "Koko", "Määrä", "Yks."])
        for type in pipeQty:
            for DN in pipeQty[type]:
                writer.writerow([type, DN, "{:.2f}".format(pipeQty[type][DN]), "m"])

        for type in ductQty:
            for size in ductQty[type]:
                writer.writerow([type, size, "{:.2f}".format(ductQty[type][size]), "m"])

        
        for part in ductParts:
            for size in ductParts[part]:
                writer.writerow([part, size, ductParts[part][size], "kpl"])

        for part in pipeParts:
            for size in pipeParts[part]:
                if size != None:
                    writer.writerow([part, size, pipeParts[part][size], "kpl"])
                else:
                    writer.writerow([part, "", pipeParts[part][size], "kpl"])
csvWriter()