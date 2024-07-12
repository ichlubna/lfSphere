import bpy
import bmesh
import mathutils
import math
import os

class LFPanel(bpy.types.Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_context = "objectmode"
    bl_category = "Lightfield"
    bl_label = "Generate lightfield array"

    def draw(self, context):
        col = self.layout.column(align=True) 
        col.prop(context.scene, "lfGrid")
        col.prop(context.scene, "lfDirection")
        col.operator("mesh.generate", text="Generate")
        if bpy.data.collections.get("LF_Cam"):
            col.operator("mesh.render", text="Render")

class LFArray(bpy.types.Operator):
    """ Generates the camera grid with given parameters.
    """
    bl_idname = "mesh.generate"
    bl_label = "Generate LF array"
    bl_options = {"UNDO"}

    def invoke(self, context, event):        
        collection = bpy.data.collections.get("LF_Cam")
        if collection:
            for object in collection.objects:
                bpy.data.objects.remove(object)
            bpy.data.collections.remove(collection)
             
        collection = bpy.data.collections.new("LF_Cam")
        bpy.context.scene.collection.children.link(collection)
    
        gridObj = context.scene.lfGrid
        nodeGroup = bpy.data.node_groups["LightFieldMesh"]
        modifier = gridObj.modifiers.new("LF", "NODES")
        #bpy.data.node_groups.remove(modifier.node_group)
        modifier.node_group = nodeGroup
        #material = bpy.data.materials.get("LightFieldProjector")
        #if gridObj.data.materials:
        #    gridObj.data.materials[0] = material
        #else:
        #    gridObj.data.materials.append(material)
        modifier = gridObj.modifiers.new("LFPROJ", "UV_PROJECT")
        modifier.projectors[0].object = bpy.context.scene.camera
            
        directionObj = context.scene.lfDirection
        mat = gridObj.matrix_world
        for v in gridObj.data.vertices:
            bpy.ops.object.camera_add(location=mat @ v.co)
            camera = context.object
            constraint = camera.constraints.new(type='TRACK_TO')
            constraint.target = directionObj
            camera.name = str(v.index)       
            camera.parent = gridObj
            camera.matrix_parent_inverse = gridObj.matrix_world.inverted()
            for coll in camera.users_collection:
                coll.objects.unlink(camera)
            collection.objects.link(camera)            
        return {"FINISHED"}

class LFRender(bpy.types.Operator):
    """ Renders the current frame.
        Takes format settings from Render options.
    """
    bl_idname = "mesh.render"
    bl_label = "Render LF"
    bl_descripiton = "Render all views to the output folder"

    def invoke(self, context, event):
        backupCam = bpy.context.scene.camera
        renderInfo = bpy.data.scenes["Scene"].render
        path = renderInfo.filepath[:]
        collection = bpy.data.collections.get("LF_Cam")
        for object in collection.objects:
            bpy.context.scene.camera = object
            renderInfo.filepath = path+"/"+str(object.name)
            bpy.ops.render.render(write_still=True) 
        renderInfo.filepath = path     
        bpy.context.scene.camera = backupCam
        return {"FINISHED"}

def register():
    bpy.utils.register_class(LFArray)
    bpy.utils.register_class(LFRender)
    bpy.utils.register_class(LFPanel)
    bpy.types.Scene.lfGrid = bpy.props.PointerProperty(name="Camera grid", description="Each vertex of this mesh is a camera", type=bpy.types.Object)
    bpy.types.Scene.lfDirection = bpy.props.PointerProperty(name="Camera direction", description="All cameras point here", type=bpy.types.Object)
    bpy.types.Scene.lfDepth = bpy.props.BoolProperty(name="Depth maps", description="Will render depth maps too", default=True)
    
def unregister():
    bpy.utils.unregister_class(LFArray)
    bpy.utils.unregister_class(LFRender)
    bpy.utils.unregister_class(LFPanel)
    del bpy.types.Scene.lfType 
    
if __name__ == "__main__" :
    register()