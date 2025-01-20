import bpy
import bmesh
from mathutils import Vector

def get_mesh_islands(bm):
    """Find all vertex islands in the mesh using select linked."""
    bpy.ops.mesh.select_all(action='DESELECT')
    islands = []
    visited_verts = set()
    
    for vert in bm.verts:
        if vert.index not in visited_verts:
            vert.select = True
            bpy.ops.mesh.select_linked()
            island = [v for v in bm.verts if v.select]
            islands.append(island)
            visited_verts.update(v.index for v in island)
            bpy.ops.mesh.select_all(action='DESELECT')
    return islands

def calculate_average_distance(island, bone_center):
    """Calculate the average distance of all vertices in an island to the bone center."""
    total_distance = sum((vert.co - bone_center).length for vert in island)
    return total_distance / len(island)

def assign_vertex_groups(mesh_obj, armature_obj):
    if mesh_obj.type != 'MESH' or armature_obj.type != 'ARMATURE':
        print("Invalid selection. Requires a mesh and an armature.")
        return
    
    # Deselect all objects and select only the mesh
    bpy.ops.object.select_all(action='DESELECT')
    mesh_obj.select_set(True)
    bpy.context.view_layer.objects.active = mesh_obj

    # Ensure the mesh is in Edit mode
    bpy.ops.object.mode_set(mode='EDIT')
    
    # Create a bmesh from the mesh
    mesh = mesh_obj.data
    bm = bmesh.from_edit_mesh(mesh)
    
    # Calculate bone centers in the mesh's local space
    bone_centers = {}
    armature_world_matrix = armature_obj.matrix_world
    mesh_world_matrix_inv = mesh_obj.matrix_world.inverted()
    
    for bone in armature_obj.data.bones:
        # Transform bone center from armature local space to world space, then to mesh local space
        bone_center_world = armature_world_matrix @ ((bone.head_local + bone.tail_local) / 2)
        bone_center_mesh = mesh_world_matrix_inv @ bone_center_world
        bone_centers[bone.name] = bone_center_mesh
    
    # Find all mesh islands
    islands = get_mesh_islands(bm)
    
    # Determine best island for each bone
    bone_to_best_island = {}
    island_to_bone_distances = {}
    
    for bone_name, bone_center in bone_centers.items():
        best_island = None
        best_distance = float('inf')
        
        for island in islands:
            avg_distance = calculate_average_distance(island, bone_center)
            if avg_distance < best_distance:
                best_island = island
                best_distance = avg_distance
        
        if best_island:
            bone_to_best_island[bone_name] = tuple(v.index for v in best_island)
            island_to_bone_distances[bone_name] = best_distance
    
    # Resolve conflicts for shared islands
    island_assignment = {}
    
    for bone_name, best_island in bone_to_best_island.items():
        if best_island not in island_assignment:
            island_assignment[best_island] = (bone_name, island_to_bone_distances[bone_name])
        else:
            current_bone, current_distance = island_assignment[best_island]
            if island_to_bone_distances[bone_name] < current_distance:
                island_assignment[best_island] = (bone_name, island_to_bone_distances[bone_name])
    
    # Generate vertex groups for bones with assigned islands
    bpy.ops.object.mode_set(mode='OBJECT')
    
    for best_island, (bone_name, _) in island_assignment.items():
        group = mesh_obj.vertex_groups.get(bone_name)
        if not group:
            group = mesh_obj.vertex_groups.new(name=bone_name)
        group.add(list(best_island), 1.0, 'ADD')
    

    print("Vertex groups assigned!")

# Example Operator to Run the Script
class AutoVertexGroupAssigner(bpy.types.Operator):
    """Automatically assigns vertex groups based on vertex islands and bone proximity."""
    bl_idname = "object.auto_vertex_groups"
    bl_label = "Auto Assign Vertex Groups"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        selected_objects = context.selected_objects
        if len(selected_objects) < 2:
            self.report({'ERROR'}, "Select a mesh and an armature.")
            return {'CANCELLED'}
        
        mesh = None
        armature = None
        for obj in selected_objects:
            if obj.type == 'MESH':
                mesh = obj
            elif obj.type == 'ARMATURE':
                armature = obj
        
        if not mesh or not armature:
            self.report({'ERROR'}, "Requires a mesh and an armature.")
            return {'CANCELLED'}
        
        assign_vertex_groups(mesh, armature)
        
         # Parent the mesh to the armature with Armature Deform
        bpy.context.view_layer.objects.active = armature
        bpy.ops.object.parent_set(type='ARMATURE_NAME')
        return {'FINISHED'}

def parent_menu_func(self, context):
    """Add the operator to the Set Parent To menu under Armature Deform."""
    self.layout.operator(
        AutoVertexGroupAssigner.bl_idname,
        text="Armature Deform With Linked Groups"
    )

def register():
    bpy.utils.register_class(AutoVertexGroupAssigner)
    # Append the operator to the parenting menu
    bpy.types.VIEW3D_MT_object_parent.append(parent_menu_func)

def unregister():
    bpy.utils.unregister_class(AutoVertexGroupAssigner)
    # Remove the operator from the parenting menu
    bpy.types.VIEW3D_MT_object_parent.remove(parent_menu_func)
