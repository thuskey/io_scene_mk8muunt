import bpy
from bpy.props import BoolProperty, CollectionProperty, EnumProperty, FloatProperty, IntProperty
from . import addon
from . import objflow

# ==== Scene ===========================================================================================================

class MK8PropsScene(bpy.types.PropertyGroup):
    scene_type = EnumProperty(name="Scene Type", description="Specifies what kind of game content this scene represents.", items=(
        ("NONE",   "None",   "Do not handle this scene as game content."),
        ("COURSE", "Course", "Handle this scene as a race track.")))

    # ---- Course ----

    effect_sw      = IntProperty (name="EffectSW")
    head_light     = EnumProperty(name="Headlights", description="Controls how headlights are turned on and off throughout the course.", items=(
        ("OFF",     "Always Off",  "Headlights are turned off, ignoring any lap path specific settings."),
        ("ON",      "Always On",   "Headlights are turned on, ignoring any lap path specific settings."),
        ("PARTIAL", "By Lap Path", "Headlights are controlled by the lap path.")))
    is_first_left  = BoolProperty(name="First Curve Left", description="Optimizes game behavior if the first curve after the start turns left.")
    is_jugem_above = BoolProperty(name="Lakitu Above")
    jugem_above    = IntProperty (name="Lakitu Above")
    lap_jugem_pos  = IntProperty (name="Lap Lakitu Pos.")
    lap_number     = IntProperty (name="Lap Number",       description="The number of total laps which have to be driven to finish this track.", min=0, max=7, default=3)
    pattern_num    = IntProperty (name="Pattern Num.")

    obj_prm_1   = IntProperty(name="Param 1")
    obj_prm_2   = IntProperty(name="Param 2")
    obj_prm_3   = IntProperty(name="Param 3")
    obj_prm_4   = IntProperty(name="Param 4")
    obj_prm_5   = IntProperty(name="Param 5")
    obj_prm_6   = IntProperty(name="Param 6")
    obj_prm_7   = IntProperty(name="Param 7")
    obj_prm_8   = IntProperty(name="Param 8")

    obj_prms_expanded = BoolProperty(name="Obj Params", description="Expand the Obj Params section or collapse it.")

# ---- UI ----

class MK8PanelScene(bpy.types.Panel):
    bl_label       = "Mario Kart 8"
    bl_space_type  = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context     = "scene"

    @classmethod
    def poll(cls, context):
        return True

    def draw(self, context):
        mk8 = context.scene.mk8
        self.layout.prop(mk8, "scene_type")
        self.layout.separator()
        if mk8.scene_type == "COURSE": self.draw_scene(context, mk8)

    def draw_scene(self, context, mk8):
        self.layout.prop(mk8, "lap_number")
        self.layout.prop(mk8, "head_light")
        row = self.layout.row()
        row.prop(mk8, "is_jugem_above")
        row.prop(mk8, "jugem_above")
        row = self.layout.row()
        row.prop(mk8, "is_first_left")
        row.prop(mk8, "lap_jugem_pos")
        row = self.layout.row()
        row.prop(mk8, "effect_sw")
        row.prop(mk8, "pattern_num")
        # Obj Parameters
        box = self.layout.mk8_colbox(mk8, "obj_prms_expanded")
        if mk8.obj_prms_expanded:
            row = box.row()
            row.prop(mk8, "obj_prm_1")
            row.prop(mk8, "obj_prm_2")
            row = box.row()
            row.prop(mk8, "obj_prm_3")
            row.prop(mk8, "obj_prm_4")
            row = box.row()
            row.prop(mk8, "obj_prm_5")
            row.prop(mk8, "obj_prm_6")
            row = box.row()
            row.prop(mk8, "obj_prm_7")
            row.prop(mk8, "obj_prm_8")


# ==== Object ==========================================================================================================

class MK8PropsObjectAreaCameraArea(bpy.types.PropertyGroup):
    value = bpy.props.IntProperty(name="Camera Area", min=0)

