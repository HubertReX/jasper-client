# -*- coding: utf-8 -*-
# a może teraz?
import os
import sys
import string
from traceback import format_exception


def listf(data):
	buffer = ""
	for line in data:
		buffer = buffer + line + "\n"
	return buffer

def recompile(modulename):
    """
    first, see if the module can be imported at all...
    """
    try:
        tmp = __import__(modulename)
    except Exception:
        return "Couldn't import module " + modulename +"\r\n" + listf(format_exception(sys.exc_type, sys.exc_value, sys.exc_traceback))

    """
    Use the imported module to determine its actual path
    """
    pycfile = tmp.__file__
    modulepath = string.replace(pycfile, ".pyc", ".py")
    
    """
    Try to open the specified module as a file
    """
    try:
        code=open(modulepath, 'rU').read()
    except Exception:
        return "Error opening file: " + modulepath + ".  Does it exist?"

    """
    see if the file we opened can compile.  If not, return the error that it gives.
    if compile() fails, the module will not be replaced.
    """
    try:
        compile(code, modulename, "exec")
    except Exception:
       return "Error in compilation: " + str(sys.exc_info()[0]) +"\r\n"  + listf(format_exception(sys.exc_type, sys.exc_value, sys.exc_traceback)) 
    else:
        """
        Ok, it compiled.  But will it execute without error?
        """
        try:
            execfile(modulepath)
        except Exception:
            return "Error in execution: " + str(sys.exc_info()[0]) +"\r\n" + listf(format_exception(sys.exc_type, sys.exc_value, sys.exc_traceback)) 
        else:
            """
            at this point, the code both compiled and ran without error.  Load it up
            replacing the original code.
            """
            try:
              reload( sys.modules[modulename] )
            except Exception:
              return "Error in reload: " + str(sys.exc_info()[0]) +"\r\n" + listf(format_exception(sys.exc_type, sys.exc_value, sys.exc_traceback))
            
    return "ok" #Error("Module successfully recompiled", True)
