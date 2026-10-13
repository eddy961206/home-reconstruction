UNREAL IMPORT SCAFFOLD — NOT ENGINE-VERIFIED

This folder is a project descriptor, FBX source assets, and an Editor Python import script. It is NOT a finished Unreal .umap/.uasset project or a playable packaged application. Unreal Engine was not installed in the authoring environment, and no engine render or runtime test has been performed.

1. Open HomeReconstruction.uproject in a licensed Unreal Engine 5.x installation. EngineAssociation is a 5.4 starting point; select your installed compatible version if prompted.
2. Enable the bundled Python Editor Script and Editor Scripting Utilities plugins if needed, then restart.
3. In Tools > Execute Python Script, select Content/Python/import_home.py.
4. The script creates /Game/HomeReconstruction/EstimatedHome and imports meshes. Inspect orientation, dimensions, lighting and materials.
5. Use the editor viewport to inspect. A character controller, gameplay collision and packaged walkthrough are not included.

The Blender file is the authoritative, verified source. FBX material colors are exported, but Blender procedural wood and cloth shading do not translate exactly. Area lights are not included in FBX. The supplied import script adds approximate point lights; these need tuning in the engine. glTF separately includes model geometry and materials but omits unsupported area lights.

Epic API references used for the scaffold:
https://dev.epicgames.com/documentation/en-us/unreal-engine/python-api/class/FbxStaticMeshImportData?application_version=5.0
https://dev.epicgames.com/documentation/en-us/unreal-engine/python-api/class/LevelEditorSubsystem?application_version=5.0

Material fidelity: no PBR texture baking was performed. The exchange files carry basic base-color/roughness/metallic values where supported. Procedural wood grain, fabric microtexture and patterned cloth may fall back to simplified colors and will need baking or native Unreal material recreation. These files do not establish Blender–Unreal visual parity.
