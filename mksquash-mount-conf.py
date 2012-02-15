#!/usr/bin/python
import os
import sys
import optparse

def importConfig(configfile):
  a={}
  b={}
  execfile(configfile,a,b)
  return b

def readconfig(confpath):
  global config
  config=importConfig(confpath)

def readoldconfig(confpath):
  global oldconfig
  oldconfig=importConfig(confpath)

def getoldconfig(x,alt=''):
  if oldconfig.has_key(x):
    return oldconfig[x]
  return alt

def getoldconfig3(x,y,z,alt=''):
  if oldconfig.has_key(x):
    if oldconfig[x].has_key(y):
      if oldconfig[x][y].has_key(z):
        return oldconfig[x][y][z]
  return alt

def executar1(cmd,verbose=False,norun=False):
  if norun or verbose:
    sys.stderr.write(cmd+"\n")
  if not norun:
    return os.system(cmd)
  else:
    return 0
                    
executar=executar1

def askvar(var,default='',example=''):
  exstr=''
  if example:
    exstr=' (Ex: '+example+')'
  defstr=''
  if default:
    defstr=' ['+default+']'
  sys.stderr.write('Value for '+ var + exstr + defstr +': ')
  result = sys.stdin.readline().strip()
  if result=='':
      return default
  else:
      return result

def askYorN(question):
  result=''
  while not (result.lower() == 'y' or result.lower()=='n'):
    sys.stderr.write(question + ' [y/n]: ')
    result = sys.stdin.readline().strip()
  return result.lower()=='y'

def readpartitiontable(ddfilepath):
  particoes=[]
  for line in os.popen('sfdisk -d '+ ddfilepath).readlines()[3:]:
    virgs=line.rstrip().split(',')
    start=virgs[0].split('=')[-1].strip()
    size=virgs[1].split('=')[-1].strip()
    type=virgs[2].split('=')[-1].strip()
    if not(type=='f' or size=='0'):
      particoes.append({'offset':int(start)*512,
                        'size':size,
                        'type':type})
  if not particoes:
    tipoparticao='auto'
    particoes.append({'offset':0,
                      'size':0,
                      'type':tipoparticao})
  return particoes

def printparticoes(fpath):
  particoes=readpartitiontable(fpath)
  for x in range(len(particoes)):
    particao=particoes[x]
    if config['partitiontypes'].has_key(particao['type']):
      tipo=config['partitiontypes'][particao['type']]
    else:
      if fpath[-4:]=='.tao' or fpath[-4:]=='.iso':
        tipo='iso9660'
      else:
        tipo='auto'
    if not tipo=='extended':
      offset=particao['offset']
      print("         {'letra':'"+chr(ord('C')+x)+"',")
      print("          'tipo':'"+tipo+"',")
      print("          'offset':'"+str(offset)+"',")
      print("#          'nofiles':'',")
      print("#          'opcoesextra':'',")
      print("#          'overrideopcoes':'',")
      print("#          'overridemountpoint':'',")
      print("#          'bindfs':'"+chr(ord('C')+x)+"',")
      print("         },")

def printimagens(options,ddfilepaths):
  def getid(fpath):
    s=fpath.split('/')
    if len(s)>1:
      return s[-2]
    else:
      return ''
  def f(id,a):
    return "imdict['"+id+"']['"+a+"']"

  print("materiais=[#[id,equipe,item,tipo,alvo,imagem] ")
  for x in range(len(ddfilepaths)):
    fpath=ddfilepaths[x]
    ximagem=os.path.basename(fpath)
    id=options.id or getid(fpath)
    print("    ['%s','','','','','%s'],"%(id,ximagem))
  print("""    ]

for x in materiais:
    xid,xequipe,xitem,xtipo,xalvo,ximagem=x
    imdict[xid]={}
    imdict[xid]['id']=xid
    imdict[xid]['equipe']=xequipe
    imdict[xid]['alvo']=xalvo
    imdict[xid]['item']=xitem
    imdict[xid]['tipo']=xtipo
    imdict[xid]['imagem']=ximagem
    imdict[xid]['path']=squashmnt+'/%s/%s'%(xid,ximagem)
    imdict[xid]['mntpath']=basemnt+'/'+makepath(imdict[xid])
""")
  for x in range(len(ddfilepaths)):
    fpath=ddfilepaths[x]
    id=options.id or getid(fpath)
    print(f(id,'particoes')+"=[")
    printparticoes(fpath)
    print("     ]")

