bl_info = {
    "name": "Armature Deform with Linked Groups",
    "description": "Automatically assigns vertex groups to bones based on vertex islands",
    "author": "Suchaaver Chahal",
    "version": (1, 0, 0),
    "blender": (4, 2, 0),
    "location": "3D View > Object > Parent > Armature Deform with Linked Groups",
    "category": "Rigging, Mesh, Animation",
    "support": "COMMUNITY",
    "doc_url": "https://github.com/minifigmaster125/ArmatureDeformWithLinkedGroups",
    "tracker_url": "https://github.com/minifigmaster125/ArmatureDeformWithLinkedGroups/issues",
    "warning": "",
}

from . import armature_deform_with_linked_groups 

def register():
    armature_deform_with_linked_groups.register()

def unregister():
    armature_deform_with_linked_groups.unregister()
