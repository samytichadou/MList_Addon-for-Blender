bl_info = {  
 "name": "MList",  
 "author": "Samy Tichadou (tonton)",  
 "version": (1, 0),  
 "blender": (2, 7, 8),  
 "location": "Toolshelf > Animation Tab",  
 "description": "Add Marker List and Marker Utilities in 3D View",  
 "warning": "",
 "wiki_url": "http://www.samytichadou.com",  
 "tracker_url": "http://www.samytichadou.com/moi",  
 "category": "3D View"}



import bpy
from bpy.props import IntProperty, CollectionProperty , StringProperty 
from bpy.types import Panel, UIList
import os
import csv
import datetime
from bpy_extras.io_utils import ImportHelper


# -------------------------------------------------------------------
# draw
# -------------------------------------------------------------------

# custom list
class Markerlist_Items(UIList):

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        layout.prop(item, "name", text="", icon='MARKER',  emboss=False, translate=False)
                
    def invoke(self, context, event):
        pass   

# draw the panel
class MarkerListPanel(Panel):
    """Creates a Panel in the Object properties window"""
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_category = "Animation"
    bl_label = "Marker List"

    def draw(self, context):
        layout = self.layout
        scene = bpy.context.scene
        mlist = scene.markerlist
        tlmlist = scene.timeline_markers
        idx = scene.marker_index
        ts = bpy.context.tool_settings
    
        row = layout.row()
        row.label("Edit Names Below", icon='ERROR')
        rows = 3
        row = layout.row()
        row.template_list("Markerlist_Items", "", scene, "markerlist", scene, "marker_index", rows=rows)
        row = layout.row(align=True)
        row.operator("markerlist.goto_previous", icon="TRIA_LEFT", text="")
        row.operator("markerlist.goto_next", icon="TRIA_RIGHT", text="")
        row.separator()
        if (idx+1) <= len(mlist) and len(mlist) != 0:
            if scene.markerlist[idx].comment != "No Comment":
                row.menu("Menu_Read_Comment", icon="COLLAPSEMENU", text="")
            else:
                row.menu("Menu_Read_Comment", icon="ZOOMOUT", text="")
            row.label(str(scene.markerlist[idx].frame), icon='TIME')
        row = layout.row(align=True)
        row.operator("markerlist.refresh", icon="FILE_REFRESH", text="")
        row.operator("markerlist.jump_to", icon="FF", text="")
        row.operator("markerlist.select_marker", icon="MARKER_HLT", text="")
        if ts.lock_markers==True:
            row.prop(ts, "lock_markers", icon='LOCKED', text="")
        else:
            row.prop(ts, "lock_markers", icon='UNLOCKED', text="")
        row.separator()
        row.operator("markerlist.delete_marker", icon="ZOOMOUT", text="")
        row.operator("markerlist.add_marker", icon="ZOOMIN", text="")
        row.separator()
        row.operator("markerlist.import_transcript", icon='PASTEDOWN', text="")
        if len(mlist) != 0:
            row.operator("markerlist.save_transcript", icon='COPYDOWN', text="")
        row = layout.row(align=True)
        if len(mlist) != 0:
            row = layout.row(align=True)
            row.menu("Menu_CopyMarkers_ToScene", text='Copy to')
            row.prop(context.scene, "markerlist_copyall", text='All Markers')
            
        
# refresh marker list button
class Markerlist_refresh(bpy.types.Operator):
    bl_idname = "markerlist.refresh"
    bl_label = "Refresh Markers"
    bl_description = "Refresh Markers and Apply Names to Timeline"
        
    def execute(self, context):
        scene=bpy.context.scene
        mlist=scene.markerlist
        framelist=[]
        Oframelist=[]
        Ocommentlist=[]
        for nm in mlist:
            for m in scene.timeline_markers:
                if nm.frame==m.frame:
                    m.name=nm.name
                elif nm.name==m.name:
                    nm.frame=m.frame
            Oframelist.append(nm.frame)
            Ocommentlist.append(nm.comment)
        for i in range(len(mlist)-1,-1,-1):
                mlist.remove(i)
        for m in scene.timeline_markers:
            framelist.append(m.frame)
        framelist.sort()
        for fm in framelist:
            newmarker=mlist.add()
            newmarker.frame=fm
        for nm in mlist:
            for m in scene.timeline_markers:
                if nm.frame==m.frame:
                    nm.name=m.name
            for of in Oframelist:
                if nm.frame==of:
                    indx=Oframelist.index(of)
                    nm.comment=Ocommentlist[indx]
        info = 'Markers List refreshed'
        self.report({'INFO'}, info)
        
        return {'FINISHED'} 
    
