bl_info = {
	'name': 'Import Virt A Mate .vab model',
	'author': 'my12doom',
	'version': (1, 0, 0),
	'blender': (2, 83, 0),
	'api': 36302,
	'location': 'File > Import > Virt A Mate model',
	'tracker_url': '',
	'support': 'COMMUNITY',
	'category': 'Import-Export'}

from .import_vab import *
import bpy

register_classes, unregister_classes = bpy.utils.register_classes_factory([VABImporter])

def menu_func_import(self, context):
	self.layout.operator(VABImporter.bl_idname, text = 'Virt A Mate model (.vab)')

def register():
	register_classes()
	bpy.types.TOPBAR_MT_file_import.append(menu_func_import)

def unregister():
	unregister_classes()
	bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)

if __name__ == '__main__':
	register()
