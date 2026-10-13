import bpy, math, random, sys, os
from mathutils import Vector
random.seed(7)
ROOT=os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0,ROOT)
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
def mat(name,c,rough=.5,metal=0):
 m=bpy.data.materials.new(name);m.diffuse_color=(*c,1);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*c,1);p.inputs['Roughness'].default_value=rough;p.inputs['Metallic'].default_value=metal;return m
cream=mat('Warm ivory plaster',(.66,.64,.57),.83); yellow=mat('Muted butter yellow laminate',(.63,.57,.30),.36);white=mat('Off white enamel',(.78,.78,.72),.35);black=mat('Black polymer',(.018,.021,.025),.36);silver=mat('Brushed steel',(.45,.47,.46),.23,.82);wood=mat('Natural oak frames',(.49,.36,.21),.46);gray=mat('Warm grey melamine',(.34,.31,.28),.55);glass=mat('Night window glass',(.04,.055,.065),.13,.35);blue=mat('Blue gray fabric',(.12,.21,.25),.9);orange=mat('Orange entry mat',(.52,.16,.045),.9)
def box(n,l,d,m,b=.015):
 bpy.ops.mesh.primitive_cube_add(size=1,location=l);o=bpy.context.object;o.name=n;o.dimensions=d;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(m)
 if b:mod=o.modifiers.new('Soft manufactured edges','BEVEL');mod.width=b;mod.segments=3;o.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
 return o
def cyl(n,l,r,depth,m,rot=(0,0,0)):
 bpy.ops.mesh.primitive_cylinder_add(vertices=32,radius=r,depth=depth,location=l,rotation=rot);o=bpy.context.object;o.name=n;o.data.materials.append(m);o.modifiers.new('Edge softness','BEVEL').width=.008;o.modifiers.new('Normals','WEIGHTED_NORMAL');return o
def sphere(n,l,s,m):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=24,ring_count=12,location=l);o=bpy.context.object;o.name=n;o.scale=s;o.data.materials.append(m);bpy.ops.object.shade_smooth();return o
def tube(n,pts,r,m):
 c=bpy.data.curves.new(n,'CURVE');c.dimensions='3D';c.bevel_depth=r;c.bevel_resolution=3;s=c.splines.new('POLY');s.points.add(len(pts)-1)
 for p,co in zip(s.points,pts):p.co=(*co,1)
 o=bpy.data.objects.new(n,c);bpy.context.collection.objects.link(o);o.data.materials.append(m);return o
# Wood planks with continuous fine procedural grain
floor=mat('Warm wood floor with fine grain',(.35,.23,.13),.52);nt=floor.node_tree;tex=nt.nodes.new('ShaderNodeTexNoise');tex.inputs['Scale'].default_value=5;tex.inputs['Detail'].default_value=3;mapping=nt.nodes.new('ShaderNodeVectorMath');mapping.operation='MULTIPLY';mapping.inputs[1].default_value=(9,1,25);coord=nt.nodes.new('ShaderNodeTexCoord');nt.links.new(coord.outputs['Generated'],mapping.inputs[0]);nt.links.new(mapping.outputs[0],tex.inputs[0]);ramp=nt.nodes.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].color=(.19,.105,.055,1);ramp.color_ramp.elements[1].color=(.46,.31,.19,1);nt.links.new(tex.outputs['Fac'],ramp.inputs[0]);nt.links.new(ramp.outputs[0],nt.nodes.get('Principled BSDF').inputs['Base Color'])
for row in range(22):
 y=row*.16
 for col in range(5):
  raw=col*.85-(.425 if row%2 else 0);x=max(0,raw);w=min(raw+.849,2.70)-x
  if w>0:box('Individual staggered oak plank',(x+w/2,y+.08,-.025),(w,.159,.05),floor,.0005)
