#Author-Bowen Christopher 
#Description-Fusion 360 Parameters with Logical operators evaluated in comments 

import adsk.core, adsk.fusion, adsk.cam, traceback, csv, time, datetime, os

_commandId = 'Parameter AddIn'
_workspaceToUse = 'FusionSolidEnvironment'
_panelToUse = 'SolidModifyPanel'

# global set of event handlers to keep them referenced for the duration of the command
_handlers = []

def commandDefinitionById(id):
    app = adsk.core.Application.get()
    ui = app.userInterface
    if not id:
        ui.messageBox('commandDefinition id is not specified')
        return None
    commandDefinitions = ui.commandDefinitions
    commandDefinition = commandDefinitions.itemById(id)
    return commandDefinition

def commandControlByIdForPanel(id):
    app = adsk.core.Application.get()
    ui = app.userInterface
    if not id:
        ui.messageBox('commandControl id is not specified')
        return None
    workspaces = ui.workspaces
    modelingWorkspace = workspaces.itemById(_workspaceToUse)
    toolbarPanels = modelingWorkspace.toolbarPanels
    toolbarPanel = toolbarPanels.itemById(_panelToUse)
    toolbarControls = toolbarPanel.controls
    toolbarControl = toolbarControls.itemById(id)
    return toolbarControl

def destroyObject(uiObj, tobeDeleteObj):
    if uiObj and tobeDeleteObj:
        if tobeDeleteObj.isValid:
            tobeDeleteObj.deleteMe()
        else:
            uiObj.messageBox('tobeDeleteObj is not a valid object')

def run(context):
    ui = None
    try:
        commandName = 'Parameter AddIn'
        commandDescription = 'Adds Executed Logic to Fusion 360 Parameter Comments\n'
        commandResources = './resources/command'

        app = adsk.core.Application.get()
        ui = app.userInterface

        class CommandExecuteHandler(adsk.core.CommandEventHandler):
            def __init__(self):
                super().__init__()
            def notify(self, args):
                try:
                    cmd = args.command
                    inputs = cmd.commandInputs
                    
                    document = app.activeDocument
                    design = document.design
                    
                    # Get Assigned User Parameters 
                    userParams = False
                    userParams = design.userParameters 
                    
                    # create parameter list 
                    params = []
                    values = [] 
                    comments = []

                    if userParams: 
                        for input in inputs: 
                            for parameter in userParams:
                                if input.id == str(parameter.name):
                                    params.append(str(input.id))
                                    values.append(str(input.value))
                                if input.id == str(parameter.name)+'_comment':
                                    comments.append(str(input.value))
                        
                        updateModel(params,values,comments)

                except:
                    if ui:
                        ui.messageBox('command executed failed:\n{}'.format(traceback.format_exc()))

        class CommandCreatedHandler(adsk.core.CommandCreatedEventHandler):
            def __init__(self):
                super().__init__() 
            def notify(self, args):
                try:
                    cmd = args.command
                    #cmd.helpFile = 'help.html'

                    onExecute = CommandExecuteHandler()
                    cmd.execute.add(onExecute)
                    # keep the handler referenced beyond this function
                    _handlers.append(onExecute)

                    #define the inputs
                    inputs = cmd.commandInputs

                    document = app.activeDocument
                    design = document.design
                    userParams = False 
                    
                    # Get Assigned User Parameters 
                    userParams = design.userParameters 

                    if userParams: 
                        for parameter in userParams: 
                            inputs.addStringValueInput(str(parameter.name),str(parameter.name),parameter.expression)
                            inputs.addStringValueInput(str(parameter.name)+'_comment','Comment',parameter.comment)
                    else:
                         ui.messageBox('Model contains no user parameters')    
                except:
                    if ui:
                        ui.messageBox('Panel command created failed:\n{}'.format(traceback.format_exc()))

        commandDefinitions = ui.commandDefinitions

	# check if we have the command definition
        commandDefinition = commandDefinitions.itemById(_commandId)
        if not commandDefinition:
            commandDefinition = commandDefinitions.addButtonDefinition(_commandId, commandName, commandDescription, commandResources)		 

        onCommandCreated = CommandCreatedHandler()
        commandDefinition.commandCreated.add(onCommandCreated)
        # keep the handler referenced beyond this function
        _handlers.append(onCommandCreated)
        
        # add a command on create panel in modeling workspace
        workspaces = ui.workspaces
        modelingWorkspace = workspaces.itemById(_workspaceToUse)
        toolbarPanels = modelingWorkspace.toolbarPanels
        toolbarPanel = toolbarPanels.itemById(_panelToUse) 
        toolbarControlsPanel = toolbarPanel.controls
        toolbarControlPanel = toolbarControlsPanel.itemById(_commandId)

        if not toolbarControlPanel:
            toolbarControlPanel = toolbarControlsPanel.addCommand(commandDefinition, '')
            toolbarControlPanel.isVisible = True
            ui.messageBox("Parameter Add-in added to the Modify Panel")

    except:
        if ui:
            ui.messageBox('AddIn Start Failed:\n{}'.format(traceback.format_exc()))

