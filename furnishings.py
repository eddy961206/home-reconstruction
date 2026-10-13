"""Procedural furnishings reconstructed from the supplied home-video frames.

Call build_furnishings() from an existing Blender scene.  The module does not
alter the room, camera, render settings, or lights except the bedside bulb.
All created objects/materials use the FUR_ prefix.  Units are metres.
"""
import bpy
import math
import random
from mathutils import Vector

P = 'FUR_'
TAU = math.tau


def _mat(name, color, rough=.65, metal=0, fabric=False, checker=False):
    mat = bpy.data.materials.new(P + name)
    mat.diffuse_color = (*color, 1)
    mat.use_nodes = True
    ns, ls = mat.node_tree.nodes, mat.node_tree.links
    bs = ns.get('Principled BSDF')
    bs.inputs['Base Color'].default_value = (*color, 1)
    bs.inputs['Roughness'].default_value = rough
    bs.inputs['Metallic'].default_value = metal
    if fabric:
        bs.inputs['Sheen Weight'].default_value = .22
        tex = ns.new('ShaderNodeTexNoise')
        tex.inputs['Scale'].default_value = 240
        tex.inputs['Detail'].default_value = 2.0
        bump = ns.new('ShaderNodeBump')
        bump.inputs['Strength'].default_value = .16
        bump.inputs['Distance'].default_value = .0015
        ls.new(tex.outputs['Fac'], bump.inputs['Height'])
        ls.new(bump.outputs['Normal'], bs.inputs['Normal'])
        coarse = ns.new('ShaderNodeTexNoise')
        coarse.inputs['Scale'].default_value = 7
        coarse.inputs['Detail'].default_value = 3
        ramp = ns.new('ShaderNodeValToRGB')
        ramp.color_ramp.elements[0].position = .16
        ramp.color_ramp.elements[0].color = (*(c*.68 for c in color),1)
        ramp.color_ramp.elements[1].position = .82
        ramp.color_ramp.elements[1].color = (*(min(1,c*1.18+.015) for c in color),1)
        ls.new(coarse.outputs['Fac'], ramp.inputs['Fac'])
        ls.new(ramp.outputs['Color'], bs.inputs['Base Color'])
    if checker:
        tex = ns.new('ShaderNodeTexChecker')
        tex.inputs['Color1'].default_value = (.51,.47,.41,1)
        tex.inputs['Color2'].default_value = (.89,.865,.79,1)
        tex.inputs['Scale'].default_value = 9
        ls.new(tex.outputs['Color'], bs.inputs['Base Color'])
    return mat


def _assign(obj, name, mat, parent):
    obj.name = P + name
    if mat:
        obj.data.materials.append(mat)
    if parent:
        obj.parent = parent
    return obj


def _empty(name, parent=None):
    ob = bpy.data.objects.new(P+name, None)
    bpy.context.collection.objects.link(ob)
    if parent:
        ob.parent = parent
    return ob


def _box(name, loc, dims, mat, parent, bevel=.01):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    ob = _assign(bpy.context.object,name,mat,parent)
    ob.dimensions = dims
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if bevel:
        m = ob.modifiers.new('soft manufactured edges','BEVEL')
        m.width = bevel
        m.segments = 3
        m = ob.modifiers.new('weighted corner normals','WEIGHTED_NORMAL')
    return ob


def _mesh(name, verts, faces, mat, parent, smooth=True):
    me = bpy.data.meshes.new(P+name+'_mesh')
    me.from_pydata(verts, [], faces)
    me.update()
    ob = bpy.data.objects.new(P+name, me)
    bpy.context.collection.objects.link(ob)
    _assign(ob,name,mat,parent)
    if smooth:
        for p in me.polygons:
            p.use_smooth = True
    return ob


def _sphere(name, loc, dims, mat, parent, seg=32):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=seg, ring_count=16, radius=1, location=loc)
    ob = _assign(bpy.context.object,name,mat,parent)
    ob.scale = dims
    for poly in ob.data.polygons:
        poly.use_smooth=True
    return ob


