import struct
import bpy
from bpy_extras.io_utils import ImportHelper
import os

def readstring(file):
	len = file.read(1)[0]
	text = file.read(len).decode()
	print("text:", text)
	return text

def DoImport(filename):    
	file = open(filename, "rb")    
	meshName = filename.split("/")[-1].split("\\")[-1].replace(".vab", "")
	

	def read32():
		return struct.unpack('i', file.read(4))[0]

	def readvertex():
		raw = struct.unpack('fff', file.read(12))
		return (raw[0], raw[2], raw[1])

	def readface2():
		(mat_id, sides) = struct.unpack('ii', file.read(8))
		return mat_id, sides, struct.unpack('i'*sides, file.read(sides*4))

	def readuv():
		return struct.unpack('ff', file.read(8))

	for i in range(8):
		readstring(file)

	n_vertex = read32()
	print("n_vertex:", n_vertex)
	vertex = []
	for i in range(n_vertex):    
		vertex.append(readvertex())
		
	mats = []
	n_mat = read32()
	print("n_mat", n_mat)
	for i in range(n_mat):
		name = readstring(file)
		mats.append(bpy.data.materials.new(name))

	# load face & uv index
	faces = []
	face_uvs = []
	face_mat = []
	n_face = read32()
	print("n_face:", n_face)
	last_idx = 0
	for i in range(n_face):
		mat_id, sides, face = readface2()
		
		faces.append(face)
		face_mat.append(mat_id)
		
	for i in range(n_face):
		mat_id, sides, face = readface2()
					
		face_uvs.append(face)

	# load UV
	n_uv = read32()
	uvs = []
	print("n_uv:", n_uv)
	for i in range(n_uv):
		uv = readuv()
		#print(uv)
		uvs.append(uv)

	file.close()

	# create object   
	mesh = bpy.context.blend_data.meshes.new(name=meshName)
	mesh.from_pydata(vertex, [], faces)
	#mesh.validate()
	profile_object = bpy.data.objects.new(meshName, mesh)
	bpy.context.collection.objects.link(profile_object)

	# create UV
	uvtex = mesh.uv_layers.new(name = "UVMap")

	uv_faces = []
	for face in face_uvs:
		for idx in face:
			uv_faces.append(uvs[idx])
		
	print("n_uv_faces", len(uv_faces))
	print("len(uvtex.data)", len(uvtex.data))

	for i, uv in enumerate(uv_faces):
		datum = uvtex.data[i]
		datum.uv = [uv[0], uv[1]]
		
	# create material
	for i in range(n_mat):
		mesh.materials.append(mats[i])
	
	for i, poly in enumerate(mesh.polygons):
		poly.material_index = face_mat[i]
		poly.use_smooth = True
		
	mesh.validate()

		
class VABImporter(bpy.types.Operator, ImportHelper):
	"""Import VAM vab model file (.vab)."""
	bl_idname = "vam.import_vab"
	bl_label = "Import VAB"

	files: bpy.props.CollectionProperty(
			name="File Path",
			type=bpy.types.OperatorFileListElement,
	)
	directory: bpy.props.StringProperty(
			subtype='DIR_PATH',
	)
	# ImportHelper mixin class uses this
	filename_ext = ".vab"

	filter_glob: bpy.props.StringProperty(
		default="*.vab",
		options={'HIDDEN'},
		maxlen=1024,  # Max internal buffer length, longer would be clamped.
	)

	def execute(self, context):
		for file in self.files:
			DoImport(os.path.join(self.directory, file.name))
		return {'FINISHED'}