bl_info = {
    "name": "Animation Presets Pro",
    "author": "Your Name",
    "version": (1, 5),
    "blender": (3, 0, 0),
    "location": "View3D > Sidebar > Animation",
    "description": "Professional animation presets with advanced controls",
    "category": "Animation"
}

import bpy
from bpy.types import Panel, Operator, PropertyGroup
from bpy.props import FloatProperty, EnumProperty, StringProperty, PointerProperty, IntProperty, BoolProperty
from mathutils import Vector, Euler
import math

def get_presets(self, context):
    return [
        ('EXPLOSION', 'Explosion', 'Explosive scale animation', 'FORCE_FORCE', 0),
        ('BOUNCE', 'Bounce', 'Realistic bouncing animation', 'FORCE_HARMONIC', 1),
        ('SPIN', 'Spin', 'Smooth rotation animation', 'FORCE_VORTEX', 2),
        ('SCALE', 'Scale Pulse', 'Dynamic scale animation', 'FULLSCREEN_ENTER', 3),
        ('FADE', 'Fade In/Out', 'Smooth fade animation', 'MATERIAL', 4),
        ('SHAKE', 'Shake', 'Energetic shaking animation', 'MOD_NOISE', 5),
    ]

class AnimationPresetProperties(PropertyGroup):
    animation_speed: FloatProperty(
        name="Animation Speed",
        description="Speed multiplier for animations (higher = faster)",
        default=1000.0,
        min=100.0,
        max=2000.0,
        soft_min=500.0,
        soft_max=1500.0
    )
    
    start_frame: IntProperty(
        name="Start Frame",
        description="Starting frame for the animation",
        default=1,
        min=1
    )
    
    preset_enum: EnumProperty(
        items=get_presets,
        name="Animation Presets",
        description="Choose an animation preset to apply"
    )
    
    intensity: FloatProperty(
        name="Effect Intensity",
        description="Controls the strength of the animation effect",
        default=1.0,
        min=0.1,
        max=2.0,
        soft_min=0.5,
        soft_max=1.5
    )
    
    loop_animation: BoolProperty(
        name="Loop Animation",
        description="Make the animation loop continuously",
        default=False
    )

    ease_type: EnumProperty(
        name="Easing",
        description="Animation easing type",
        items=[
            ('EASE_IN_OUT', 'Smooth', 'Smooth acceleration and deceleration'),
            ('EASE_IN', 'Accelerate', 'Gradual acceleration'),
            ('EASE_OUT', 'Decelerate', 'Gradual deceleration'),
            ('LINEAR', 'Linear', 'Constant speed'),
        ],
        default='EASE_IN_OUT'
    )

class ANIM_OT_add_preset(Operator):
    bl_idname = "anim.add_preset"
    bl_label = "Apply Animation"
    bl_description = "Apply the selected animation preset to objects"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        props = context.scene.animation_preset_props
        preset_name = props.preset_enum
        
        if not context.selected_objects:
            self.report({'WARNING'}, "Please select at least one object")
            return {'CANCELLED'}
        
        # Store the animation function mapping
        animation_functions = {
            'EXPLOSION': self.add_explosion_animation,
            'BOUNCE': self.add_bounce_animation,
            'SPIN': self.add_spin_animation,
            'SCALE': self.add_scale_animation,
            'FADE': self.add_fade_animation,
            'SHAKE': self.add_shake_animation
        }
        
        # Call the appropriate animation function
        if preset_name in animation_functions:
            animation_functions[preset_name](context)
            self.report({'INFO'}, f"Applied {preset_name.lower()} animation")
        
        return {'FINISHED'}
    
    def setup_animation(self, obj, name):
        if not obj.animation_data:
            obj.animation_data_create()
        action = bpy.data.actions.new(name=f"{name}_{obj.name}")
        obj.animation_data.action = action
        return action
    
    def set_keyframe_interpolation(self, action, props):
        for fc in action.fcurves:
            for kf in fc.keyframe_points:
                kf.interpolation = 'BEZIER'
                if props.ease_type == 'EASE_IN_OUT':
                    kf.easing = 'EASE_IN_OUT'
                elif props.ease_type == 'EASE_IN':
                    kf.easing = 'EASE_IN'
                elif props.ease_type == 'EASE_OUT':
                    kf.easing = 'EASE_OUT'
                else:
                    kf.easing = 'LINEAR'
    
    def add_explosion_animation(self, context):
        props = context.scene.animation_preset_props
        frame_start = props.start_frame
        duration = 30 * (1000/props.animation_speed)
        frame_end = frame_start + duration
        
        for obj in context.selected_objects:
            action = self.setup_animation(obj, "Explosion")
            
            # Enhanced explosion animation with intensity scaling
            max_scale = 2.0 * props.intensity
            obj.scale = Vector((1, 1, 1))
            obj.keyframe_insert(data_path="scale", frame=frame_start)
            
            mid_frame = frame_start + (duration * 0.4)
            obj.scale = Vector((max_scale, max_scale, max_scale))
            obj.keyframe_insert(data_path="scale", frame=mid_frame)
            
            obj.scale = Vector((0, 0, 0))
            obj.keyframe_insert(data_path="scale", frame=frame_end)
            
            self.set_keyframe_interpolation(action, props)
            
            if props.loop_animation:
                action.use_cyclic = True

    # Add similar enhancements for other animation methods...
    # [Additional animation methods would go here with similar improvements]

class ANIM_OT_reset_animation(Operator):
    bl_idname = "anim.reset_animation"
    bl_label = "Reset Animation"
    bl_description = "Clear animations and reset object transforms"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        if not context.selected_objects:
            self.report({'WARNING'}, "Please select at least one object")
            return {'CANCELLED'}
            
        for obj in context.selected_objects:
            if obj.animation_data:
                obj.animation_data_clear()
            obj.location = Vector((0, 0, 0))
            obj.rotation_euler = Euler((0, 0, 0))
            obj.scale = Vector((1, 1, 1))
        
        self.report({'INFO'}, "Animation reset complete")
        return {'FINISHED'}

class ANIM_PT_presets_panel(Panel):
    bl_label = "Animation Presets Pro"
    bl_idname = "ANIM_PT_presets_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Animation'
    bl_options = {'DEFAULT_CLOSED'}
    
    @classmethod
    def poll(cls, context):
        return context.mode in {'OBJECT', 'POSE'}
    
    def draw(self, context):
        layout = self.layout
        props = context.scene.animation_preset_props
        
        # Preset Selection
        box = layout.box()
        col = box.column(align=True)
        row = col.row()
        row.scale_y = 1.2
        row.prop(props, "preset_enum", text="")
        
        row = col.row(align=True)
        row.scale_y = 1.5
        row.operator("anim.add_preset", text="Apply Animation", icon='PLAY')
        row.operator("anim.reset_animation", text="Reset", icon='LOOP_BACK')
        
        # Animation Settings
        box = layout.box()
        box.label(text="Animation Settings", icon='SETTINGS')
        
        col = box.column(align=True)
        col.prop(props, "animation_speed", slider=True)
        col.prop(props, "start_frame")
        col.prop(props, "intensity", slider=True)
        
        # Animation Options
        box = layout.box()
        box.label(text="Options", icon='MODIFIER')
        
        col = box.column(align=True)
        col.prop(props, "ease_type")
        col.prop(props, "loop_animation")

classes = (
    AnimationPresetProperties,
    ANIM_OT_add_preset,
    ANIM_OT_reset_animation,
    ANIM_PT_presets_panel
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.animation_preset_props = PointerProperty(type=AnimationPresetProperties)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.animation_preset_props

if __name__ == "__main__":
    register()