def printfile(options,ddfilepaths):
  print('#!/usr/bin/python')
  print('operacao="'+ options.operacao +'"')
  print('squashfile="'+ options.squashfile +'"')
  print('squashmnt="'+ options.squashmnt +'"')
  print('basemnt="'+ options.basemnt +'"')
  print("""def makepath(dic):
    item=dic['item']
    if item and not item.startswith('item'):
        item='item'+item
    subresult='-'.join([x for x in [item,
                                    dic['tipo'],
                                    dic['id']] if x])
    result='/'.join([x for x in [dic['equipe'],
                                 dic['alvo'],
                                 subresult] if x])
    
    return result
imdict={}
""")
  printimagens(options,ddfilepaths)
  print('imagens=imdict.values()')

def mountpointexist(mountpoint):
  return (os.path.exists(mountpoint) and os.path.isdir(mountpoint))

def mountpointmounted(mountpoint):
  f=open('/proc/mounts','r')
  for line in f:
    a=line.strip().split(" ")
    if a and len(a)>2:
      b=a[1]
      if b==mountpoint:
        f.close
        return True
  f.close
  return False

def main():
  p = optparse.OptionParser(usage="usage: %prog [options] <oldconfigfile>")
  p.add_option('--operacao',
               default='')
  p.add_option('--expediente',
               default='')
  p.add_option('--squashfile',
               default='',
               help="Ex: --squashfile=fileXYZ.squash")
  p.add_option('--squashmnt',
               default='',
               help="where the squashfile will be mounted")
  p.add_option('--basemnt',
               default='',
               help="where the dd files will be mounted")
  p.add_option('--id',
               default='',
               help="material id")
  p.add_option('--equipe',
               default='',
               help="material equipe")
  p.add_option('--alvo',
               default='',
               help="material alvo")
  p.add_option('--item',
               default='',
               help="material item")
  p.add_option('--tipo',
               default='',
               help="material tipo")
  p.add_option('--squashmountconf', '-f',
               default="/etc/squash-mount/squash-mount.conf",
               help="defaults to /etc/squash-mount/squash-mount.conf")
  p.add_option('--noquestions', action='store_true',default=False)
  options, arguments = p.parse_args()

  if len(arguments) > 1: 
    p.print_help()
    p.error('too many arguments')

  readconfig(options.squashmountconf)
  global oldconfig
  oldconfig={}
  if len(arguments) > 0 :
    readoldconfig(arguments[0])
    if oldconfig.has_key('imagens') and not oldconfig.has_key('imdict'):
      oldconfig['imdict']={}
      for x in oldconfig['imagens']:
        oldconfig['imdict'][x['id']]=x
  if not options.noquestions:
    if options.operacao=='':
      options.operacao=askvar('operacao',default=getoldconfig('operacao'))
    if options.expediente=='':
      options.expediente=askvar('expediente',
                                default=getoldconfig('expediente'),
                                example='R090123, R080021')
    op_exp='-'.join([x for x in [options.operacao, options.expediente] if x])
    if options.squashfile=='':
      options.squashfile=askvar('squashfile',
                                default=getoldconfig(
                                  'squashfile',
                                  config['squashfileprefix'] +
                                  op_exp +
                                  config['squashfilesuffix']))
    if options.squashmnt=='':
      options.squashmnt=askvar('squashmnt',
                               default=getoldconfig(
                                 'squashmnt',
                                 config['squashmntprefix'] +
                                 op_exp +
                                 config['squashmntsuffix']))
    if options.basemnt=='':
      options.basemnt=askvar('basemnt',
                             default=getoldconfig(
                               'basemnt',
                               config['basemntprefix'] +
                               options.operacao +
                               config['basemntsuffix']))

    if not mountpointexist(options.squashmnt):
      if askYorN('Confirm mkdir of ' + options.squashmnt + '?'):
        os.mkdir(options.squashmnt)
      else:
        sys.exit(1)

    if not mountpointmounted(options.squashmnt):
      command="mount '"+options.squashfile+"' "+options.squashmnt+' -o ro,loop'
      if askYorN('Run "' + command + '" ?'):
        executar(command)
      else:
        sys.exit(1)

    ftypes='*.dd *.iso *.tao *.001'
    if askYorN('Confirm search for file images ('+ftypes+')?'):
      os.chdir(options.squashmnt)
      fftypes=' -or '.join([" -iname '"+i+"'" for i in ftypes.split()])
      lines=os.popen('find * '+fftypes).readlines()
      files=[f.strip() for f in lines]
      if askYorN('Files found:\n'+'\n'.join(files)+'\nUse them?'):
        pass
      else:
        sys.exit(1)
    else:
      sys.exit(1)

  ddfilepaths=files
  printfile(options,ddfilepaths)

if __name__ == '__main__':
  try:
    main()
  except KeyboardInterrupt:
    sys.exit(0)
