import sys,os,glob,re,zipfile,io
from PIL import Image
src,out=sys.argv[1],sys.argv[2]
z=zipfile.ZipFile(src); files={n:z.read(n) for n in z.namelist()}
renames={}
for n in list(files):
    if not n.startswith('ppt/media/') or n.endswith('.gif') or len(files[n])<100_000: continue
    im=Image.open(io.BytesIO(files[n])); im.load()
    alpha=False
    if im.mode in('RGBA','LA','P'):
        alpha=im.convert('RGBA').getchannel('A').getextrema()[0]<250
    im.thumbnail((700,700) if alpha else (1400,1400))
    buf=io.BytesIO()
    if alpha:
        im.convert('RGBA').save(buf,'PNG',optimize=True); new=n
    else:
        im.convert('RGB').save(buf,'JPEG',quality=80,optimize=True,progressive=True)
        new=re.sub(r'\.(png|jpe?g)$','.jpg',n)
    if len(buf.getvalue())<len(files[n]):
        del files[n]; files[new]=buf.getvalue()
        if new!=n: renames[os.path.basename(n)]=os.path.basename(new)
        print(n,'->',new,len(buf.getvalue()))
for n in list(files):
    if n.endswith('.rels') and renames:
        s=files[n].decode('utf8')
        for a,b in renames.items(): s=s.replace('media/'+a+'"','media/'+b+'"')
        files[n]=s.encode('utf8')
with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED) as o:
    o.writestr('[Content_Types].xml',files.pop('[Content_Types].xml'))
    for n,b in files.items(): o.writestr(n,b)
print('size',os.path.getsize(out))