# Walls, ceiling separately hidden for cutaway camera only
box('West living wall',(-.08,1.7,1.25),(.16,3.4,2.5),cream)
box('East living wall',(2.78,2.325,1.25),(.16,2.15,2.5),cream)
box('Entry opening header',(2.78,.625,2.3),(.16,1.25,.4),cream)
window_before=set(bpy.data.objects)
# window wall aperture
box('Window sill wall',(1.35,3.48,.44),(2.85,.16,.88),cream);box('Window lintel',(1.35,3.48,2.3),(2.85,.16,.4),cream)
for x in [.12,2.58]:box('Window side masonry',(x,3.48,1.49),(.24,.16,1.22),cream)
for x in [.29,2.42]:box('Oak window frame vertical',(x,3.36,1.5),(.075,.12,1.28),wood)
for z in [.89,2.12]:box('Oak window frame horizontal',(1.35,3.36,z),(2.19,.12,.075),wood)
for x in [.825,1.965]:box('Dark frosted window pane',(x,3.40,1.51),(.98,.035,1.15),glass,.005)
box('Sliding window middle frame',(1.35,3.32,1.51),(.08,.10,1.2),wood)
# ceiling coffer and perimeter trim
ceiling=box('Ceiling removable for plan',(1.35,1.7,2.56),(2.85,3.56,.12),cream)
for x in [.09,2.61]:box('Ceiling edge molding',(x,1.7,2.43),(.09,3.4,.09),wood,.005)
for y in [.05,3.35]:box('Ceiling edge molding',(1.35,y,2.43),(2.70,.08,.09),wood,.005)
for x in [.06,2.64]:box('Baseboard',(x,1.7,.055),(.045,3.4,.11),wood,.003)
# Linen drapes with folds
linen=mat('Cream linen curtains',(.65,.57,.43),.96)
for cx in [.43,2.27]:
 vs=[];fs=[];nx=28;nz=22
 for j in range(nz+1):
  z=.15+2.1*j/nz
  for i in range(nx+1):
   x=cx+(i/nx-.5)*.58;y=2.70+.065*math.sin(i/nx*10*math.pi)+.018*math.sin(z*4+i);vs.append((x,y,z))
 for j in range(nz):
  for i in range(nx):a=j*(nx+1)+i;fs.append((a,a+1,a+nx+2,a+nx+1))
 me=bpy.data.meshes.new('Linen folds');me.from_pydata(vs,[],fs);o=bpy.data.objects.new('Pleated beige drape',me);bpy.context.collection.objects.link(o);o.data.materials.append(linen);o.modifiers.new('Cloth thickness','SOLIDIFY').thickness=.005
 for p in me.polygons:p.use_smooth=True
cyl('Curtain rod',(1.35,3.08,2.27),.022,2.50,white,(0,math.pi/2,0))
# Correct window wall to west, adjacent to the plain bed-head wall.
window_names=[o for o in bpy.data.objects if o not in window_before and any(t in o.name for t in ['Window','window','drape','Curtain'])]
for o in window_names:
 x,y,z=o.location;o.location=(3.4-y,x+.35,z);o.rotation_euler.z+=math.pi/2
# Drape vertices were authored in world coordinates: transform via empty instead.
for o in window_names:
 if 'drape' in o.name:
  o.location=(3.4,.35,0);o.rotation_euler.z=math.pi/2
west=bpy.data.objects['West living wall'];west.location=(1.35,3.48,1.25);west.dimensions=(2.85,.16,2.5);west.name='Plain wall behind headboard'
for y in [.14,3.26]:box('West wall end return',(-.08,y,1.25),(.16,.28,2.5),cream)
builtin_before=set(bpy.data.objects)
# Built-in wall: fridge south, workstation middle, wardrobe north, facing +X
box('Compact white refrigerator',(.31,.43,.64),(.58,.59,1.28),white,.055)
for z,h in [(.47,.86),(1.1,.35)]:box('Refrigerator door',(.613,.43,z),(.035,.565,h),white,.018)
box('Microwave body',(.31,.43,1.47),(.5,.54,.32),white,.02);box('Microwave dark glass',(.567,.39,1.48),(.015,.39,.22),black)
box('Microwave display',(.58,.64,1.5),(.02,.07,.07),black)
box('Desk niche back',(.035,1.39,1.27),(.07,1.27,2.46),gray)
for y in [.77,2.04]:box('Niche upright',(.3,y,1.27),(.59,.055,2.46),gray)
box('Yellow desktop',(.35,1.40,.73),(.7,1.23,.055),yellow)
for z in [1.48,1.96,2.42]:box('Open storage shelf',(.265,1.40,z),(.52,1.22,.045),gray)
box('Shelf divider',(.27,1.42,1.96),(.5,.04,.9),gray)
box('Curved monitor body',(.28,1.42,1.08),(.08,.93,.52),black,.035);box('Screen charcoal glass',(.326,1.42,1.08),(.008,.88,.47),glass,.01)
box('Monitor stand',(.32,1.42,.81),(.1,.08,.12),black);box('Monitor foot',(.39,1.42,.755),(.21,.40,.02),black)
box('Keyboard',(.52,1.42,.775),(.18,.43,.025),black)
for j in range(5):
 for i in range(14):box('Keyboard key',(.448+j*.03,1.225+i*.028,.792),(.024,.024,.005),gray,.002)
