# Standard Autodesk Libraries
import adsk.core, adsk.fusion

# Standard Python Libraries
import traceback, random, time, os

# Global variable definition
numComponents = 3

minSizeWidth = 1000
minSizeHeight = 1000
minPartThickness = 10
minHoleDiameter = int(minSizeHeight / 30)

maxHoleDiameter = int(minSizeHeight / 3)
maxSizeWidth = 10000
maxSizeHeight = 10000
maxPartThickness = 1000

# Number to start with for naming of files
startName = 1


'''
# Creating debug dialog
app = adsk.core.Application.get()
ui  = app.userInterface
ui.messageBox('Hello script')
'''

def run(context):

    global startName

    ui = None
    
    # Find current time for determining runtime
    t0 = time.time()

    try:

        # get active design        
        app = adsk.core.Application.get()
        ui = app.userInterface
        product = app.activeProduct
        design = adsk.fusion.Design.cast(product)
        
        # Get the root component of the active design
        rootComp = design.rootComponent

        # get the script location
        scriptDir = os.path.dirname(os.path.realpath(__file__)) + '/data' 
        # create a single exportManager instance
        exportMgr = design.exportManager

        for i in range(numComponents):
            comp = createComponent(rootComp, app, ui, product, design)
            # Save the 3D information
            save3D(app, ui, product, design, scriptDir, exportMgr, startName, comp)
            # TODO: Generate Drawings
            # TODO: Save darwings
            
            # Delete the component
            delComponent(rootComp, app, ui, product, design, comp)


            # Tick startName up one
            startName += 1
            

        timeToRun = time.time() - t0
        ui.messageBox(f'time to run: {timeToRun/60} minutes for {numComponents} parts for {numComponents/timeToRun*60} parts per minute')

    except:
        if ui:

            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

def delComponent(rootComp, app, ui, product, design, comp):

    # Build a list of unique immediate occurrences of the component.
    occurrences = rootComp.allOccurrencesByComponent(comp)
    for o in occurrences:
        o.deleteMe()



def save3D(app, ui, product, design, scriptDir, exportMgr, startName, comp):
        ''' export the component one by one with a specified format '''

        '''
        # Moved away from this naming schele by using startName instead
         compName = comp.name
        '''

        fileNameF3D = scriptDir + "/f3d/" + str(startName)
        fileNameSTP = scriptDir + "/stp/" + str(startName)

        '''
        # export the component with SAT format
        satOptions = exportMgr.createSATExportOptions(fileName, comp)
        exportMgr.execute(satOptions)
        '''
        # export the component with F3D format
        archOptions = exportMgr.createFusionArchiveExportOptions(fileNameF3D, comp)
        exportMgr.execute(archOptions)
            
        # export the component with STP format
        stpOptions = exportMgr.createSTEPExportOptions(fileNameSTP, comp)
        exportMgr.execute(stpOptions)


def createComponent(rootComp, app, ui, product, design):
        ''' Create a component '''

        ## Grab global variables 
        global numComponents

        global minHoleDiameter
        global minSizeWidth
        global minSizeHeight
        global minPartThickness

        global maxHoleDiameter
        global maxSizeWidth
        global maxSizeHeight
        global maxPartThickness

        allOccs = rootComp.occurrences
        transform = adsk.core.Matrix3D.create()

        # Create a component under root component
        occ1 = allOccs.addNewComponent(transform)
        subComp1 = occ1.component
        print(subComp1.revisionId)

        # Create a sketch in sub component 1
        sketches1 = subComp1.sketches
        sketch1 = sketches1.add(rootComp.yZConstructionPlane)
        print(subComp1.revisionId)

        # Get sketch lines
        sketchLines = sketch1.sketchCurves.sketchLines

        ## Get sketch circles
        sketchCircles = sketch1.sketchCurves.sketchCircles

        # Create sketch rectangle
        ## Start rectangle from zero always (for project, assume 0,0,0 is refernece point and always exists)
        startX = 0
        startY = 0
        startZ = 0

        ## Create end point for rectangle and save to variables to use letter for hole generation
        endX = random.randrange(minSizeWidth, maxSizeWidth)
        endY = random.randrange(minSizeHeight, maxSizeHeight)
        endZ = 0

        ## Use the Autodesk F360 library for storing points as native 3D points. Don't have to do this for circle
        startPoint = adsk.core.Point3D.create(startX, startY, startZ)
        endPoint = adsk.core.Point3D.create(endX, endY, endZ)
        sketchLines.addTwoPointRectangle(startPoint, endPoint)
        print(subComp1.revisionId)

        # Create holes
        circles = sketch1.sketchCurves.sketchCircles

        # Generate random  number of holes
        numHoles = random.randrange(1,4)

        # Generate holder for holes
        circleList = []

        # Loop through number of holes and generate holes
        for i in range(numHoles):

            # Use existing rectangle dimensions to ensure holes are within part
            holeX = random.randrange(endX)
            holeY = random.randrange(endY)
            holeD = random.randrange(minHoleDiameter, maxHoleDiameter)

            cir = circles.addByCenterRadius(adsk.core.Point3D.create(holeX, holeY, 0), holeD)
            circleList.append(cir)


        # Get the profile of the first sketch
        prof1 = sketch1.profiles.item(0)

        # Create an extrusion input
        extrudes1 = subComp1.features.extrudeFeatures
        extInput1 = extrudes1.createInput(prof1, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)

        # Define that the extent is a distance extent of 2 cm
        distance1 = adsk.core.ValueInput.createByReal(random.randrange(minPartThickness, maxPartThickness))
        # Set the distance extent
        extInput1.setDistanceExtent(False, distance1)
        # Set the extrude type to be solid
        extInput1.isSolid = True

        # Create the extrusion
        ext1 = extrudes1.add(extInput1)
        print(subComp1.revisionId)


        return(subComp1)