class MK8PropsObject(bpy.types.PropertyGroup):
    def update(self, context):
        ob = context.object
        if ob and ob.type == "MESH":
            if   self.object_type == "NONE":       ob.data = None # Does not seem to have an effect.
            elif self.object_type == "AREA":       self.update_area(context, ob)
            elif self.object_type == "CLIPAREA":   self.update_clip_area(context, ob)
            elif self.object_type == "EFFECTAREA": self.update_effect_area(context, ob)
            elif self.object_type == "OBJ":        self.update_obj(context, ob)

    # ---- Generic ----

    object_type   = EnumProperty(name="Object Type", description="Specifies what kind of course content this object represents.", update=update, items=(
        ("NONE",       "None",        "Do not handle this object as course content."),
        ("AREA",       "Area",        "Handle this object as an area."),
        ("CLIPAREA",   "Clip Area",   "Handle this object as a clip area"),
        ("EFFECTAREA", "Effect Area", "Handle this object as an effect area"),
        ("OBJ",        "Obj",         "Handle this object as a course object.")))
    index         = IntProperty  (name="Index",   description="The array index this object will have when exporting.",                  min=-1, default=-1)
    unit_id_num   = IntProperty  (name="Unit ID", description="Seems to have been an internal editor ID, but no longer has an effect.", min=0)
    float_param_1 = FloatProperty(name="Param 1")
    float_param_2 = FloatProperty(name="Param 2")
    float_param_3 = FloatProperty(name="Param 3")
    float_param_4 = FloatProperty(name="Param 4")
    float_param_5 = FloatProperty(name="Param 5")
    float_param_6 = FloatProperty(name="Param 6")
    float_param_7 = FloatProperty(name="Param 7")
    float_param_8 = FloatProperty(name="Param 8")

    # ---- Area ----

    def update_area(self, context, ob):
        ob.data = addon.get_default_mesh(ob.mk8.area_shape)
        ob.draw_type = "WIRE"

    area_shape = EnumProperty(name="Shape", description="Specifies the outer form of the region this area spans.", update=update, items=(
        ("AREACUBE",   "Cube",   "The area spans a cuboid region."),
        ("AREASPHERE", "Sphere", "The area spans a spherical region.")))
    area_type  = EnumProperty(name="Type",  description="Specifies the action taken for objects inside of this region.", items=(
        ("NONE",     "None",        "No special action will be taken."),
        ("UNKNOWN1", "Unknown (1)", "Unknown area type. Appears in Mario Circuit and Twisted Mansion."),
        ("UNKNOWN2", "Unknown (2)", "Unknown area type. Appears almost everywhere."),
        ("PULL",     "Pull",        "Objects are moved along the specified path."),
        ("UNKNOWN4", "Unknown (4)", "Unknown area type. Appears in Mario Kart Stadium, Royal Raceway and Animal Crossing.")))
    area_path      = IntProperty(name="Path",      min=0)
    area_pull_path = IntProperty(name="Pull Path", min=0)
    camera_areas   = CollectionProperty(type=MK8PropsObjectAreaCameraArea)

    camera_areas_active = bpy.props.IntProperty(
    )

    # ---- Clip Area ----

    def update_clip_area(self, context, ob):
        ob.data = addon.get_default_mesh(self.area_shape)
        ob.draw_type = "WIRE"

    clip_area_shape = EnumProperty(name="Shape", description="Specifies the outer form of the region this clip area spans.", update=update, items=(
        ("AREACUBE", "Cube",        "The clip area spans a cuboid region."),))
    clip_area_type  = EnumProperty(name="Type",  items=(
        ("UNKNOWN5", "Unknown (5)", "Unknown clip area type. Appears almost everywhere."),))

    # ---- Effect Area ----

    def update_effect_area(self, context, ob):
        ob.data = addon.get_default_mesh("AREACUBE")
        ob.draw_type = "WIRE"

    effect_sw = IntProperty(name="EffectSW", min=0)

    # ---- Obj ----

    def update_obj(self, context, ob):
        ob.data = None
        ob.empty_draw_type = "PLAIN_AXES"
        ob.empty_draw_size = 20

    def obj_id_enum_items(self, context):
        return objflow.get_id_label_items()

    # General
    obj_id   = IntProperty  (name="Obj ID",          description="The ID determining the type of this object (as defined in objflow.byaml).", min=1000, max=9999, update=update)
    multi_2p = BoolProperty (name="Exclude 2P",      description="Removes this obj in 2 player offline games.")
    multi_4p = BoolProperty (name="Exclude 4P",      description="Removes this obj in 4 player offline games.")
    wifi     = BoolProperty (name="Exclude WiFi",    description="Removes this obj in online games.")
    wifi_2p  = BoolProperty (name="Exclude WiFi 2P", description="Removes this obj in 2 player online games.")
    no_col   = BoolProperty (name="No Collisions",   description="Removes collision detection with this object when set.")
    top_view = BoolProperty (name="Top View")
    # Relations
    has_obj_obj = BoolProperty(name="Has Related Obj", description="Determines whether this Obj has relations to another.")
    obj_obj     = IntProperty (name="Related Obj",     description="The index of the Obj this Obj has relations to.")
    # Paths
    speed                = FloatProperty(name="Speed",              description="The speed in which the obj follows its path.")
    has_obj_path         = BoolProperty (name="Has Path",           description="Determines whether a Path will be used.")
    has_obj_path_point   = BoolProperty (name="Has Path Point",     description="Determines whether a Path Point will be used.")
    has_obj_obj_path     = BoolProperty (name="Has Obj Path",       description="Determines whether an Obj Path will be used.")
    has_obj_obj_point    = BoolProperty (name="Has Obj Path Point", description="Determines whether an Obj Path Point will be used.")
    has_obj_enemy_path_1 = BoolProperty (name="Has Enemy Path 1",   description="Determines whether an Enemy Path 1 will be used.")
    has_obj_enemy_path_2 = BoolProperty (name="Has Enemy Path 2",   description="Determines whether an Enemy Path 2 will be used.")
    has_obj_item_path_1  = BoolProperty (name="Has Item Path 1",    description="Determines whether an Item Path 1 will be used.")
    has_obj_item_path_2  = BoolProperty (name="Has Item Path 2",    description="Determines whether an Item Path 2 will be used.")
    obj_path             = IntProperty  (name="Path",               description="The index of the path this obj follows.", min=0)
    obj_path_point       = IntProperty  (name="Path Point",         min=0)
    obj_obj_path         = IntProperty  (name="Obj",                min=0)
    obj_obj_point        = IntProperty  (name="Obj Point",          min=0)
    obj_enemy_path_1     = IntProperty  (name="Enemy 1",            min=0)
    obj_enemy_path_2     = IntProperty  (name="Enemy 2",            min=0)
    obj_item_path_1      = IntProperty  (name="Item 1",             min=0)
    obj_item_path_2      = IntProperty  (name="Item 2",             min=0)
    # UI
    obj_id_enum         = EnumProperty(items=obj_id_enum_items)
    params_expanded     = BoolProperty(name="Params",     description="Expand the Params section or collapse it.",     default=True)
    paths_expanded      = BoolProperty(name="Paths",      description="Expand the Paths section or collapse it.",      default=True)
    exclusions_expanded = BoolProperty(name="Exclusions", description="Expand the Exclusions section or collapse it.", default=False)