sphere('Mouse',(.57,1.82,.79),(.05,.032,.025),black)
box('Racing wheel base',(.61,1.36,.84),(.24,.29,.12),black)
bpy.ops.mesh.primitive_torus_add(major_radius=.15,minor_radius=.022,major_segments=48,minor_segments=12,location=(.77,1.36,.91),rotation=(0,math.pi/2,0));bpy.context.object.name='Racing steering wheel';bpy.context.object.data.materials.append(black)
for a in [0,2.1,4.2]:tube('Steering spoke',[(.77,1.36,.91),(.77,1.36+.13*math.cos(a),.91+.13*math.sin(a))],.017,black)
box('PC tower',(.34,1.87,.33),(.46,.26,.61),black)
# office chair
box('Office chair seat',(.99,1.40,.46),(.49,.5,.09),black,.05);box('Office chair back',(1.22,1.4,.72),(.09,.49,.52),black,.045)
box('Chair back inset',(1.273,1.4,.72),(.022,.35,.35),gray,.04)
box('Chair back central black panel',(1.29,1.4,.72),(.02,.22,.26),black,.035)
cyl('Chair gas lift',(.98,1.40,.25),.035,.4,silver)
for a in range(5):
 end=(.98+.33*math.cos(a*1.256),1.4+.33*math.sin(a*1.256),.08);tube('Chair five star base',[(.98,1.4,.12),end],.022,silver);sphere('Caster',end,(.04,.04,.05),black)
# open shelf supplies (generic geometry, no private labels)
for i in range(8):
 m=mat('Book spine '+str(i),random.choice([(.14,.13,.11),(.7,.69,.61),(.3,.26,.2)]));box('Books',(.25,.88+i*.047,2.16),(.25,.04,random.uniform(.27,.4)),m,.002)
for z in [2.06,2.27]:cyl('Orange storage tub',(.25,1.68,z),.13,.2,orange)
for y in [1.03,1.24]:
 for z in [1.57,1.72]:box('White storage basket',(.29,y,z),(.36,.19,.13),white,.01)
for z in [1.57,1.73]:box('Translucent supplies box',(.3,1.70,z),(.35,.42,.14),white,.015)
# tall two-door yellow wardrobe
box('Wardrobe carcass',(.32,2.57,1.23),(.64,1.00,2.46),yellow)
for y in [2.32,2.82]:box('Yellow wardrobe door',(.65,y,1.23),(.045,.485,2.43),yellow)
for y in [2.53,2.61]:cyl('Tall silver wardrobe pull',(.686,y,1.23),.017,2.25,silver)
for y,m in [(2.35,blue),(2.84,linen)]:
 box('Hanging fabric shoulder bag',(.77,y,.87),(.18,.34,.37),m,.055);box('Shoulder bag front pocket',(.875,y,.85),(.025,.25,.20),m,.025);tube('Bag strap',[(.71,y-.12,.92),(.70,y-.12,1.58),(.70,y+.12,1.58),(.71,y+.12,.92)],.012,m)
# wardrobe bag trim and entry accessories
tube('Yellow stitched bag trim',[(.894,2.20,.91),(.894,2.20,.72),(.894,2.49,.72),(.894,2.49,.91)],.009,orange)
# Rotate the cabinet run onto the wall opposite the bed headboard.
# Preserve depth/height; shorten along run to generic object-based width estimate.
for o in [q for q in bpy.data.objects if q not in builtin_before]:
 x,y,z=o.location
 if o.type=='CURVE':
  for spl in o.data.splines:
   for pt in spl.points:
    xx,yy,zz,ww=pt.co;pt.co=(2.70-.85*yy,xx,zz,ww)
 else:
  o.location=(2.70-.85*y,x,z);o.rotation_euler.z+=math.pi/2;o.scale.y*=.85
