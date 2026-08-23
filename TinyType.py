import tkinter as tk
import sys,os,html,re,webbrowser,tempfile,subprocess,zipfile
from tkinter import filedialog,messagebox,font,simpledialog
def set_app_name(r):
    if sys.platform == "darwin":
        try:
            r.tk.call("tk", "appname", "TinyType")
        except:
            pass


W="http://schemas.openxmlformats.org/wordprocessingml/2006/main"
R="http://schemas.openxmlformats.org/officeDocument/2006/relationships"
WP="http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing"
A="http://schemas.openxmlformats.org/drawingml/2006/main"
PIC="http://schemas.openxmlformats.org/drawingml/2006/picture"

class App:
 def __init__(s,r):
  s.r=r;s.file=None;s.dirty=False;s.n=0
  s.images=[];s.links=[];s.b=s.i=s.u=False
  r.title("Untitled — TinyType");r.geometry("850x600")
  s.t=tk.Text(r,undo=True,wrap="word",font=("Arial",12),border=0,
              highlightthickness=0,padx=12,pady=10)
  s.t.pack(fill="both",expand=True)
  s.t.bind("<<Modified>>",s.modified)
  s.styles("Arial",12);s.menu();s.keys()
  s.t.edit_modified(False)

 def menu(s):
  m=tk.Menu(s.r)
  s.r.config(menu=m)
  if sys.platform=="darwin":
   appmenu=tk.Menu(m,tearoff=False,name="apple")
   appmenu.add_command(label="About TinyType",command=s.about)
   appmenu.add_separator()
   appmenu.add_command(label="Quit TinyType",command=s.exit)
  menus={
   "File":[("New",s.new),("Open",s.open),("Save",s.save),
           ("Save As...",s.saveas),None,("Insert Image...",s.image),
           ("Hyperlink...",s.link),None,("Exit",s.exit)],
   "Edit":[("Undo",s.undo),("Redo",s.redo),None,
           ("Cut",lambda:s.ev("<<Cut>>")),
           ("Copy",lambda:s.ev("<<Copy>>")),
           ("Paste",lambda:s.ev("<<Paste>>")),None,
           ("Select All",lambda:s.ev("<<SelectAll>>"))],
   "Format":[("Bold",s.bold),("Italic",s.italic),("Underline",s.under)],
   "Font":[("Choose Font...",s.choose_font),("Choose Size...",s.choose_size)]
  }
  for name,items in menus.items():
   q=tk.Menu(m,tearoff=False)
   for x in items:
    if x is None:q.add_separator()
    else:q.add_command(label=x[0],command=x[1])
   m.add_cascade(label=name,menu=q)

 def about(s):
  w=tk.Toplevel(s.r)
  w.title("About TinyType")
  w.resizable(False,False)
  w.geometry("300x220")
  w.transient(s.r)
  tk.Label(w,text="TinyType",font=("Arial",22,"bold")).pack(pady=(30,5))
  tk.Label(w,text="Version 1.0",font=("Arial",12)).pack()
  tk.Label(w,text="by DanDevProjects",font=("Arial",11)).pack(pady=5)
  tk.Button(w,text="OK",width=10,command=w.destroy).pack(pady=20)

 def keys(s):
  for k,c in {
   "<Command-n>":s.new,"<Command-o>":s.open,"<Command-s>":s.save,
   "<Command-b>":s.bold,"<Command-i>":s.italic,
   "<Command-u>":s.under,"<Command-z>":s.undo,
   "<Command-y>":s.redo}.items():
   s.r.bind(k,lambda e,c=c:c())

 def styles(s,f,n):
  for tag,weight,slant,u in [
   ("b","bold","roman",0),("i","normal","italic",0),
   ("u","normal","roman",1),("bi","bold","italic",0),
   ("bu","bold","roman",1),("iu","normal","italic",1),
   ("biu","bold","italic",1)]:
   s.t.tag_configure(tag,font=(f,n,weight,slant),underline=u)

 def selected(s):
  try:return s.t.index("sel.first"),s.t.index("sel.last")
  except:return None

 def fmt(s):
  q=s.selected()
  if not q:return
  a,z=q
  for x in ("b","i","u","bi","bu","iu","biu"):
   s.t.tag_remove(x,a,z)
  tag={(1,0,0):"b",(0,1,0):"i",(0,0,1):"u",
       (1,1,0):"bi",(1,0,1):"bu",(0,1,1):"iu",
       (1,1,1):"biu"}.get((s.b,s.i,s.u))
  if tag:s.t.tag_add(tag,a,z)
  s.dirty=True;s.title()

 def bold(s):
  s.b=not s.b;s.fmt()

 def italic(s):
  s.i=not s.i;s.fmt()

 def under(s):
  s.u=not s.u;s.fmt()

 def choose_font(s):
  w=tk.Toplevel(s.r);w.title("Font");w.geometry("300x400")
  b=tk.Listbox(w);b.pack(fill="both",expand=True,padx=8,pady=8)
  for x in sorted(font.families()):b.insert("end",x)
  def go(e=None):
   q=b.curselection()
   if not q:return
   f=b.get(q[0])
   try:n=int(str(s.t.cget("font")).split()[-1])
   except:n=12
   s.t.config(font=(f,n));s.styles(f,n);s.dirty=True;s.title();w.destroy()
  b.bind("<Double-1>",go)
  tk.Button(w,text="Choose",command=go).pack(pady=5)

 def choose_size(s):
  w=tk.Toplevel(s.r);w.title("Size");w.geometry("180x330")
  b=tk.Listbox(w);b.pack(fill="both",expand=True,padx=8,pady=8)
  for n in (8,9,10,11,12,14,16,18,20,24,28,32,36,48,60,72):
   b.insert("end",n)
  def go(e=None):
   q=b.curselection()
   if not q:return
   n=int(b.get(q[0]))
   f=str(s.t.cget("font")).split()[0]
   s.t.config(font=(f,n));s.styles(f,n);s.dirty=True;s.title();w.destroy()
  b.bind("<Double-1>",go)
  tk.Button(w,text="Choose",command=go).pack(pady=5)

 def image(s):
  p=filedialog.askopenfilename(
   filetypes=[("Images","*.png *.jpg *.jpeg *.gif *.bmp"),("All files","*.*")])
  if not p:return
  try:
   src=p
   if not p.lower().endswith(".png"):
    q=tempfile.mktemp(".png")
    subprocess.run(["sips","-s","format","png",p,"--out",q],
                   stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,
                   check=True)
    p=q
   im=tk.PhotoImage(file=p)
   if im.width()>600:
    k=(im.width()+599)//600
    im=im.subsample(k,k)
   name="image%d"%s.n;s.n+=1
   s.t.image_create("insert",image=im,name=name)
   s.images.append((name,im,p,src))
   s.dirty=True;s.title()
  except Exception as e:
   messagebox.showerror("TinyType","Image error:\n"+str(e))

 def link(s):
  q=s.selected()
  if not q:
   messagebox.showinfo("TinyType","Select text first.");return
  u=simpledialog.askstring("Hyperlink","URL:",initialvalue="https://")
  if not u:return
  if not re.match(r"^[a-z][a-z0-9+.-]*://",u,re.I):
   u="https://"+u
  a,z=q;tag="link%d"%s.n;s.n+=1
  s.t.tag_configure(tag,foreground="#06c",underline=True)
  s.t.tag_add(tag,a,z)
  s.t.tag_bind(tag,"<Button-1>",lambda e,u=u:webbrowser.open(u))
  s.links.append((a,z,u));s.dirty=True;s.title()

 def rpr(s,tags):
  x=""
  if any(t in tags for t in ("b","bi","bu","biu")):x+="<w:b/>"
  if any(t in tags for t in ("i","bi","iu","biu")):x+="<w:i/>"
  if any(t in tags for t in ("u","bu","iu","biu")):
   x+='<w:u w:val="single"/>'
  return "<w:rPr>"+x+"</w:rPr>"

 def run(s,a,b):
  text=s.t.get(a,b)
  if not text:return ""
  r="<w:r>"+s.rpr(s.t.tag_names(a))+"<w:t xml:space=\"preserve\">"
  r+=html.escape(text,False)+"</w:t></w:r>"
  for i,(_,_,u) in enumerate(s.links,1):
   try:
    if s.t.compare(a,">=",s.links[i-1][0]) and s.t.compare(
       b,"<=",s.links[i-1][1]):
     return f'<w:hyperlink r:id="rIdLink{i}">'+r+"</w:hyperlink>"
   except:pass
  return r

 def picture(s,n):
  return '''<w:r><w:drawing><wp:inline>
<wp:extent cx="5486400" cy="4114800"/>
<wp:docPr id="%d" name="Picture %d"/>
<a:graphic><a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/picture">
<pic:pic><pic:nvPicPr><pic:cNvPr id="%d" name="Image %d"/><pic:cNvPicPr/></pic:nvPicPr>
<pic:blipFill><a:blip r:embed="rIdImg%d"/><a:stretch><a:fillRect/></a:stretch></pic:blipFill>
<pic:spPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="5486400" cy="4114800"/></a:xfrm>
<a:prstGeom prst="rect"><a:avLst/></a:prstGeom></pic:spPr>
</pic:pic></a:graphicData></a:graphic></wp:inline></w:drawing></w:r>'''%(n,n,n,n,n)

 def document(s):
  body=[];current=[]
  for kind,value,index in s.t.dump("1.0","end-1c",text=True,image=True,tag=False):
   if kind=="text":
    text=value;pos=0
    while pos<len(text):
     nl=text.find("\n",pos)
     end=len(text) if nl<0 else nl
     if end>pos:
      p=pos
      while p<end:
       aa=s.t.index(f"{index}+{p}c")
       tags=s.t.tag_names(aa);q=p+1
       while q<end and s.t.tag_names(s.t.index(f"{index}+{q}c"))==tags:q+=1
       current.append(s.run(aa,s.t.index(f"{index}+{q}c")))
       p=q
     if nl>=0:
      body.append("<w:p>"+''.join(current)+"</w:p>")
      current=[];pos=nl+1
     else:pos=end
   elif kind=="image":
    for i,x in enumerate(s.images,1):
     if x[0]==value:
      current.append(s.picture(i));break
  if current or not body:
   body.append("<w:p>"+''.join(current)+"</w:p>")
  return '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="%s" xmlns:r="%s" xmlns:wp="%s"
 xmlns:a="%s" xmlns:pic="%s"><w:body>%s
