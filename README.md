# Armature Deform with Linked Groups

This add-on creates an armature with automatic vertex group assignment by vertex islands. A vertex island is all the vertices selected when "select linked" is used (ctrl-l, usually). Its intended use is for mechanical rigs, in which one mesh is usually made of several separate pieces. 

If this add-on helps you, let me know! Star the repo :)

## How to Use
1. Install via the add-on interface. Look for "Armature Deform with Linked Groups"
2. Select your mesh, and then your armature (as you would when you normally create an armature deform, with armature active)
3. Go to Object -> Parent -> Armature Deform with Linked Groups

## Limitations
### Single Mesh
Currently you can only select one mesh to be auto-deformed by the armature (planned for a future release).

### One Island per Vertex Group
Only the island nearest the bone (defined as the island with the lowest average vertex to bone center) will be assigned to the vertex group for that bone. This means things like bolts and other bits and bobs may not be assigned (or may be misassigned). This is also planned for a future release. 