# air conditioner over bed
box('Wall mounted air conditioner',(2.59,2.72,2.14),(.22,.78,.30),white,.08)
for z in [2.03,2.06,2.09]:box('Air conditioner vent',(2.466,2.72,z),(.009,.6,.011),gray,.001)
entry_before=set(bpy.data.objects)
box('Entry corridor wood floor',(1.1,-1.10,-.025),(2.2,2.2,.05),floor)
# Corridor and entry, kitchen on east side
box('Entry back wall',(1.05,-2.28,1.25),(2.25,.16,2.5),cream)
box('Entry door',(.72,-2.18,1.05),(.88,.07,2.1),gray,.025)
for x in [.24,1.20]:box('Door oak jamb',(x,-2.12,1.09),(.055,.09,2.18),wood)
box('Door header',(.72,-2.12,2.17),(1.02,.09,.065),wood)
box('Digital entry lock',(.40,-2.06,1.02),(.10,.06,.26),black);tube('Door handle',[(.40,-2.0,.92),(.54,-2.0,.92)],.015,silver)
box('Entry tile inset',(.73,-1.84,-.005),(1.0,.6,.055),gray);box('Orange welcome mat',(.73,-1.84,.025),(.90,.5,.012),orange)
for x in [.5,.72]:sphere('Mint house slippers',(x,-1.68,.065),(.085,.16,.04),mat('Mint slippers'+str(x),(.38,.57,.38)))
box('Kitchen east wall',(2.21,-1.1,1.25),(.14,2.2,2.5),cream)
for y in [-1.75,-1.16,-.56]:
 if y>-1.5:
  box('Kitchen lower cabinet',(1.86,y,.36),(.60,.58,.72),yellow)
  box('Kitchen base door',(1.545,y,.45),(.025,.55,.77),yellow)
 box('Overhead yellow cabinet',(1.97,y,1.91),(.43,.58,.90),yellow)
 box('Overhead cabinet front',(1.74,y,1.91),(.025,.55,.87),yellow)
countertop=box('Kitchen countertop',(1.83,-1.16,.89),(.68,1.82,.065),white)
# tiled backsplash and cooktop
for j in range(6):
 for k in range(3):box('White backsplash ceramic tile',(2.129,-2+j*.30,.99+k*.25),(.015,.294,.244),white,.003)
box('Black induction cooktop',(1.77,-1.76,.933),(.45,.43,.016),black)
# washer visible under cooktop
box('Front loading washing machine',(1.85,-1.78,.43),(.60,.57,.83),white,.03)
cyl('Washing machine steel rim',(1.535,-1.78,.42),.20,.035,silver,(0,math.pi/2,0));cyl('Washer black porthole',(1.511,-1.78,.42),.163,.015,glass,(0,math.pi/2,0))
box('Washer controls',(1.53,-1.78,.75),(.02,.5,.09),white);cyl('Washer dial',(1.50,-1.64,.75),.03,.015,silver,(0,math.pi/2,0))
# sink rim and recessed basin approximated with layered shape
rim=box('Steel sink rim',(1.83,-.79,.93),(.52,.64,.018),silver,.045)
cut=box('Temporary basin cutout',(1.83,-.79,.92),(.43,.55,.34),gray,.06)
for target in [countertop,rim]:
 mod=target.modifiers.new('Recessed sink opening','BOOLEAN');mod.operation='DIFFERENCE';mod.object=cut
 bpy.context.view_layer.objects.active=target;bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.data.objects.remove(cut,do_unlink=True)
vs=[]
for sx,sy,z in [(.214,.274,.93),(.15,.20,.775)]:
 for xx,yy in [(-sx,-sy),(sx,-sy),(sx,sy),(-sx,sy)]:vs.append((1.83+xx,-.79+yy,z))
fs=[(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7),(4,5,6,7)]
me=bpy.data.meshes.new('Deep sink bowl');me.from_pydata(vs,[],fs);o=bpy.data.objects.new('Recessed stainless basin',me);bpy.context.collection.objects.link(o);o.data.materials.append(silver);o.modifiers.new('Basin rounded seams','BEVEL').width=.025;o.modifiers.new('Basin shell','SOLIDIFY').thickness=.006
cyl('Sink drain',(1.83,-.79,.782),.04,.004,black)
tube('Chrome faucet',[(2.02,-.69,.95),(2.02,-.69,1.19),(1.96,-.69,1.25),(1.79,-.69,1.25),(1.76,-.69,1.18)],.018,silver)
for y,col in [(-.38,(.3,.45,.28)),(-.51,(.8,.72,.6))]:
 mm=mat('Soap bottle '+str(y),col);cyl('Dish soap bottle',(2.03,y,1.03),.037,.17,mm);box('Bottle dispenser',(2.03,y,1.13),(.08,.025,.025),black)