# jumpto button
class Markerlist_jumpto(bpy.types.Operator):
    bl_idname = "markerlist.jump_to"
    bl_label = "Jump to Marker"
    bl_description = "Jump to selected Marker"

    def execute(self, context):
        scene=bpy.context.scene
        idx=scene.marker_index
        mlist = scene.markerlist
        tlmlist = scene.timeline_markers
        if (idx+1) > len(mlist):
            info = 'Please select a marker'
            self.report({'ERROR'}, info)
        else :
            of = mlist[bpy.context.scene.marker_index].frame
            bpy.ops.markerlist.refresh()
            if (idx+1) > len(mlist):
                info = 'Marker no longer exists'
                self.report({'ERROR'}, info)
            else:
                nf = mlist[bpy.context.scene.marker_index].frame
                if of==nf:
                    newF = mlist[bpy.context.scene.marker_index].frame
                    scene.frame_current=newF
                    for m in tlmlist :
                        m.select=False
                        if m.frame==newF:
                            m.select=True
                else:
                    info = 'Marker no longer exists'
                    self.report({'ERROR'}, info)
        
        return{'FINISHED'}
    
# select button
class Markerlist_select(bpy.types.Operator):
    bl_idname = "markerlist.select_marker"
    bl_label = "Select Marker"
    bl_description = "Select Marker on Timeline"
        
    def execute(self, context):
        scene=bpy.context.scene
        idx=scene.marker_index
        mlist = scene.markerlist
        tlmlist = scene.timeline_markers
        if (idx+1) > len(mlist):
            info = 'Please select a marker'
            self.report({'ERROR'}, info)
        else :
            of = mlist[bpy.context.scene.marker_index].frame
            bpy.ops.markerlist.refresh()
            if (idx+1) > len(mlist):
                info = 'Marker no longer exists'
                self.report({'ERROR'}, info)
            else:
                nf = mlist[bpy.context.scene.marker_index].frame
                if of==nf:
                    for m in bpy.context.scene.timeline_markers:
                        m.select=False
                    lmarker = bpy.context.scene.markerlist[bpy.context.scene.marker_index]
                    for m in bpy.context.scene.timeline_markers:
                        if m.frame==lmarker.frame:
                            m.select=True
                else:
                    info = 'Marker no longer exists'
                    self.report({'ERROR'}, info)
            
        return {'FINISHED'} 
    
# add marker button
class Markerlist_add(bpy.types.Operator):
    bl_idname = "markerlist.add_marker"
    bl_label = "Add Marker"
    bl_description = "Add Marker for Current Frame"
        
    def execute(self, context):
        scene=bpy.context.scene
        mlist=scene.markerlist
        framelist=[]
        check=0
        
        for nm in scene.timeline_markers:
            nm.select=False
            if nm.frame==scene.frame_current:
                info = 'Markers already exists'
                self.report({'ERROR'}, info)
                check=1
        if check==0:
            Ocontext=bpy.context.area.type
            bpy.context.area.type='TIMELINE'
            bpy.ops.marker.add()
            bpy.context.area.type=Ocontext
            bpy.ops.markerlist.refresh()
            for nm in scene.timeline_markers:
                if nm.select==True:
                    Nmarker=nm
            for m in mlist:
                framelist.append(m.frame)
            for f in framelist:
                if f==Nmarker.frame:
                    scene.marker_index=framelist.index(f)
                    
            info = 'Marker created'
            self.report({'INFO'}, info)
        
        return {'FINISHED'} 