def stop(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface
        objArray = []

        commandControlPanel = commandControlByIdForPanel(_commandId)
        if commandControlPanel:
            objArray.append(commandControlPanel)
            
        commandDefinition = commandDefinitionById(_commandId)
        if commandDefinition:
            objArray.append(commandDefinition)

        for obj in objArray:
            destroyObject(ui, obj)

    except:
        if ui:
            ui.messageBox('AddIn Stop Failed:\n{}'.format(traceback.format_exc()))

def updateModel(params,values,comments):
    # update model parametric
    app = adsk.core.Application.get()
    ui = app.userInterface
    try: 
        document = app.activeDocument
        design = document.design
        
        #variable insert string to add previous parameters to evaluated comments 
        insert = ""

        # get assigned user parameters
        userParams = False 
        userParams = design.userParameters 
        # if design contains user params attempt to update
        if userParams: 
            # make sure number of comments is equal to number of parameters 
            if (len(params) == len(comments)):
                for parameter in userParams: 
                    i = params.index(parameter.name)
                    # remove units from parameter value 
                    value  = (values[i]).split(' ')
                    value = value[0]

                    if (len(parameter.comment)>0):
                        # clean and run the comment 
                        test = cleanComment(params[i],comments[i],value,insert)
                        value = str(test)

                    # supress feature if the parameter value is 0 
                    if (value =='0'):
                        userParams.itemByName(parameter.name).isSuppressed = True
                    else:
                        userParams.itemByName(parameter.name).expression = value

                    insert = insert + str(parameter.name+'='+value+"\n")

    except: 
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc())) 

def cleanComment(name,comment,value,insert):
    app = adsk.core.Application.get()
    ui = app.userInterface
    try:  
        # this list of restricted syntax exists to make the exec command safer
        restricted_syntax = ['as','assert','break','class','continue','def','del','except','for','from','global','lambda','None','nonlocal','return','try','with','while','yield','open','import','eval','exec','os.']
        # all comments that can be executed will contain either a : or ; 
        if (';' in comment or ':' in comment):
            # replace semicolons with new line characters to convert to Python syntax
            comment = comment.replace(";", "\n")
            safe = True

            for word in restricted_syntax:
                if (word in comment.lower()):
                    safe = False
                    ui.messageBox(word + ' is unsafe syntax')
                    
            if (safe):
                value = execComment(name,str(comment),value,insert)

            return(value)    
    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))  
            
def execComment(name,comment,value,insert):
    app = adsk.core.Application.get()
    ui = app.userInterface
    try: 
        # append parametric variables name and value to the front of the comment so it can be passed to the expression 
        val = name+'='+value+"\n"
        comment = val+insert+comment
        loc = {}
        try:
            # creates a global variable to get return variable from executed comment 
            exec(comment, globals(), loc)
            return_val = str(loc[name])
            return(return_val)
        except:
            ui.messageBox('Python Syntax issue Found \n'+str(comment))
            return value
    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc())) 