# Hanging pan, towel and wire dish rack seen in kitchenette
cyl('Hanging stainless frying pan',(2.09,-1.47,1.30),.12,.025,silver,(0,math.pi/2,0))
tube('Pan handle',[(2.08,-1.47,1.38),(2.08,-1.47,1.61)],.025,black)
for z in [1.02,1.21,1.40]:
 for x in [1.76,2.10]:tube('Dish rack side wire',[(x,-.27,z),(x,-.03,z)],.007,white)
 for y in [-.27,-.03]:tube('Dish rack shelf edge',[(1.76,y,z),(2.10,y,z)],.007,white)
 for x in [1.80,1.86,1.92,1.98,2.04]:tube('Dish rack shelf wire',[(x,-.27,z),(x,-.03,z)],.005,white)
for x in [1.76,2.10]:
 for y in [-.27,-.03]:tube('Dish rack upright',[(x,y,.98),(x,y,1.48)],.008,white)
for y in [-.21,-.12]:cyl('Stacked dish',(1.95,y,1.27),.085,.016,white,(math.pi/2,0,0))
# Sliding glass partition between room and kitchenette, opening at west
for x in [1.35,2.13]:box('Sliding partition oak stile',(x,.01,1.22),(.06,.09,2.44),wood)
box('Sliding partition lintel',(1.06,.01,2.43),(2.2,.1,.1),wood)
box('Frosted green partition glass',(1.75,.01,1.21),(.71,.025,2.28),mat('Frosted green privacy glass',(.15,.26,.20),.55))
# Bathroom to west of corridor, partial source coverage
bath=mat('Bathroom warm taupe tile',(.32,.30,.26),.65)
box('Bathroom floor',(-.77,-1.10,-.025),(1.55,2.2,.05),bath)
box('Bathroom west wall',(-1.62,-1.10,1.25),(.15,2.2,2.5),cream)
box('Bathroom rear wall',(-.78,-2.27,1.25),(1.7,.15,2.5),cream)
box('Bathroom divider south section',(-.02,-1.78,1.25),(.10,.76,2.5),cream)
box('Bathroom doorway lintel',(-.02,-.67,2.25),(.12,1.45,.5),cream)
# toilet at rear, sink nearer opening
sphere('Toilet ceramic base',(-1.14,-1.42,.22),(.20,.32,.25),white);sphere('Toilet bowl',(-1.14,-1.32,.43),(.25,.36,.13),white);sphere('Toilet seat',(-1.14,-1.32,.51),(.25,.34,.035),white);box('Toilet cistern',(-1.14,-1.74,.67),(.47,.20,.50),white,.07)
cyl('Sink pedestal',(-.63,-.47,.38),.105,.71,white);sphere('Bathroom sink',(-.63,-.47,.80),(.34,.25,.12),white);sphere('Sink recess',(-.63,-.47,.85),(.25,.17,.065),gray)
box('Bathroom mirror',(-1.535,-.48,1.43),(.035,.63,.80),silver)
tube('Bathroom faucet',[(-.77,-.47,.86),(-.77,-.47,1.02),(-.62,-.47,1.02)],.013,silver)
# Place the entry/kitchen beyond the opening beside the refrigerator.
for o in [q for q in bpy.data.objects if q not in entry_before]:
 if o.type=='CURVE':
  for spl in o.data.splines:
   for pt in spl.points:
    xx,yy,zz,ww=pt.co;pt.co=(2.70-yy,xx,zz,ww)
 else:
  x,y,z=o.location;o.location=(2.70-y,x,z);o.rotation_euler.z+=math.pi/2
for o in bpy.data.objects:
 if any(t in o.name for t in ['Sliding partition oak','Frosted green partition']):o.location.y-=.95
box('Bathroom doorway return wall',(3.10,-.02,1.25),(.80,.12,2.50),cream)
box('Bathroom left oak door jamb',(3.50,.02,1.09),(.06,.09,2.18),wood)
# main furnishing module
try:
 from furnishings import build_furnishings
 furn_groups=build_furnishings()
 for key in ['Desk','Chair']:
  furn_groups[key].rotation_euler.z=math.pi/2;furn_groups[key].location=(3.05,1.1,0)