# delete marker button
class Markerlist_delete(bpy.types.Operator):
    bl_idname = "markerlist.delete_marker"
    bl_label = "Delete Marker"
    bl_description = "Delete selected Marker"
        
    def execute(self, context):
        scene=bpy.context.scene
        idx=scene.marker_index
        mlist = scene.markerlist
        tlmlist = scene.timeline_markers
        if (idx+1) > len(mlist):
            info = 'Please select a marker'
            self.report({'ERROR'}, info)
        else :
            of = mlist[bpy.context.scene.marker_index].frame
            bpy.ops.markerlist.refresh()
            if (idx+1) > len(mlist):
                info = 'Marker no longer exists'
                self.report({'ERROR'}, info)
            else:
                nf = mlist[bpy.context.scene.marker_index].frame
                if of==nf:
                    if len(bpy.context.scene.timeline_markers) > 0:
                        for m in bpy.context.scene.timeline_markers:
                            m.select=False
                        for m in bpy.context.scene.timeline_markers:
                            if m.frame==bpy.context.scene.markerlist[bpy.context.scene.marker_index].frame:
                                m.select=True
                        info = 'Marker removed'
                        Ocontext=bpy.context.area.type
                        bpy.context.area.type='TIMELINE'
                        Nmarker=bpy.ops.marker.delete()
                        bpy.context.area.type=Ocontext
                        self.report({'INFO'}, info)
                        bpy.ops.markerlist.refresh()
                else:
                    info = 'Marker no longer exists'
                    self.report({'ERROR'}, info)
        
        return {'FINISHED'} 

# Go to next marker
class Markerlist_Gotonext(bpy.types.Operator):
    bl_idname = "markerlist.goto_next"
    bl_label = "Go to Next Marker"
    bl_description = "Go to Next Marker"
        
    def execute(self, context):
        scene=bpy.context.scene
        tlmlist=scene.timeline_markers
        mlist=scene.markerlist
        cframe=scene.frame_current
        framelist=[]
        upperframelist=[]
        bpy.ops.markerlist.refresh()
        for m in tlmlist:
            m.select=False
        for m in mlist:
            framelist.append(m.frame)
            if m.frame > cframe:
                upperframelist.append(m.frame)
        if len(upperframelist)==0:
            ncframe=cframe
        else:
            scene.frame_current=upperframelist[0]
            ncframe=scene.frame_current
        for m in tlmlist:
            if m.frame==ncframe:
                m.select=True
        for f in framelist:
            if f==ncframe:
                scene.marker_index=framelist.index(f)
        
        return {'FINISHED'} 
    
    
# Go to previous marker
class Markerlist_Gotoprevious(bpy.types.Operator):
    bl_idname = "markerlist.goto_previous"
    bl_label = "Go to Previous Marker"
    bl_description = "Go to Previous Marker"
        
    def execute(self, context):
        scene=bpy.context.scene
        tlmlist=scene.timeline_markers
        mlist=scene.markerlist
        cframe=scene.frame_current
        framelist=[]
        lowerframelist=[]
        bpy.ops.markerlist.refresh()
        for m in tlmlist:
            m.select=False
        for m in mlist:
            framelist.append(m.frame)
            if m.frame < cframe:
                lowerframelist.append(m.frame)
        lowerframelist.sort(reverse=True)
        if len(lowerframelist)==0:
            ncframe=cframe
        else:
            scene.frame_current=lowerframelist[0]
            ncframe=scene.frame_current
        for m in tlmlist:
            if m.frame==ncframe:
                m.select=True
        for f in framelist:
            if f==ncframe:
                scene.marker_index=framelist.index(f)
        
        return {'FINISHED'} 
    
    
