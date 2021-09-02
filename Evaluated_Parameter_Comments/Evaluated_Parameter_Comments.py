#Author-Bowen Christopher 
#Description-This script adds the ability to evaluate logical operators added to the comment of a Fusion 360 Parameter
#
# Example parameter comment:
# if OD_IN >7:; OD_IN = OD_IN;else:; OD_IN=11; 
#
# the line will be evaluated as 
# OD_IN =3
# if OD_IN >7:
#  OD_IN= OD_IN
# else:
#  OD_IN=11
#
# Notes:
# Semicolons are used to end lines and are replaced with a new line character,
# All expressions are evaluated using python syntax so spacing needs to be consistent 


import adsk.core, adsk.fusion, adsk.cam, traceback

def run(context):
    ui = None
    try:

        app = adsk.core.Application.get()
        ui  = app.userInterface   
        
        # Get the active document
        document = app.activeDocument

        # Get the active design 
        design = document.design

        # Get the design parameters 
        userParams = design.userParameters 
        
        def cleanComment(name,comment,value):
            # The exec command is inherently dangerous but useful in this case 
            # This list of restricted syntax exists to make the command safer but not perfectly safe
            restricted_syntax = ['as','assert','break','class','continue','def','del','except','for','from','global','lambda','None','nonlocal','return','try','with','while','yield','open','import','eval','exec','os.']
            
            # All comments that can be executed will contain either a : or ; 
            if (';' in comment or ':' in comment):
                # Replace semi colons with new line characters to convert to python syntax
                comment = comment.replace(";", "\n")
                exist = False

                for word in restricted_syntax:
                    if (word in comment.lower()):
                        ui.messageBox(word + ' is not allowed syntax')
                        exist = True
                        return(value)

                if (not exist):
                    return(execComment(name,str(comment),value))
            else: 
                ui.messageBox('Syntax issue found operation missing required syntax : or ;')


        def execComment(name,comment,value):
            # Append parametric variables name and value to the front of the comment so it can be passed to the expression 
            insert = str(name+'='+value+"\n")
            comment = insert+comment
            loc = {}
            try:
                # Creates a global variable to get return variable from executed comment 
                exec(comment, globals(), loc)
                return_val = str(loc[name])
                return(return_val)
            except:
                ui.messageBox('Python Syntax issue Found \n'+str(comment))
                return value

        
        # If design contains user parameters 
        if userParams: 
            for parameter in userParams: 
                if (len(parameter.comment)>0):
                    
                    # A parameter contans both value and unit
                    value  = (parameter.expression).split(' ')
                    
                    # Strip unit from parameter 
                    value = value[0]

                    # Clean comment before its executed  
                    exec_param = cleanComment(parameter.name,str(parameter.comment),value)

                    # Set design parameter to result of evaluated expression 
                    userParams.itemByName(parameter.name).expression = str(exec_param)
        else:
            ui.messageBox('Model does not contain user parameters')


    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