except ImportError:pass
# Fine-scale surfaces catch light without relying on external textures.
for m in list(bpy.data.materials):
 if not m.use_nodes:continue
 p=m.node_tree.nodes.get('Principled BSDF')
 if not p:continue
 name=m.name.lower()
 if any(w in name for w in ['plaster','linen','fabric','cloth','duvet','pillow','bedding','wood floor','upholstery']):
  tex=m.node_tree.nodes.new('ShaderNodeTexNoise');tex.inputs['Scale'].default_value=180 if 'plaster' in name else 95;tex.inputs['Detail'].default_value=2
  bump=m.node_tree.nodes.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.18;bump.inputs['Distance'].default_value=.003
  m.node_tree.links.new(tex.outputs['Fac'],bump.inputs['Height']);m.node_tree.links.new(bump.outputs['Normal'],p.inputs['Normal'])
# lights and cameras
world=bpy.context.scene.world;world.use_nodes=True;world.node_tree.nodes['Background'].inputs[0].default_value=(.16,.18,.22,1);world.node_tree.nodes['Background'].inputs[1].default_value=.25
def area(n,l,power,size,color,target):
 d=bpy.data.lights.new(n,'AREA');d.energy=power;d.shape='DISK';d.size=size;d.color=color;o=bpy.data.objects.new(n,d);bpy.context.collection.objects.link(o);o.location=l;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
area('Ceiling warm diffuse',(1.65,1.7,2.40),100,1.2,(.86,.92,1),(1.6,1.7,0))
box('Ceiling light panel',(1.60,1.75,2.48),(.55,.65,.035),white)
area('Window soft cool fill',(.12,1.70,1.8),5,1.8,(.65,.75,1),(2,1.7,1))
area('Kitchen ceiling light',(3.8,.85,2.4),55,.7,(.9,.94,1),(3.7,1,0))
area('Bathroom soft light',(3.6,-.7,2.25),35,.4,(1,.90,.76),(3.7,-.7,0))
def camera(n,l,target,lens):
 d=bpy.data.cameras.new(n);o=bpy.data.objects.new(n,d);bpy.context.collection.objects.link(o);o.location=l;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();d.lens=lens;d.clip_start=.03;return o
cam=camera('01 Room from entry',(2.45,.82,1.52),(1.20,2.57,1.0),21)
camera('02 Workstation',(1.10,2.80,1.48),(1.32,.28,1.20),32)
camera('03 Kitchen view',(2.98,.45,1.57),(4.00,1.70,1.02),22)
camera('04 Bed and window',(.88,1.00,1.52),(1.96,2.78,.91),24)
scene=bpy.context.scene;scene.camera=cam;scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=256;scene.cycles.use_denoising=False;scene.render.resolution_x=1400;scene.render.resolution_y=1000;scene.render.resolution_percentage=100
scene.view_settings.exposure=-.45;scene.view_settings.view_transform='AgX';scene.view_settings.look='AgX - Medium High Contrast';scene.render.image_settings.file_format='PNG';scene.unit_settings.system='METRIC'
scene['reference']='21.32-second user-supplied walkthrough; no surveyed measurements';scene['scale_assumption']='1.1 x 2.0 m SS mattress used provisionally; main room 2.70 x 3.4 m; hidden geometry estimated. No loft shown in source.'
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(ROOT,'Home_Reconstruction.blend'))
# Convert curve details to exportable mesh; source blend retains editable curves.
bpy.ops.object.select_all(action='DESELECT')
for o in list(bpy.context.scene.objects):
 if o.type=='CURVE':
  o.select_set(True);bpy.context.view_layer.objects.active=o;bpy.ops.object.convert(target='MESH');o.select_set(False)
# export visible modeled objects with named materials
bpy.ops.export_scene.gltf(filepath=os.path.join(ROOT,'Home_Reconstruction.glb'),export_format='GLB',export_cameras=True,export_lights=True)
bpy.ops.export_scene.fbx(filepath=os.path.join(ROOT,'Home_Reconstruction.fbx'),object_types={'MESH'},apply_unit_scale=True,axis_forward='-Z',axis_up='Y',bake_anim=False)
if '--render' in sys.argv:
 for name in (['03 Kitchen view','04 Bed and window'] if '--remaining' in sys.argv else ['01 Room from entry','02 Workstation','03 Kitchen view','04 Bed and window']):
  scene.camera=bpy.data.objects[name];scene.render.filepath=os.path.join(ROOT,name[:2]+'_Render.png');bpy.ops.render.render(write_still=True)