# Save Transcript of Marker Comments
class Markerlist_SaveTranscript(bpy.types.Operator, ImportHelper):
    bl_idname = "markerlist.save_transcript"
    bl_label = "Save Transcript"
    bl_description = "Save Transcript of markers as text file in current folder"
        
    def execute(self, context):
        bpy.ops.markerlist.refresh()
        filepath=self.properties.filepath
        blendname2=bpy.path.abspath(bpy.path.basename(bpy.context.blend_data.filepath))
        blendname=os.path.splitext(blendname2)[0]
        scene=bpy.context.scene
        scenename=str(scene.name)
        scene=bpy.context.scene
        scenename=str(scene.name)
        tlmlist=scene.timeline_markers
        mlist=scene.markerlist
        today = datetime.date.today()
        dt = datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S")
        
        if ".mkt" not in filepath :
            file = open(filepath +".mkt", "w")
        else : 
            file = open(filepath, "w")
        file.write("Markers Transcript\nProject : "+blendname+"\n"+"Timeline : "+scenename+"\n\n")
        file.write("Date : "+str(dt)+"\n\n")
        for m in mlist:
            file.write("____Marker "+m.name+" : \n")
            file.write("    Frame "+str(m.frame)+"\n")
            file.write("    "+m.comment+"\n\n")
        file.close()
        info = 'Marker Transcript created'
        self.report({'INFO'}, info)

        return {'FINISHED'} 


# Import Transcript of Marker Comments
class Markerlist_ImportTranscript(bpy.types.Operator, ImportHelper):
    bl_idname = "markerlist.import_transcript"
    bl_label = "Import Transcript"
    bl_description = "Import text file markers Transcript from current folder"
        
    def execute(self, context):
        filepath=self.properties.filepath
        blendname2=bpy.path.abspath(bpy.path.basename(bpy.context.blend_data.filepath))
        blendname=os.path.splitext(blendname2)[0]
        scene=bpy.context.scene
        tlmlist=scene.timeline_markers
        mlist=scene.markerlist
        linelist=[]
        oframelist=[]
        nframelist=[]
        check=0
        
        if ".mkt" not in filepath:
            info = 'Select a .mkt file'
            self.report({'ERROR'}, info)
        else:
            bpy.ops.markerlist.refresh()
            with open(filepath, 'r', newline='') as csvfile:
                line = csv.reader(csvfile, delimiter='\n')
                for l in line:
                    linelist.append(str(l))
                for l in mlist:
                    oframelist.append(l.frame)
                for l in linelist:
                    if "    Frame " in l:
                        idx=linelist.index(l)
                        frametemp=str(linelist[idx]).split("Frame ")[1]
                        frame=frametemp.split("']")[0]
                        nframelist.append(frame)
                for l in linelist:
                    if "____" in l:
                        check=0
                        nametemp=l.split("____Marker ")[1]
                        mname=nametemp.split(" :")[0]
                        fidx=linelist.index(l)+1
                        cidx=linelist.index(l)+2
                        frametemp=str(linelist[fidx]).split("Frame ")[1]
                        frame=int(frametemp.split("']")[0])
                        comment=str(linelist[cidx]).split("']")[0]
                        for f in oframelist:
                            if frame==int(f):
                                check=1
                                mlist[oframelist.index(f)].name=mname
                        if check==0:
                            newM=scene.timeline_markers.new(mname)
                            newM.frame=frame
                bpy.ops.markerlist.refresh()
                for l in linelist:
                    if "____" in l:
                        nametemp=l.split("____Marker ")[1]
                        mname=nametemp.split(" :")[0]
                        cidx=linelist.index(l)+2
                        commenttemp=str(linelist[cidx]).split("['   ")[1]
                        comment=str(commenttemp).split("']")[0]
                        for ml in mlist:
                            if ml.name==mname:
                                ml.comment=comment
            info = 'Marker Transcript Imported'
            self.report({'INFO'}, info)                
        return {'FINISHED'} 