def _rod(name, a, b, radius, mat, parent, vertices=16):
    a,b = Vector(a),Vector(b)
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius,
                                      depth=(b-a).length, location=(a+b)/2)
    ob = _assign(bpy.context.object,name,mat,parent)
    ob.rotation_euler = (b-a).to_track_quat('Z','Y').to_euler()
    for p in ob.data.polygons:
        p.use_smooth=True
    be = ob.modifiers.new('end rounding','BEVEL')
    be.width=radius*.2
    be.segments=2
    return ob


def _curve(name, pts, radius, mat, parent, closed=False):
    cu = bpy.data.curves.new(P+name+'_curve','CURVE')
    cu.dimensions='3D'
    cu.resolution_u=3
    cu.bevel_depth=radius
    cu.bevel_resolution=3
    sp = cu.splines.new('POLY')
    sp.points.add(len(pts)-1)
    for p,co in zip(sp.points,pts):
        p.co=(*co,1)
    sp.use_cyclic_u=closed
    ob=bpy.data.objects.new(P+name,cu)
    bpy.context.collection.objects.link(ob)
    _assign(ob,name,mat,parent)
    return ob


def _cloth(name, nu, nv, fn, mat, parent, thickness=.006, subd=1):
    verts=[fn(i/nu,j/nv) for j in range(nv+1) for i in range(nu+1)]
    faces=[]
    for j in range(nv):
        for i in range(nu):
            k=j*(nu+1)+i
            faces.append((k,k+1,k+nu+2,k+nu+1))
    ob=_mesh(name,verts,faces,mat,parent)
    if subd:
        m=ob.modifiers.new('fabric soft folds','SUBSURF')
        m.levels=subd
        m.render_levels=subd
    m=ob.modifiers.new('stitched fabric thickness','SOLIDIFY')
    m.thickness=thickness
    m.offset=0
    return ob


def _pillow(name, center, dims, mat, parent, rotation=0, crease=.006):
    # Superellipsoid makes a gently squared and fully stuffed sewn cushion.
    c=Vector(center)
    def spow(v,e):
        return math.copysign(abs(v)**e,v)
    nr,ns=30,72
    vs=[]
    for j in range(nr+1):
        lat=-math.pi/2+math.pi*j/nr
        for i in range(ns):
            t=TAU*i/ns
            x=dims[0]/2*spow(math.cos(lat),.52)*spow(math.cos(t),.58)
            y=dims[1]/2*spow(math.cos(lat),.52)*spow(math.sin(t),.58)
            z=dims[2]/2*spow(math.sin(lat),.60)
            z += crease*math.sin(t*16+lat*8)*math.exp(-abs(math.sin(lat))*4)
            z += crease*.6*math.sin(t*9+lat*4)
            vs.append((c.x+x*math.cos(rotation)-y*math.sin(rotation),
                       c.y+x*math.sin(rotation)+y*math.cos(rotation),c.z+z))
    fs=[]
    for j in range(nr):
        for i in range(ns):
            a=j*ns+i;b=j*ns+(i+1)%ns
            fs.append((a,b,b+ns,a+ns))
    ob=_mesh(name,vs,fs,mat,parent)
    seam=[]
    for i in range(ns):
        t=TAU*i/ns
        x=dims[0]/2*spow(math.cos(t),.58)
        y=dims[1]/2*spow(math.sin(t),.58)
        seam.append((c.x+x*math.cos(rotation)-y*math.sin(rotation),
                     c.y+x*math.sin(rotation)+y*math.cos(rotation),c.z))
    _curve(name+'_perimeter_seam',seam,.0017,mat,parent,True)
    return ob