<w:sectPr><w:pgSz w:w="12240" w:h="15840"/>
<w:pgMar w:top="1440" w:right="1440" w:bottom="1440" w:left="1440"/>
</w:sectPr></w:body></w:document>'''%(W,R,WP,A,PIC,''.join(body))

 def savezip(s,p):
  try:
   with zipfile.ZipFile(p,"w",zipfile.ZIP_DEFLATED) as z:
    z.writestr("[Content_Types].xml",
'''<?xml version="1.0" encoding="UTF-8"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
<Default Extension="xml" ContentType="application/xml"/>
<Default Extension="png" ContentType="image/png"/>
<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
</Types>''')
    z.writestr("_rels/.rels",
'''<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
<Relationship Id="rIdDoc"
Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument"
Target="word/document.xml"/>
</Relationships>''')
    rel=['<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">']
    for i,x in enumerate(s.images,1):
     rel.append(f'<Relationship Id="rIdImg{i}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image" Target="media/image{i}.png"/>')
     with open(x[2],"rb") as f:z.writestr(f"word/media/image{i}.png",f.read())
    for i,x in enumerate(s.links,1):
     rel.append(f'<Relationship Id="rIdLink{i}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink" Target="{html.escape(x[2],True)}" TargetMode="External"/>')
    rel.append("</Relationships>")
    z.writestr("word/_rels/document.xml.rels","".join(rel))
    z.writestr("word/document.xml",s.document())
   s.file=p;s.dirty=False;s.title();return True
  except Exception as e:
   messagebox.showerror("TinyType","Save failed:\n"+str(e));return False

 def save(s):
  return s.saveas() if not s.file else s.savezip(s.file)

 def saveas(s):
  p=filedialog.asksaveasfilename(
   defaultextension=".docx",
   filetypes=[("Word Document","*.docx"),("All files","*.*")])
  return False if not p else s.savezip(p)

 def open(s):
  p=filedialog.askopenfilename(
   filetypes=[("Word Document","*.docx"),("All files","*.*")])
  if p:
   messagebox.showinfo("TinyType",
    "DOCX importing is not enabled in this lightweight build.\n\n"
    "TinyType can create DOCX files with text, formatting, hyperlinks and images.")

 def new(s):
  if not s.confirm():return
  s.t.delete("1.0","end");s.images=[];s.links=[];s.file=None
  s.dirty=False;s.title()

 def undo(s):
  try:s.t.edit_undo()
  except:pass

 def redo(s):
  try:s.t.edit_redo()
  except:pass

 def ev(s,x):
  s.t.event_generate(x)

 def modified(s,e=None):
  if s.t.edit_modified():
   s.dirty=True
   s.t.edit_modified(False)
   s.title()

 def title(s):
  n=os.path.basename(s.file) if s.file else "Untitled"
  s.r.title(("*" if s.dirty else "")+n+" — TinyType")

 def confirm(s):
  if not s.dirty:return True
  x=messagebox.askyesnocancel("TinyType","Save changes?")
  if x is None:return False
  return s.save() if x else True

 def exit(s):
  if s.confirm():s.r.destroy()

r=tk.Tk()
a=App(r)

if sys.platform=="darwin":
    try:
        r.tk.call("tk","appname","TinyType")
    except:
        pass

r.protocol("WM_DELETE_WINDOW",a.exit)
r.mainloop()