# Copy Marker to Scene
def copymarkertoscene(scn, self, context):
    scene=bpy.context.scene
    scenename=str(scene.name)
    tlmlist=scene.timeline_markers
    mlist=scene.markerlist
    idx=scene.marker_index
    copyall = bpy.context.scene.markerlist_copyall
    mcount=0
    
    bpy.ops.markerlist.refresh()
    for sc in bpy.data.scenes:
        if sc.name==scn:
            if copyall == True:
                for m in tlmlist:
                    new=sc.timeline_markers.new(m.name)
                    new.frame=m.frame
                    mcount=mcount+1
                for nm in mlist:
                    new=sc.markerlist.add()
                    new.name=nm.name
                    new.frame=nm.frame
                    new.comment=nm.comment
                info = str(mcount) + ' Marker(s) copied to ' + str(sc.name)
                self.report({'INFO'}, info)
            else:
                if idx > len(mlist):
                    info = 'Please select a Marker'
                    self.report({'ERROR'}, info)
                else:
                    mok=mlist[idx]
                    new=sc.timeline_markers.new(mok.name)
                    new.frame=mok.frame
                    newm=sc.markerlist.add()
                    newm.name=mok.name
                    newm.frame=mok.frame
                    newm.comment=mok.comment
                    info = 'Marker copied to ' + str(sc.name)
                    self.report({'INFO'}, info)

            
    
        
class CopyMarkerToScene(bpy.types.Operator):
    bl_idname = "copy.marker_toscene"
    bl_label = "Copy Marker to Scene"
    bl_description = "Copy Marker to Scene\nWARNING : Can create several markers on same frame"
    bl_options = {'REGISTER'}
    scn = bpy.props.StringProperty()

    
    def execute(self, context):
        copymarkertoscene(self.scn, self, context)
        return {'FINISHED'}
        

        return {'FINISHED'} 


### MENU READ COMMENT ###
class MenuReadComment(bpy.types.Menu):
    """Read and Modify Markers Comment"""
    bl_label = "Read Comment"
    bl_idname = "Menu_Read_Comment"
    
    def draw(self, context):
        layout = self.layout
        scene=bpy.context.scene
        idx=scene.marker_index
        mlist = scene.markerlist
        tlmlist = scene.timeline_markers
        
        if (idx+1) > len(mlist):
            info = 'Please select a marker'
            self.report({'ERROR'}, info)
        else :
            layout.prop(context.scene.markerlist[idx], "comment", text='')
            

### MENU COPY MARKERS TO SCENE ###
class MenuCopyMarkersToScene(bpy.types.Menu):
    """Copy Marker(s) to Scene\nWARNING : Can create several markers on same frame"""
    bl_label = "Copy Marker(s) to Scene"
    bl_idname = "Menu_CopyMarkers_ToScene"
    
    def draw(self, context):
        layout = self.layout
        scenes=bpy.data.scenes
        Cscene=bpy.context.scene
        idx=Cscene.marker_index
        mlist = Cscene.markerlist
        tlmlist = Cscene.timeline_markers
        
        if len(scenes) > 1:
            for s in scenes:
                if s != Cscene:
                    s2=str(s.name)
                    opcopy=layout.operator('copy.marker_toscene', text=s.name, icon='SCENE_DATA')
                    opcopy.scn = s2
        else:
            layout.label("Only One Scene in this blend file", icon='ERROR')       



# Create custom property group
class MarkerList(bpy.types.PropertyGroup):
    '''name = StringProperty() '''
    frame = IntProperty()
    comment = StringProperty(default = "No Comment")
    markerid = IntProperty()

# -------------------------------------------------------------------
# register
# -------------------------------------------------------------------

def register():
    bpy.utils.register_module(__name__)
    bpy.types.Scene.markerlist = CollectionProperty(type=MarkerList)
    bpy.types.Scene.marker_index = IntProperty()
    bpy.types.Scene.markerlist_copyall = bpy.props.BoolProperty(
        name="Copy All Markers",
        description="Copy All Markers to selected Scene",
        default = False)



    

def unregister():
    bpy.utils.unregister_module(__name__)
    del bpy.types.Scene.markerlist
    del bpy.types.Scene.marker_index
    del bpy.types.Scene.markerlist_copyall



if __name__ == "__main__":
    register()