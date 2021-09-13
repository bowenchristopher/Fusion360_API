#Author-Bowen Christopher 
#Description-Fusion 360 Parameters with Logical operators allowed in comments 

import adsk.core, adsk.fusion, adsk.cam, traceback, csv, time, datetime, os

_commandId = 'Parameteric Plugin'
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
        commandName = 'Parameter Plugin'
        commandDescription = 'Adds Executed Logic to Fusion 360 Parameter Comments\n'
        commandResources = './resources/command'

        app = adsk.core.Application.get()
        ui = app.userInterface

        class designParam:
            def __init__(self, ids, param, comment):
                self.ids = ids
                self.param = param
                self.comment = comment 


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
            # ui.messageBox("Weidmann Automation added to the Modify Panel")

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
    # update Model Parametric
    app = adsk.core.Application.get()
    ui = app.userInterface
    try: 
        document = app.activeDocument
        design = document.design

        # Get Assigned User Parameters
        userParams = False 
        userParams = design.userParameters 

        if userParams: 
            x = len(params) 
            y = len(comments)
            if ( x == y):
                for parameter in userParams: 
                    if (len(parameter.comment)>0):
                        i = params.index(parameter.name)

                        value  = (values[i]).split(' ')
                        # remove units from parameter value 
                        value = value[0]
                        test = cleanComment(params[i],comments[i],value)
                        userParams.itemByName(parameter.name).expression = str(test)
        
    except: 
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc())) 

def cleanComment(name,comment,value):
    # update Model Parametric
    app = adsk.core.Application.get()
    ui = app.userInterface
    try:  

        # List of restricted words 
        # This exists to make exec safer 
        restricted_syntax = ['as','assert','break','class','continue','def','del','except','for','from','global','lambda','None','nonlocal','return','try','with','yield','open','import','exec','eval']
                     
        if (';' in comment or ':' in comment or ' '):
            # Replace semi colons with newline characters to make python syntax right
            comment = comment.replace(";", "\n")
            
            # This is a soft limit, 
            if(len(comment) < 128):
                exist = False
                for word in restricted_syntax:
                    if (word in comment):
                        message = word + ' is not allowed syntax'
                        return(value)
                if (not exist):
                    return(execComment(name,str(comment),value))
            else:
                message = 'expressions cannot excede 128 characters'
        
        # ui.messageBox(message)
    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))  

def execComment(name,comment,value):
    app = adsk.core.Application.get()
    ui = app.userInterface
    try: 
        # append parametric variable to the front of the comment so it can be used in the equation 
        insert = str(name+'='+value+"\n")

        comment = insert+comment

        loc = {}
        try:
            exec(comment, globals(), loc)
            return_workaround = loc[name]
            return(str(return_workaround))
        except:
            ui.messageBox('Python Syntax issue Found \n'+str(comment))
            return value
    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc())) 