def build_furnishings():
    """Build the bed, drawer unit, drying rack, desk and folding chair.

    Returns a dictionary of group empties.  Their child geometry uses room
    world coordinates; translate a group to reposition the complete piece.
    """
    random.seed(89)
    root=_empty('Furnishings')
    groups={key:_empty(key,root) for key in ('Bed','Bedside','DryingRack','Desk','Chair')}
    groups['root']=root
    m={
      'gray':_mat('gray duvet woven cloth',(.34,.355,.38),fabric=True),
      'charcoal':_mat('charcoal upholstered headboard',(.105,.115,.14),fabric=True),
      'piping':_mat('light gray upholstery piping',(.42,.43,.43),fabric=True),
      'sage':_mat('sage teal bedsheet',(.23,.36,.36),fabric=True),
      'leaf':_mat('bedsheet pale botanical pattern',(.57,.64,.60),fabric=True),
      'butter':_mat('pale butter yellow body pillow',(.77,.72,.45),fabric=True),
      'pillow':_mat('warm gray pillow',(.53,.51,.48),fabric=True),
      'white':_mat('offwhite enamel',(.86,.86,.82),rough=.36),
      'steel':_mat('drying rack silver',(.65,.69,.7),rough=.27,metal=.72),
      'black':_mat('soft black plastic',(.035,.043,.05),rough=.45),
      'blue':_mat('blue terrycloth towel',(.21,.36,.51),fabric=True),
      'plaid':_mat('cream taupe gingham towel',(.66,.61,.52),fabric=True,checker=True),
      'cream':_mat('cream cotton',(.81,.79,.71),fabric=True),
      'darkcloth':_mat('dark laundry',(.035,.045,.06),fabric=True),
      'drawer':_mat('warm gray drawer plastic',(.58,.57,.52),rough=.42),
      'drawerfront':_mat('translucent drawer face',(.72,.71,.65),rough=.38),
      'orange':_mat('orange snack packet',(.93,.25,.027),rough=.35),
      'green':_mat('lime green tumbler',(.37,.67,.025),rough=.28),
      'brown':_mat('tan plush fur',(.47,.29,.11),fabric=True),
      'plushgray':_mat('gray plush fur',(.26,.34,.35),fabric=True),
    }
    _build_bed(groups['Bed'],m)
    _build_bedside(groups['Bedside'],m)
    _build_rack(groups['DryingRack'],m)
    _build_desk(groups['Desk'],groups['Chair'],m)
    # Final plan calibration: 2.70 m clear interior width.
    groups['Bed'].location.x = -.45
    groups['Bedside'].location.x = -.45
    groups['DryingRack'].location.x = -.40
    return groups


