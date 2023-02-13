bl_info = {
    "name": "rFactor 2 Suspension Model Exporter",
    "author": "FuNK!",
    "version": "0.1.0",
    "blender": (2, 90, 0),
    "location": "File > Export",
    "description": "Exports the suspension definition for a PM suspension model to be used in rFactor2.",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Import-Export"
}

import bpy
import re
import os
import math

from bpy.props import StringProperty
from bpy_extras.io_utils import ExportHelper

class SuspensionModelPMExporter(bpy.types.Operator, ExportHelper):
    """Exports the suspension definition for a PM suspension model to be used in rFactor2."""
    bl_idname = "export_suspension.pm_definition"
    bl_label = "Export rFactor2 Suspension Definition"

    filename_ext = ".pm"

    filter_glob: StringProperty(
        default="*.pm",
        options={'HIDDEN'},
        maxlen=255,  # Max internal buffer length, longer would be clamped.
    )

    def execute(self, context):
        filepath = bpy.path.ensure_ext(self.filepath, self.filename_ext)

        # Empty the error message list
        error_messages = []

        # Write bodies to the pm file
        try:
            with open(self.filepath, 'w') as pm_file:
                pm_file.write("// Suspension Model exported from Blender with rFactor 2 Suspension Model Exporter for Blender by FuNK!\n")
                pm_file.write("//////////////////////////////////////////////////////////////////////////\n")
                pm_file.write("// Conventions:\n")
                pm_file.write("// +x = left\n")
                pm_file.write("// +z = rear\n")
                pm_file.write("// +y = up\n")
                pm_file.write("// +pitch = nose up\n")
                pm_file.write("// +yaw = nose right\n")
                pm_file.write("// +roll = right\n")
                pm_file.write("//\n")
                pm_file.write("// [BODY]  - a rigid mass with mass and inertial properties\n")
                pm_file.write("// [JOINT] - a ball joint constraining an offset of one body to an offset of another body (eliminates 3 DOF)\n")
                pm_file.write("// [HINGE] - a constraint restricting the relative rotations of two bodies to be around a single axis (eliminates 2 DOF).\n")
                pm_file.write("// [BAR]   - a constraint holding an offset of one body from an offset of  another body at a fixed distance (eliminates 1 DOF).\n")
                pm_file.write("// [JOINT&HINGE] - both the joint and hinge constraints, forming the conventional definition of a hinge (eliminates 5 DOF).\n")
                pm_file.write("//////////////////////////////////////////////////////////////////////////\n\n")

                pm_file.write("// Body including all rigidly attached parts (wings, barge boards, etc.)\n")
                pm_file.write("// NOTE: the mass and inertia for the main vehicle 'body' are not used because it is derived from the HDV file\n")
                pm_file.write("// by subtracting out all the wheels, etc.  For all other bodies (wheels, spindles), they are important!\n\n")

                # Check for bodies, use default objects in case no objects are found
                # Check for "body" object
                body_obj = bpy.data.objects.get("body")
                if not body_obj:
                    error_messages.append("Object with name 'body' not found, using defaults.\nManual editing required!")
                    pm_file.write("[BODY]\n")
                    pm_file.write("name=body mass=(0) inertia=(0,0,0)\n")
                    pm_file.write("pos=(0,0,0) ori=(0,0,0)\n\n")
                else:
                    # Get object properties here and write to file
                    pm_file.write("[BODY]\n")
                    pm_file.write("name=body mass=(0) inertia=(0,0,0)\n")
                    pm_file.write("pos=({:.3f}, {:.3f}, {:.3f}) ori=({:.3f}, {:.3f}, {:.3f})\n\n".format(body_obj.location.x, body_obj.location.z, body_obj.location.y, body_obj.rotation_euler.x, body_obj.rotation_euler.z, body_obj.rotation_euler.y))

                # Check for "fl_spindle" object
                body_obj = bpy.data.objects.get("fl_spindle")
                if not body_obj:
                    error_messages.append("Object with name 'fl_spindle' not found, using defaults.\nManual editing required!")
                    pm_file.write("// FRONT SPINDLES\n")
                    pm_file.write("[BODY]\n")
                    pm_file.write("name=fl_spindle mass=(0) inertia=(0,0,0) // Unsprung masses that do not exhibit any pitch rotation with significant relation to the wheel rotation rate\n")
                    pm_file.write("pos=(0,0,0) ori=(0,0,0)\n\n")
                else:
                    # Get object properties here and write to file
                    pm_file.write("// FRONT SPINDLES\n")
                    pm_file.write("[BODY]\n")
                    pm_file.write("name=fl_spindle mass=(0) inertia=(0,0,0) // Unsprung masses that do not exhibit any pitch rotation with significant relation to the wheel rotation rate\n")
                    pm_file.write("pos=({:.3f}, {:.3f}, {:.3f}) ori=({:.3f}, {:.3f}, {:.3f})\n\n".format(body_obj.location.x, body_obj.location.z, body_obj.location.y, body_obj.rotation_euler.x, body_obj.rotation_euler.z, body_obj.rotation_euler.y))

                # Check for "fr_spindle" object
                body_obj = bpy.data.objects.get("fr_spindle")
                if not body_obj:
                    error_messages.append("Object with name 'fr_spindle' not found, using defaults.\nManual editing required!")
                    pm_file.write("[BODY]\n")
                    pm_file.write("name=fr_spindle mass=(0) inertia=(0,0,0)\n")
                    pm_file.write("pos=(0,0,0) ori=(0,0,0)\n\n")
                else:
                    # Get object properties here and write to file
                    pm_file.write("[BODY]\n")
                    pm_file.write("name=fr_spindle mass=(0) inertia=(0,0,0)\n")
                    pm_file.write("pos=({:.3f}, {:.3f}, {:.3f}) ori=({:.3f}, {:.3f}, {:.3f})\n\n".format(body_obj.location.x, body_obj.location.z, body_obj.location.y, body_obj.rotation_euler.x, body_obj.rotation_euler.z, body_obj.rotation_euler.y))

                # Check for "fl_wheel" object
                body_obj = bpy.data.objects.get("fl_wheel")
                if not body_obj:
                    error_messages.append("Object with name 'fl_wheel' not found, using defaults.\nManual editing required!")
                    pm_file.write("// FRONT WHEELS\n")
                    pm_file.write("[BODY]\n")
                    pm_file.write("name=fl_wheel mass=(0) inertia=(0,0,0) // Any unsprung bodies that rotate significantly in proportion to the wheel rotation rate (i.e. generally tyre+rim+disc/bell+bearing+nuts)\n")
                    pm_file.write("pos=(0,0,0) ori=(0,0,0)\n\n")
                else:
                    # Get object properties here and write to file
                    pm_file.write("// FRONT WHEELS\n")
                    pm_file.write("[BODY]\n")
                    pm_file.write("name=fl_wheel mass=(0) inertia=(0,0,0) // Any unsprung bodies that rotate significantly in proportion to the wheel rotation rate (i.e. generally tyre+rim+disc/bell+bearing+nuts)\n")
                    pm_file.write("pos=({:.3f}, {:.3f}, {:.3f}) ori=({:.3f}, {:.3f}, {:.3f})\n\n".format(body_obj.location.x, body_obj.location.z, body_obj.location.y, body_obj.rotation_euler.x, body_obj.rotation_euler.z, body_obj.rotation_euler.y))

                # Check for "fr_wheel" object
                body_obj = bpy.data.objects.get("fr_wheel")
                if not body_obj:
                    error_messages.append("Object with name 'fr_wheel' not found, using defaults.\nManual editing required!")
                    pm_file.write("[BODY]\n")
                    pm_file.write("name=fl_wheel mass=(0) inertia=(0,0,0)\n")
                    pm_file.write("pos=(0,0,0) ori=(0,0,0)\n\n")
                else:
                    # Get object properties here and write to file
                    pm_file.write("[BODY]\n")
                    pm_file.write("name=fr_wheel mass=(0) inertia=(0,0,0)\n")
                    pm_file.write("pos=({:.3f}, {:.3f}, {:.3f}) ori=({:.3f}, {:.3f}, {:.3f})\n\n".format(body_obj.location.x, body_obj.location.z, body_obj.location.y, body_obj.rotation_euler.x, body_obj.rotation_euler.z, body_obj.rotation_euler.y))

                # Check for "rl_spindle" object
                body_obj = bpy.data.objects.get("rl_spindle")
                if not body_obj:
                    error_messages.append("Object with name 'rl_spindle' not found, using defaults.\nManual editing required!")
                    pm_file.write("// REAR SPINDLES\n")
                    pm_file.write("[BODY]\n")
                    pm_file.write("name=rl_spindle mass=(0) inertia=(0,0,0)\n")
                    pm_file.write("pos=(0,0,0) ori=(0,0,0)\n\n")
                else:
                    # Get object properties here and write to file
                    pm_file.write("// REAR SPINDLES\n")
                    pm_file.write("[BODY]\n")
                    pm_file.write("name=rl_spindle mass=(0) inertia=(0,0,0)\n")
                    pm_file.write("pos=({:.3f}, {:.3f}, {:.3f}) ori=({:.3f}, {:.3f}, {:.3f})\n\n".format(body_obj.location.x, body_obj.location.z, body_obj.location.y, body_obj.rotation_euler.x, body_obj.rotation_euler.z, body_obj.rotation_euler.y))

                # Check for "rr_spindle" object
                body_obj = bpy.data.objects.get("rr_spindle")
                if not body_obj:
                    error_messages.append("Object with name 'rr_spindle' not found, using defaults.\nManual editing required!")
                    pm_file.write("[BODY]\n")
                    pm_file.write("name=rr_spindle mass=(0) inertia=(0,0,0)\n")
                    pm_file.write("pos=(0,0,0) ori=(0,0,0)\n\n")
                else:
                    # Get object properties here and write to file
                    pm_file.write("[BODY]\n")
                    pm_file.write("name=rr_spindle mass=(0) inertia=(0,0,0)\n")
                    pm_file.write("pos=({:.3f}, {:.3f}, {:.3f}) ori=({:.3f}, {:.3f}, {:.3f})\n\n".format(body_obj.location.x, body_obj.location.z, body_obj.location.y, body_obj.rotation_euler.x, body_obj.rotation_euler.z, body_obj.rotation_euler.y))

                # Check for "rl_wheel" object
                body_obj = bpy.data.objects.get("rl_wheel")
                if not body_obj:
                    error_messages.append("Object with name 'rl_wheel' not found, using defaults.\nManual editing required!")
                    pm_file.write("// REAR WHEELS (includes half of driveshaft)\n")
                    pm_file.write("[BODY]\n")
                    pm_file.write("name=rl_wheel mass=(0) inertia=(0,0,0)\n")
                    pm_file.write("pos=(0,0,0) ori=(0,0,0)\n\n")
                else:
                    # Get object properties here and write to file
                    pm_file.write("// REAR WHEELS (includes half of driveshaft)\n")
                    pm_file.write("[BODY]\n")
                    pm_file.write("name=rl_wheel mass=(0) inertia=(0,0,0)\n")
                    pm_file.write("pos=({:.3f}, {:.3f}, {:.3f}) ori=({:.3f}, {:.3f}, {:.3f})\n\n".format(body_obj.location.x, body_obj.location.z, body_obj.location.y, body_obj.rotation_euler.x, body_obj.rotation_euler.z, body_obj.rotation_euler.y))

                # Check for "rr_wheel" object
                body_obj = bpy.data.objects.get("rr_wheel")
                if not body_obj:
                    error_messages.append("Object with name 'rr_wheel' not found, using defaults.\nManual editing required!")
                    pm_file.write("[BODY]\n")
                    pm_file.write("name=rr_wheel mass=(0) inertia=(0,0,0)\n")
                    pm_file.write("pos=(0,0,0) ori=(0,0,0)\n\n")
                else:
                    # Get object properties here and write to file
                    pm_file.write("[BODY]\n")
                    pm_file.write("name=rr_wheel mass=(0) inertia=(0,0,0)\n")
                    pm_file.write("pos=({:.3f}, {:.3f}, {:.3f}) ori=({:.3f}, {:.3f}, {:.3f})\n\n".format(body_obj.location.x, body_obj.location.z, body_obj.location.y, body_obj.rotation_euler.x, body_obj.rotation_euler.z, body_obj.rotation_euler.y))

                # Fuel tank is a default body that does not affect physics, so it's not required to be in the scene. Still it should be in the PM!
                pm_file.write("// FUEL TANK\n")
                pm_file.write("// Fuel in tank is not rigidly attached - it is attached with springs and dampers to simulate movement.  Properties are defined in the HDV file.\n")
                pm_file.write("[BODY]\n")
                pm_file.write("name=fuel_tank mass=(0.5) inertia=(0.3,0.3,0.3) // Defines the minimum mass of remaining fuel in tank\n")
                pm_file.write("pos=(0,0,0) ori=(0,0,0)\n\n")

                # Driver head is a default body that does not affect physics, so it's not required to be in the scene. Still it should be in the PM!
                pm_file.write("// DRIVER HEAD\n")
                pm_file.write("// Driver's head is not rigidly attached, and it does NOT affect the vehicle physics.\n")
                pm_file.write("// Position is from the eyepoint defined in the VEH file, while other properties are defined in the head physics file.\n")
                pm_file.write("[BODY]\n")
                pm_file.write("name=driver_head mass=(6.6) inertia=(0.047,0.036,0.039)\n")
                pm_file.write("pos=(0,0,0) ori=(0,0,0)\n\n")

                # Writing the constraints as defaults for now.

                pm_file.write("//////////////////////////////////////////////////////////////////////////\n")
                pm_file.write("// CONSTRAINTS\n")
                pm_file.write("//////////////////////////////////////////////////////////////////////////\n\n")

                pm_file.write("// Wheel and spindle connections\n")
                pm_file.write("[JOINT&HINGE]\n")
                pm_file.write("posbody=fl_wheel negbody=fl_spindle pos=fl_wheel axis=( 1,0,0)\n\n")

                pm_file.write("[JOINT&HINGE]\n")
                pm_file.write("posbody=fr_wheel negbody=fr_spindle pos=fr_wheel axis=(-1,0,0)\n\n")

                pm_file.write("[JOINT&HINGE]\n")
                pm_file.write("posbody=rl_wheel negbody=rl_spindle pos=rl_wheel axis=( 1,0,0)\n\n")

                pm_file.write("[JOINT&HINGE]\n")
                pm_file.write("posbody=rr_wheel negbody=rr_spindle pos=rr_wheel axis=(-1,0,0)\n\n")

                # Check the presence of required BAR objects, cancle the execution if not present, write the BAR objects
                # For now requires the BAR objects as in the Skippy, so code requires further optimization later to allow other suspension setups
                bar_objs = ["fl_fore_upper", "fl_rear_upper", "fl_fore_lower", "fl_rear_lower", "fl_steering", "fr_fore_upper", "fr_rear_upper", "fr_fore_lower", "fr_rear_lower", "fr_steering", "rl_fore_upper", "rl_rear_upper", "rl_fore_lower", "rl_rear_lower", "rl_toelink", "rr_fore_upper", "rr_rear_upper", "rr_fore_lower", "rr_rear_lower", "rr_toelink"]

                bar_neg_body_mapping = {
                    "fl": "fl_spindle",
                    "fr": "fr_spindle",
                    "rl": "rl_spindle",
                    "rr": "rr_spindle",
                }

                for bar_obj_name in bar_objs:
                    if bar_obj_name not in bpy.data.objects:
                        error_messages.append(f"Object with name '{bar_obj_name}' not found.")
                        continue

                    obj = bpy.data.objects.get(bar_obj_name)

                    if len(obj.data.vertices) != 2:
                        error_messages.append(f"Object '{bar_obj_name}' should have exactly 2 vertices.")

                if error_messages:
                    error_message = "\n".join(error_messages)
                    self.report({'ERROR'}, error_message)
                    return {'CANCELLED'}

                for bar_obj_name in bar_objs:
                    if bar_obj_name not in bpy.data.objects:
                        error_messages.append(f"Object with name '{bar_obj_name}' not found.")
                        continue

                    bar = bpy.data.objects.get(bar_obj_name)

                    # Original
                    # v1 = bar.data.vertices[0].co
                    # v2 = bar.data.vertices[1].co
                    #
                    # if v1.y > v2.y:
                    #     pos_vertex = v1
                    #     neg_vertex = v2
                    # else:
                    #     pos_vertex = v2
                    #     neg_vertex = v1

                    v1 = bar.data.vertices[0].co
                    v2 = bar.data.vertices[1].co

                    d1 = math.sqrt((v1.x - 0)**2 + (v1.y - 0)**2 + (v1.z - 0)**2)
                    d2 = math.sqrt((v2.x - 0)**2 + (v2.y - 0)**2 + (v2.z - 0)**2)

                    if d1 < d2:
                        pos_vertex = v1
                        neg_vertex = v2
                    else:
                        pos_vertex = v2
                        neg_vertex = v1

                    prefix = bar.name[:2]
                    if prefix not in bar_neg_body_mapping:
                        error_messages.append(f"Object name {bar.name} does not meet criteria for setting negbody value.")
                        continue

                    bar_neg_body = bar_neg_body_mapping[prefix]

                    if bar.name == "fl_fore_upper":
                        pm_file.write("// FRONT LEFT SUSPENSION (2 A-arms + 1 steering arm = 5 links)\n")
                    elif bar.name == "fr_fore_upper":
                        pm_file.write("// FRONT RIGHT SUSPENSION (2 A-arms + 1 steering arm = 5 links)\n")
                    elif bar.name == "rl_fore_upper":
                        pm_file.write("// REAR LEFT SUSPENSION (2 A-arms + 1 straight link = 5 links)\n")
                    elif bar.name == "rr_fore_upper":
                        pm_file.write("// REAR RIGHT SUSPENSION (2 A-arms + 1 straight link = 5 links)\n")

                    if bar.name == "fl_steering":
                        pm_file.write("[BAR] // Steering arm must be named for identification!\n")
                    elif bar.name == "fr_fore_upper":
                        pm_file.write("[BAR] // Forward upper arm is used in steering lock calculation\n")
                    elif bar.name == "fr_steering":
                        pm_file.write("[BAR] // Steering arm must be named for identification!\n")
                    else:
                        pm_file.write("[BAR]\n")

                    pm_file.write("name={} ".format(bar.name))
                    pm_file.write("posbody=body ")
                    pm_file.write("negbody={} ".format(bar_neg_body))
                    pm_file.write("pos=({:.4f}, {:.4f}, {:.4f}) ".format(pos_vertex.x, pos_vertex.z, pos_vertex.y))
                    pm_file.write("neg=({:.4f}, {:.4f}, {:.4f})\n\n".format(neg_vertex.x, neg_vertex.z, neg_vertex.y))

        except Exception as e:
            self.report({'ERROR'}, "Error while opening or writing to file: " + str(e))
            return {'CANCELLED'}

    	# Check if any error messages were added to the list and display them to the user
        if error_messages:
            error_message = "\n".join(error_messages)
            self.report({'ERROR'}, error_message)
            print(error_message)
        else:
            self.report({'INFO'}, "Successfully exported rFactor2 Supension Model PM file.")
            print("Successfully exported rFactor2 Supension Model PM file.")

        return {'FINISHED'}

def menu_func_export(self, context):
    self.layout.operator(SuspensionModelPMExporter.bl_idname, text="Export rFactor2 Suspension Model (.pm)")

def register():
    bpy.utils.register_class(SuspensionModelPMExporter)
    bpy.types.TOPBAR_MT_file_export.append(menu_func_export)

def unregister():
    bpy.utils.unregister_class(SuspensionModelPMExporter)
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)

if __name__ == "__main__":
    register()
