bl_info = {
    "name": "Mario Kart 8 Course Info format",
    "description": "Import-Export Mario Kart 8 Course info",
    "author": "Syroot",
    "version": (0, 1, 0),
    "blender": (2, 75, 0),
    "location": "File > Import-Export",
    "warning": "This add-on is under development.",
    "wiki_url": "https://github.com/Syroot/io_scene_mk8muunt/wiki",
    "tracker_url": "https://github.com/Syroot/io_scene_mk8muunt/issues",
    "support": "COMMUNITY",
    "category": "Import-Export"
}

# Reload the classes when reloading add-ons in Blender with F8.
if "bpy" in locals():
    import importlib
    if "log" in locals():
        print("Reloading: " + str(log))
        importlib.reload(log)
    if "binary_io" in locals():
        print("Reloading: " + str(binary_io))
        importlib.reload(binary_io)
    if "byaml_file" in locals():
        print("Reloading: " + str(byaml_file))
        importlib.reload(byaml_file)
    if "importing" in locals():
        print("Reloading: " + str(importing))
        importlib.reload(importing)
    if "editing" in locals():
        print("Reloading: " + str(editing))
        importlib.reload(editing)
    if "exporting" in locals():
        print("Reloading: " + str(exporting))
        importlib.reload(exporting)

import bpy
from . import log
from . import binary_io
from . import byaml_file
from . import importing
from . import editing
from . import exporting

def register():
    bpy.utils.register_module(__name__)
    # Importing
    bpy.types.INFO_MT_file_import.append(importing.ImportOperator.menu_func_import)
    # Editing
    bpy.types.Scene.mk8       = bpy.props.PointerProperty(type=editing.MK8PropsScene)
    bpy.types.Scene.mk8course = bpy.props.PointerProperty(type=editing.MK8PropsSceneCourse)
    bpy.types.Object.mk8      = bpy.props.PointerProperty(type=editing.MK8PropsObject)
    bpy.types.Object.mk8obj   = bpy.props.PointerProperty(type=editing.MK8PropsObjectObj)
    # Exporting
    #bpy.types.INFO_MT_file_export.append(exporting.ExportOperator.menu_func_export)

def unregister():
    bpy.utils.unregister_module(__name__)
    # Importing
    bpy.types.INFO_MT_file_import.remove(importing.ImportOperator.menu_func_import)
    # Editing
    del bpy.types.Scene.mk8
    del bpy.types.Scene.mk8course
    del bpy.types.Object.mk8
    del bpy.types.Object.mk8obj
    # Exporting
    #bpy.types.INFO_MT_file_export.remove(exporting.ExportOperator.menu_func_export)

# Register classes of the add-on when Blender runs this script.
if __name__ == "__main__":
    register()