def _build_bed(g,m):
    cx=2.565
    _box('bed_base',(cx,2.15,.205),(1.105,2.02,.29),m['charcoal'],g,.035)
    for x in (2.11,3.02):
        for y in (1.24,3.02):
            _rod('bed_short_foot',(x,y,.04),(x,y,.16),.035,m['black'],g)
    _box('thick_mattress',(cx,2.15,.40),(1.085,1.99,.225),m['sage'],g,.065)
    # Subtle mattress perimeter piping and a lightly rumpled fitted top.
    pts=[]
    for x,y in ((2.065,1.19),(3.065,1.19),(3.09,1.23),(3.09,3.08),(3.04,3.13),(2.08,3.13),(2.035,3.08),(2.035,1.24)):
        pts.append((x,y,.443))
    _curve('mattress_piping',pts,.004,m['leaf'],g,True)
    def sheet(u,v):
        x=2.027+1.075*u;y=1.17+1.96*v
        return (x,y,.514+.006*math.sin(x*51+y*15)+.004*math.sin(y*60-x*5))
    _cloth('fitted_sheet',36,64,sheet,m['sage'],g,.003)
    # Actual surface motifs, instead of a featureless solid green mattress.
    for i in range(85):
        x=random.uniform(2.045,3.085); y=random.uniform(1.20,3.12)
        z=sheet((x-2.027)/1.075,(y-1.17)/1.96)[2]+.004
        ang=random.random()*TAU
        length=random.uniform(.024,.058); width=length*.26
        verts=[]
        for j in range(15):
            t=TAU*j/15
            a=length*.5*math.cos(t);b=width*.5*math.sin(t)
            verts.append((x+a*math.cos(ang)-b*math.sin(ang),y+a*math.sin(ang)+b*math.cos(ang),z))
        _mesh('sheet_leaf_%02d'%i,verts,[tuple(range(15))],m['leaf'],g,False)
    # Arched upholstered headboard, its top rises smoothly toward the centre.
    outline=[(2.004,.34),(3.126,.34),(3.126,.76)]
    outline += [(cx+.561*math.cos(t),.76+.255*math.sin(t)) for t in [math.pi*k/48 for k in range(1,49)]]
    vs=[(x,y,z) for y in (3.11,3.225) for x,z in outline]
    n=len(outline)
    fs=[tuple(range(n-1,-1,-1)),tuple(range(n,2*n))]
    fs += [(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
    ob=_mesh('arched_upholstered_headboard',vs,fs,m['charcoal'],g)
    b=ob.modifiers.new('rounded upholstered edge','BEVEL');b.width=.037;b.segments=5
    ob.modifiers.new('weighted cushion normals','WEIGHTED_NORMAL')
    pipe=[(cx+.532*math.cos(math.pi*i/64),3.068,.54+.172*math.sin(math.pi*i/64)) for i in range(65)]
    _curve('headboard_sweeping_piping',pipe,.0045,m['piping'],g)
    _curve('headboard_center_seam',[(cx,3.066,.47),(cx-.004,3.066,.76),(cx,3.073,.976)],.002,m['black'],g)
    for x in (2.29,2.83):
        _curve('headboard_panel_dart',[(x,3.071,.60),(x-.012,3.061,.8),(x-.02,3.081,.941)],.0018,m['charcoal'],g)
    # Thick, crumpled duvet concentrated on the left with deep lengthwise folds.
    def duvet(u,v):
        y=1.075+1.79*v+.032*math.sin(u*17+v*5)
        x=1.96+.88*u+.065*math.sin(v*6)-.018*math.cos(v*18+u*9)
        z=.55+.022*math.sin(u*22+v*7+2.3*math.sin(v*9))+.011*math.sin(u*49-v*16+math.sin(v*17))
        z+=.095*math.exp(-((u-.25)/.25)**2-((v-.32)/.19)**2)-.030*math.exp(-((u-.65)/.20)**2-((v-.50)/.23)**2)
        z+=.094*math.exp(-((u-.45-.12*math.sin(v*8))/.10)**2)
        z+=.12*math.exp(-((v-.88)/.16)**2)*(.6+.4*math.sin(u*9))
        z+=.004*math.sin(u*78+v*29)+.003*math.sin(u*37-v*60)
        z-=.27*max(0,1-u/.15)**1.5
        z-=.15*max(0,1-v/.12)**1.4
        z+=.032*math.sin(v*24)*math.exp(-u*9)
        return (x,y,z)
    _cloth('rumpled_gray_duvet',74,108,duvet,m['gray'],g,.017,1)
    _curve('duvet_left_hem',[duvet(0,i/110) for i in range(111)],.005,m['gray'],g)
    _curve('duvet_foot_hem',[duvet(i/74,0) for i in range(75)],.005,m['gray'],g)
    # The long pale yellow curved pillow is a closed soft tube, with end caps.
    vs=[];fs=[];nt=90;nr=32
    for j in range(nt+1):
        t=j/nt
        x=2.865-.15*math.sin(t*math.pi)+.05*math.sin(t*TAU)
        y=1.43+1.12*t
        z=.615+.045*math.sin(t*math.pi)
        rad=(.105+.035*math.sin(t*math.pi))*max(.09,math.sin(math.pi*t)**.20)
        for k in range(nr):
            a=TAU*k/nr
            r=rad*(1+.022*math.sin(a*9+t*70))
            vs.append((x+r*math.cos(a),y+.022*math.sin(a*3+t*16),z+r*.77*math.sin(a)))
    for j in range(nt):
        for k in range(nr):
            a=j*nr+k;b=j*nr+(k+1)%nr
            fs.append((a,b,b+nr,a+nr))
    fs.extend([tuple(range(nr-1,-1,-1)),tuple(nt*nr+k for k in range(nr))])
    _mesh('curved_pale_yellow_body_pillow',vs,fs,m['butter'],g)
    _pillow('loose_gray_pillow',(2.79,1.37,.61),(.62,.46,.16),m['pillow'],g,-.16)
    _pillow('head_gray_pillow',(2.63,2.965,.564),(.70,.36,.13),m['gray'],g,.035)
    # Small recognisable plush silhouettes at the head of the bed.
    _sphere('gray_plush_body',(2.70,2.89,.68),(.087,.068,.105),m['plushgray'],g)
    _sphere('gray_plush_belly',(2.70,2.827,.67),(.056,.014,.069),m['cream'],g)
    for x in (2.66,2.735):
        _sphere('gray_plush_ear',(x,2.9,.79),(.025,.022,.065),m['plushgray'],g)
        _sphere('gray_plush_eye',(x,2.832,.727),(.008,.007,.009),m['black'],g,16)
    _sphere('tan_plush_body',(2.51,2.89,.654),(.074,.055,.091),m['brown'],g)
    for x in (2.455,2.56):
        _sphere('tan_plush_ear',(x,2.885,.731),(.024,.021,.036),m['cream'],g)
    _sphere('white_plush_body',(3.00,2.77,.653),(.073,.12,.077),m['cream'],g)
    _sphere('white_plush_head',(3.00,2.883,.69),(.07,.07,.07),m['cream'],g)
    _curve('white_plush_yellow_band',[(3.00+.074*math.cos(TAU*i/48),2.784,.653+.074*math.sin(TAU*i/48)) for i in range(49)],.016,m['butter'],g,True)


def _build_bedside(g,m):
    x,y=1.805,3.035
    _box('drawer_tower_frame',(x,y,.316),(.385,.43,.60),m['drawer'],g,.013)
    for k in range(4):
        z=.098+k*.142
        _box('plastic_drawer_%d'%k,(x,y-.011,z),(.354,.418,.123),m['drawerfront'],g,.011)
        _box('drawer_recess_%d'%k,(x,y-.224,z+.039),(.198,.011,.013),m['drawer'],g,.006)
        _box('drawer_pull_%d'%k,(x,y-.233,z+.046),(.19,.024,.012),m['white'],g,.005)
    _box('drawer_dark_top',(x,y,.63),(.402,.445,.026),m['black'],g,.006)
    # Compact bulb lamp on a black stalk and warm amber base.
    _rod('lamp_base',(1.90,3.075,.652),(1.90,3.075,.673),.065,m['brown'],g,32)
    _rod('lamp_stem',(1.90,3.075,.67),(1.90,3.075,.791),.014,m['black'],g)
    glow=_mat('warm opal bedside bulb',(1,.77,.40),rough=.28)
    bs=glow.node_tree.nodes.get('Principled BSDF')
    bs.inputs['Emission Color'].default_value=(1,.51,.16,1)
    bs.inputs['Emission Strength'].default_value=2.8
    _sphere('warm_bulb',(1.90,3.075,.828),(.039,.039,.056),glow,g)
    data=bpy.data.lights.new(P+'bedside_bulb','POINT');data.energy=7;data.color=(1,.59,.27);data.shadow_soft_size=.05
    ob=bpy.data.objects.new(P+'bedside_bulb',data);bpy.context.collection.objects.link(ob);ob.location=(1.90,3.075,.844);ob.parent=g
    # Round tabletop mirror, silver face enclosed by a white halo.
    _rod('mirror_stand',(1.716,2.975,.656),(1.716,2.975,.811),.011,m['steel'],g)
    _rod('mirror_base',(1.716,2.973,.652),(1.716,2.973,.658),.055,m['white'],g,32)
    mirror=_mat('mirror reflective face',(.73,.78,.81),rough=.065,metal=1)
    _rod('mirror_disc',(1.716,2.972,.888),(1.716,2.958,.888),.082,mirror,g,64)
    _curve('mirror_white_ring',[(1.716+.087*math.cos(TAU*i/72),2.947,.888+.087*math.sin(TAU*i/72)) for i in range(73)],.008,m['white'],g,True)
    _box('bedside_remote',(1.78,2.875,.659),(.04,.102,.016),m['white'],g,.006)
    for j in range(4):
        _sphere('remote_button',(1.78,2.850+j*.011,.669),(.005,.005,.002),m['black'],g,12)
    _curve('charger_cable',[(1.82,2.92,.655),(1.82,2.81,.645),(1.9,2.78,.49),(1.87,2.795,.28),(1.88,2.87,.10)],.0025,m['black'],g)


def _build_rack(g,m):
    # A compact, densely loaded metal multi-tier indoor drying rack.
    x1,x2=.70,1.535
    for x in (x1,x2):
        _rod('rack_front_upright',(x,2.90,.045),(x,2.995,1.77),.012,m['steel'],g)
        _rod('rack_rear_upright',(x,3.29,.045),(x,3.215,1.77),.012,m['steel'],g)
        _rod('rack_foot',(x,2.82,.043),(x,3.33,.043),.019,m['black'],g)
        for z in (.32,.86,1.73):
            _rod('rack_side_bar',(x,2.925,z),(x,3.26,z),.011,m['steel'],g)
    for z in (.30,.86,1.73):
        for y in (2.935,3.085,3.235):
            _rod('rack_drying_rail',(x1,y,z),(x2,y,z),.009,m['steel'],g)
    for i in range(6):
        xx=.73+i*.154
        _rod('rack_lower_shelf_rail',(xx,2.94,.30),(xx,3.235,.30),.006,m['steel'],g)
    # Dark stored bins/cloths under the crossbars and teal folded textile.
    _box('rack_lower_dark_bin',(1.12,3.065,.48),(.70,.29,.30),m['black'],g,.022)
    _box('rack_upper_dark_laundry',(1.10,3.09,1.08),(.69,.29,.25),m['darkcloth'],g,.04)
    _pillow('rack_folded_teal_cloth',(1.11,3.065,1.225),(.76,.32,.085),m['sage'],g)
    # Front towel is clearly taupe/cream checked, with wavy hems and folds.
    def plaid(u,v):
        return (.70+.82*u,2.84+.023*math.sin(u*38)+.018*math.sin(v*9+u*8),
                1.225-.48*v+.012*math.sin(u*26)+.014*math.sin(u*12+v*4)*v)
    _cloth('gingham_towel_front',52,36,plaid,m['plaid'],g,.004)
    _curve('gingham_bottom_hem',[plaid(i/75,1) for i in range(76)],.004,m['cream'],g)
    # Blue bath towel folded over the top rail, with textured scalloped hem.
    def blue(u,v):
        y=3.045-.047*math.sin(min(v*4,1)*math.pi/2)
        y+=.014*math.sin(u*28+v*3)+.006*math.sin(u*55-v*9)
        return (.90+.49*u,y,1.756-.48*v+.012*math.sin(u*33)*v)
    _cloth('blue_bath_towel',52,48,blue,m['blue'],g,.008)
    _curve('blue_towel_hem',[blue(i/70,1) for i in range(71)],.005,m['blue'],g)
    def dark(u,v):
        return (.725+.21*u,3.06+.009*math.sin(u*18+v*5),1.75-.39*v+.009*math.sin(u*23)*v)
    _cloth('dark_hanging_tshirt',24,36,dark,m['darkcloth'],g,.005)
    for h in (.80,.86,.92):
        _curve('shirt_white_stripe',[dark(i/30,h) for i in range(31)],.004,m['cream'],g)
    # Clothes hangers and loose pale socks at the right of the rack.
    for idx,(x,y,z) in enumerate(((1.40,3.12,1.65),(1.48,3.20,1.71),(1.31,3.23,1.63))):
        _curve('hanger_%d'%idx,[(x,y,z),(x-.13,y,z-.13),(x+.13,y,z-.13),(x,y,z)],.003,m['cream'],g)
        _curve('hanger_hook_%d'%idx,[(x,y,z),(x,y,z+.07),(x+.025,y,z+.09),(x+.038,y,z+.07)],.003,m['cream'],g)
    for j in range(2):
        xx=1.395+j*.069
        def sock(u,v,xx=xx,j=j):
            return (xx+.046*u+.015*math.sin(v*4),3.018+.008*math.sin(u*9+v*15),1.46-.31*v+.008*math.sin(u*10+j))
        _cloth('pale_hanging_sock_%d'%j,10,30,sock,m['cream'],g,.005)
    _curve('rack_black_power_cord',[(1.45,2.88,.76),(1.52,2.84,.67),(1.55,2.82,.37),(1.55,2.87,.05)],.003,m['black'],g)


def _build_desk(g,c,m):
    _box('white_narrow_desktop',(.75,2.455,.733),(1.20,.51,.035),m['white'],g,.007)
    wood=_mat('exposed_plywood_edge',(.60,.48,.34),rough=.6)
    _box('desktop_front_plywood_edge',(.75,2.199,.727),(1.195,.004,.024),wood,g,.002)
    for x in (.20,1.30):
        for y in (2.24,2.67):
            _rod('white_desk_leg',(x,y,.029),(x,y,.712),.026,m['white'],g,24)
            _rod('desk_leg_floor_cap',(x,y,.012),(x,y,.039),.028,m['black'],g,24)
    # Compact aluminum folding chair, gray vinyl seat/back, tubular bent frame.
    cx,cy=.73,1.91
    seat=_mat('folding_chair_gray_vinyl',(.41,.43,.43),rough=.47)
    _box('folding_chair_seat',(cx,cy,.425),(.365,.35,.048),seat,c,.027)
    _box('folding_chair_back',(cx,cy-.175,.685),(.382,.045,.17),seat,c,.033)
    for x in (cx-.196,cx+.196):
        _curve('chair_outer_tube',[(x,cy+.16,.04),(x,cy+.17,.08),(x,cy+.065,.44),
               (x,cy-.19,.715),(x,cy-.20,.765)],.013,m['white'],c)
        _curve('chair_crossed_leg',[(x,cy-.22,.04),(x,cy-.225,.09),(x,cy+.12,.44)],.013,m['white'],c)
        _sphere('chair_hinge',(x,cy+.015,.36),(.018,.018,.018),m['black'],c,16)
    _curve('chair_rear_floor_loop',[(cx-.196,cy-.22,.06),(cx-.18,cy-.24,.035),
           (cx+.18,cy-.24,.035),(cx+.196,cy-.22,.06)],.014,m['white'],c)
    _curve('chair_top_frame',[(cx-.196,cy-.195,.714),(cx-.196,cy-.195,.761),
           (cx-.16,cy-.195,.791),(cx+.16,cy-.195,.791),(cx+.196,cy-.195,.761),
           (cx+.196,cy-.195,.714)],.013,m['white'],c)
    # Green insulated tumbler and napkin on the left, snack packets on right.
    _rod('lime_green_tumbler',(.34,2.54,.755),(.34,2.54,.944),.033,m['green'],g,48)
    _rod('tumbler_stainless_lip',(.34,2.54,.94),(.34,2.54,.952),.0345,m['steel'],g,48)
    _rod('tumbler_dark_inside',(.34,2.54,.952),(.34,2.54,.953),.029,m['black'],g,48)
    paper=_mat('white_tissue_paper',(.92,.92,.88),rough=.92)
    def tissue(u,v):
        return (.15+.22*u,2.36+.17*v,.756+.012*math.sin(u*18+v*3)**2+.015*math.sin(v*16+u*7)**2)
    _cloth('crumpled_white_napkin',22,22,tissue,paper,g,.001,1)
    _rod('blue_pen',(.205,2.565,.755),(.34,2.583,.755),.0035,m['blue'],g)
    for i,(x,y,a) in enumerate(((.99,2.48,.23),(1.19,2.49,-.20))):
        _pillow('orange_snack_packet_%d'%i,(x,y,.77),(.20,.145,.031),m['orange'],g,a,crease=.004)
        ob=_box('packet_cream_label_%d'%i,(x,y,.79),(.108,.056,.0015),m['cream'],g,.002)
        ob.rotation_euler.z=a
        for k in range(3):
            ob=_box('packet_print_%d_%d'%(i,k),(x-.024+k*.020,y,.792),(.009,.039,.0018),m['black'],g,.001)
            ob.rotation_euler.z=a
    _mesh('torn_orange_wrapper',[(1.24,2.60,.754),(1.30,2.615,.754),(1.28,2.65,.758),(1.25,2.638,.76)],[(0,1,2,3)],m['orange'],g,False)