# ---- Operators ----

class MK8OperatorObjectObjIDSearch(bpy.types.Operator):
    bl_idname   = "object.mk8muunt_obj_id_search"
    bl_label    = "Obj ID Search"
    bl_property = "obj_ids"

    obj_ids = MK8PropsObject.obj_id_enum

    def execute(self, context):
        context.object.mk8.obj_id = int(self.obj_ids)
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.invoke_search_popup(self)
        return {'FINISHED'}

# ---- UI ----

class MK8PanelObject(bpy.types.Panel):
    bl_label       = "Mario Kart 8"
    bl_space_type  = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context     = "object"

    @classmethod
    def poll(cls, context):
        return bool(context.object)

    def draw(self, context):
        mk8 = context.object.mk8
        self.layout.prop(mk8, "object_type")
        # Generic properties.
        if mk8.object_type != "NONE":
            row = self.layout.row()
            row.prop(mk8, "index")
            row.prop(mk8, "unit_id_num")
            # Type specific properties.
            self.layout.separator()
            if   mk8.object_type == "AREA":       self.draw_area(context, mk8)
            elif mk8.object_type == "CLIPAREA":   self.draw_clip_area(context, mk8)
            elif mk8.object_type == "EFFECTAREA": self.draw_effect_area(context, mk8)
            elif mk8.object_type == "OBJ":        self.draw_obj(context, mk8)

    def draw_area(self, context, mk8):
        row = self.layout.row(align=True)
        row.prop(mk8, "float_param_1")
        row.prop(mk8, "float_param_2")
        self.layout.prop(mk8, "area_shape")
        # Area Type
        self.layout.prop(mk8, "area_type")
        if mk8.area_type == "UNKNOWN2":
            self.layout.prop(mk8, "area_path")
        elif mk8.area_type == "PULL":
            self.layout.prop(mk8, "area_pull_path")
        # Camera Areas
        self.layout.label("Camera Areas")
        self.layout.template_list("MK8ListObjectAreaCameraArea", "", mk8, "camera_areas", mk8, "camera_areas_active")

    def draw_clip_area(self, context, mk8):
        row = self.layout.row(align=True)
        row.prop(mk8, "float_param_1")
        row.prop(mk8, "float_param_2")
        self.layout.prop(mk8, "clip_area_type")

    def draw_effect_area(self, context, mk8):
        row = self.layout.row(align=True)
        row.prop(mk8, "float_param_1")
        row.prop(mk8, "float_param_2")
        self.layout.prop(mk8, "effect_sw")

    def draw_obj(self, context, mk8):
        def optional_prop(layout, path):
            # Checkbox
            row = layout.row(align=True)
            row.prop(mk8, "has_" + path, text="")
            # Property
            sub = row.row(align=True)
            sub.active = getattr(mk8, "has_" + path)
            sub.prop(mk8, path)
            return sub

        # Obj ID
        split = self.layout.split(0.5)
        col = split.column()
        row = col.row(align=True)
        row.operator("object.mk8muunt_obj_id_search", text="", icon="MESH_CUBE")
        row.prop(mk8, "obj_id")
        col = split.column()
        obj_name = objflow.get_obj_label(context, mk8.obj_id)
        if obj_name:
            col.label(obj_name, icon="FORWARD")
        else:
            col.label("Unknown", icon="ERROR")
        # Relations
        col = self.layout.column_flow(2)
        row = col.row()
        optional_prop(row, "obj_obj")
        # Other
        row = col.row()
        row.prop(mk8, "no_col")
        row.prop(mk8, "top_view")
        # Obj Params
        box = self.layout.mk8_colbox(mk8, "params_expanded")
        if mk8.params_expanded:
            row = box.row()
            row.prop(mk8, "float_param_1")
            row.prop(mk8, "float_param_2")
            row = box.row()
            row.prop(mk8, "float_param_3")
            row.prop(mk8, "float_param_4")
            row = box.row()
            row.prop(mk8, "float_param_5")
            row.prop(mk8, "float_param_6")
            row = box.row()
            row.prop(mk8, "float_param_7")
            row.prop(mk8, "float_param_8")
        # Paths
        box = self.layout.mk8_colbox(mk8, "paths_expanded")
        if mk8.paths_expanded:
            row = box.row()
            row.prop(mk8, "speed")
            row = box.row()
            optional_prop(row, "obj_path")
            optional_prop(row, "obj_path_point")
            row = box.row()
            optional_prop(row, "obj_obj_path")
            optional_prop(row, "obj_obj_point")
            row = box.row()
            optional_prop(row, "obj_enemy_path_1")
            optional_prop(row, "obj_enemy_path_2")
            row = box.row()
            optional_prop(row, "obj_item_path_1")
            optional_prop(row, "obj_item_path_2")
        # Exclusions
        box = self.layout.mk8_colbox(mk8, "exclusions_expanded")
        if mk8.exclusions_expanded:
            row = box.row(align=True)
            row.prop(mk8, "multi_2p")
            row.prop(mk8, "multi_4p")
            row = box.row(align=True)
            row.prop(mk8, "wifi")
            row.prop(mk8, "wifi_2p")

class MK8ListObjectAreaCameraArea(bpy.types.UIList):
    layout_type = "GRID"

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        if self.layout_type == "GRID":
            layout.alignment = "CENTER"
        layout.label(str(item.value), icon="CAMERA_DATA")
