import bpy

bl_info = {
    "name": "iJewel Diamond Extension",
    "extension_name": "WEBGI_materials_diamond",
    "category": "GLTF Exporter",
    "version": (1, 0, 0),
    "blender": (2, 92, 0),
    'location': 'File > Export > glTF 2.0',
    'description': 'Extension to set and export diamond material properties.',
    'tracker_url': '',  # Replace with your issue tracker
    'isDraft': False,
    'developer': "Palash Bansal",
    'url': 'https://repalash.com',
}


# https://github.com/KhronosGroup/glTF-Blender-IO/tree/master/example-addons/example_gltf_extension

# glTF extensions are named following a convention with known prefixes.
# See: https://github.com/KhronosGroup/glTF/tree/master/extensions#about-gltf-extensions
# also: https://github.com/KhronosGroup/glTF/blob/master/extensions/Prefixes.md

gltf_extension_is_required = False


class IJewelGLTFExtensionProperties(bpy.types.PropertyGroup):
    enabled: bpy.props.BoolProperty(
        name=bl_info["name"],
        description='Include this extension in the exported glTF file.',
        default=True
    )
    extension_name: bpy.props.StringProperty(
        name="Extension",
        description='GLTF extension name.',
        default=bl_info["extension_name"]
    )


class MaterialButtonsPanel:
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "material"
    # COMPAT_ENGINES must be defined in each subclass, external engines can add themselves here

    @classmethod
    def poll(cls, context):
        mat = context.material
        return mat and (context.engine in cls.COMPAT_ENGINES) and not mat.grease_pencil



class MATERIAL_PT_ijewel_diamond(MaterialButtonsPanel, bpy.types.Panel):
    bl_label = "iJewel Diamond Material"
    bl_options = {'DEFAULT_CLOSED'}
    COMPAT_ENGINES = {'BLENDER_EEVEE'}

    def draw_header(self, context):
        props = context.object.active_material.ijewel_diamond
        self.layout.prop(props, 'isDiamond')

    def draw(self, context):
        layout = self.layout
        ob = context.object
        prop = ob.active_material.ijewel_diamond
        layout.use_property_split = True
        layout.use_property_decorate = False  # No animation.
        layout.active = prop.isDiamond
        layout.prop(prop, 'dispersion')
        layout.prop(prop, 'refractiveIndex')
        layout.prop(prop, 'boostFactors')
        layout.prop(prop, 'envMapIntensity')



class IJewelDiamondMaterialPropertyGroup(bpy.types.PropertyGroup):
    isDiamond: bpy.props.BoolProperty(name="")
    dispersion: bpy.props.FloatProperty(name="Dispersion", min=0, max=5, step=0.01)
    refractiveIndex: bpy.props.FloatProperty(name="Refractive Index", min=0, max=5, step=0.01)
    envMapIntensity: bpy.props.FloatProperty(name="Env Intensity", min=0, max=10, step=0.1, default=1)
    boostFactors: bpy.props.FloatVectorProperty(name="Boost Factors", min=0, max=5, step=0.1, size=3, default=(1,1,1))



def register_panel():
    try:
        bpy.utils.register_class(GLTF_PT_IJewelExtensionPanel)
    except Exception:
        pass

def unregister_panel():
    try:
        bpy.utils.unregister_class(GLTF_PT_IJewelExtensionPanel)
    except Exception:
        pass

def register():
    bpy.utils.register_class(MATERIAL_PT_ijewel_diamond)
    bpy.utils.register_class(IJewelGLTFExtensionProperties)
    bpy.utils.register_class(IJewelDiamondMaterialPropertyGroup)

    bpy.types.Scene.IJewelExtensionProperties = bpy.props.PointerProperty(type=IJewelGLTFExtensionProperties)
    bpy.types.Material.ijewel_diamond = bpy.props.PointerProperty(type=IJewelDiamondMaterialPropertyGroup)
    #bpy.types.MATERIAL_PT_preview.prepend(draw_func)

def unregister():
    unregister_panel()
    del bpy.types.Material.ijewel_diamond
    bpy.utils.unregister_class(MATERIAL_PT_ijewel_diamond)
    bpy.utils.unregister_class(IJewelGLTFExtensionProperties)
    bpy.utils.unregister_class(IJewelDiamondMaterialPropertyGroup)
    #bpy.types.MATERIAL_PT_preview.remove(draw_func)



class GLTF_PT_IJewelExtensionPanel(bpy.types.Panel):

    bl_space_type = 'FILE_BROWSER'
    bl_region_type = 'TOOL_PROPS'
    bl_label = "Enabled"
    bl_parent_id = "GLTF_PT_export_user_extensions"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        sfile = context.space_data
        operator = sfile.active_operator
        return operator.bl_idname == "EXPORT_SCENE_OT_gltf"

    def draw_header(self, context):
        props = bpy.context.scene.IJewelExtensionProperties
        self.layout.prop(props, 'enabled')

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False  # No animation.

        props = bpy.context.scene.IJewelExtensionProperties
        layout.active = props.enabled

        box = layout.box()
        box.label(text=props.extension_name)

        layout.prop(props, 'extension_name', text="GLTF extension name")


class glTF2ExportUserExtension:

    def __init__(self):
        from io_scene_gltf2.io.com.gltf2_io_extensions import Extension
        self.Extension = Extension
        self.properties = bpy.context.scene.IJewelExtensionProperties


    def gather_material_hook(self, gltf2_material, blender_material, export_settings):

        if self.properties.enabled and blender_material.ijewel_diamond.isDiamond:

            extension_data = {
                'isDiamond': True,
                'dispersion': blender_material.ijewel_diamond.dispersion,
                'refractiveIndex': blender_material.ijewel_diamond.refractiveIndex,
                'boostFactors': tuple(blender_material.ijewel_diamond.boostFactors),
                'envMapIntensity': blender_material.ijewel_diamond.envMapIntensity
            }

            gltf2_material.extensions[self.properties.extension_name] = self.Extension(
                name=self.properties.extension_name,
                extension=extension_data,
                required=gltf_extension_is_required)



if __name__ == "__main__":
    register()
