#!/usr/bin/python
import os
import sys
import optparse
import functools

def importConfig(configfile):
  a={}
  b={}
  execfile(configfile,a,b)
  return b

def readconfig(confpath):
  global config
  config=importConfig(confpath)
  global expedientes
  expedientes={}
  for f in os.listdir(config['includedir']):
    expedientes[f]=importConfig(os.path.join(config['includedir'],f))

def iterexpedientes():
  for filename,expediente in expedientes.iteritems():
    for imagem in expediente['imagens']:
      for particao in imagem['particoes']:
        yield(expediente,imagem,particao)

def executar1(cmd,verbose=False,norun=False):
  if norun or verbose:
    sys.stderr.write(cmd+"\n")
  if not norun:
    return os.system(cmd)
  else:
    return 0

executar=executar1

def getmountpoint(expediente,imagem,particao,letra=''):
  if particao.has_key('overridemountpoint'):
    return particao['overridemountpoint']
  if not letra:
    letra=particao['letra']
  item=''
  if str(imagem['item']):
    item="item"+str(imagem['item'])
  tipo=''
  if imagem['tipo']:
    tipo = imagem['tipo']
  id=''
  if imagem['id']:
    id=imagem['id']
  nome=[item,tipo,id]
  for x in range(nome.count('')):
    nome.remove('')
  nomestr='-'.join(nome)
  if imagem.has_key('mntpath'):
    nomestr=imagem['mntpath']
  return os.path.join(expediente['basemnt'],
                      imagem['equipe'],
                      imagem['alvo'],
                      nomestr,
                      letra)

def getmntbindfs(expediente,imagem,particao):
  letra=particao['bindfs']
  return getmountpoint(expediente,imagem,particao,letra)

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

def mountpointhasfiles(mountpoint):
  return mountpointexist(mountpoint) and len(os.listdir(mountpoint))>0

def getmountoptions(expediente,imagem,particao):
  if particao.has_key('overrideopcoes'):
    return particao['overrideopcoes']
  basicoptions = config['typeoptions'][particao['tipo']]
  offset=''
  if particao.has_key('offset'):
    offset="offset="+str(particao['offset'])
  opcoesextra=''
  if particao.has_key('opcoesextra'):
    opcoesextra = particao['opcoesextra']
  opcoes=[basicoptions,
          opcoesextra,
          "gid="+expediente['operacao'],
          offset]
  for x in range(opcoes.count('')):
    opcoes.remove('')
  return ",".join(opcoes)

def ensureddmounted(expediente,imagem,particao):
  mountpoint=getmountpoint(expediente,imagem,particao)
  if not mountpointmounted(mountpoint):
    result=0
    result+=executar("mount -t "+particao['tipo'] + " '"
                     + imagem['path'] + "' "
                     + mountpoint
                     + " -o "+getmountoptions(expediente,imagem,particao))
    if particao.has_key('bindfs'):
      mntbindfs=getmntbindfs(expediente,imagem,particao)
      result+=executar("bindfs -o perms=ug=rX:o-rwx,user=root,group="+expediente['operacao']+ " "
                       + mountpoint + " "
                       + mntbindfs)
    return result
  else:
    return 0

def ensuresquashmounted(expediente):
  if not mountpointmounted(expediente['squashmnt']):
    return executar("mount "+
                    expediente['squashfile'] + "\t" +
                    expediente['squashmnt'] + "\t" +
                    " -o ro,umask=227,_netdev,noexec,uid=root,gid=root,loop")
  else:
    return 0
                    

def umount(mountpoint):
  if mountpointmounted(mountpoint):
    return executar("umount " + mountpoint)
  else:
    return 0

def main():
  result=0
  p = optparse.OptionParser()
  p.add_option('--listsquash', action='store_true',default=False,
               help="list squash files")
  p.add_option('--listmnt', action='store_true',default=False,
               help="list mountpoints")
  p.add_option('--listsquashmnt', action='store_true',default=False,
               help="list squash mountpoints")
  p.add_option('--listdd', action='store_true',default=False,
               help="list dd images")
  p.add_option('--mountdd',action='store_true',default=False,
               help="ensure all dd images are mounted")
  p.add_option('--umountdd',action='store_true',default=False,
               help="umount all dd images")
  p.add_option('--mountsquash', action='store_true',default=False,
               help="ensure all squash files are mounted")
  p.add_option('--umountsquash', action='store_true',default=False,
               help="umount all squash files")
  p.add_option('--checksquash',action='store_true',default=False,
               help="checks if all squash files are mounted")
  p.add_option('--checkpartitions',action='store_true',default=False,
               help="checks if all partitions are mounted")
  p.add_option('--checkfiles',action='store_true',default=False,
               help="checks if all partitions have files")
  p.add_option('--mkdirs',action='store_true',default=False,
               help="create all needed directories (squash and dd mountpoints)")
  p.add_option('--mklinks',action='store_true',default=False,
               help="create links to dd images")
  p.add_option('--operacao',
               default='',
               help="only consider this operacao")
  p.add_option('--configfile', '-f',
               default="/etc/squash-mount/squash-mount.conf",
               help="defaults to /etc/squash-mount/squash-mount.conf")
  p.add_option('--norun', '-n',action='store_true',default=False)
  p.add_option('--verbose', '-v',action='store_true',default=False,
               help="print commands to stderr")
  options, arguments = p.parse_args()
  global executar
  executar=functools.partial(executar1,
                             verbose=options.verbose,
                             norun=options.norun)
  if not(options.listsquash or
         options.listdd or
         options.listsquashmnt or
         options.listmnt or
         options.mountdd or
         options.umountdd or
         options.mountsquash or
         options.umountsquash or
         options.checksquash or
         options.checkpartitions or
         options.checkfiles or
         options.mklinks):
    p.print_help()
  else:
    readconfig(options.configfile)
    for filename,expediente in expedientes.iteritems():
      if not options.operacao or options.operacao==expediente['operacao']:
        if options.listsquash:
          print(expediente['squashfile'])
        if options.listsquashmnt:
          print(expediente['squashmnt'])
        if options.mkdirs:
          if not mountpointexist(expediente['squashmnt']):
            os.makedirs(expediente['squashmnt'])
        if options.umountsquash:
          result+=umount(expediente['squashmnt'])
        if options.mountsquash:
          result+=ensuresquashmounted(expediente)
        if options.checksquash:
          if not mountpointmounted(expediente['squashmnt']):
            sys.stderr.write('squash file not mounted: '+
                             expediente['squashfile']+"\n")
            result+=1
    lastddimage=''
    for expediente,imagem,particao in iterexpedientes():
      if not options.operacao or options.operacao==expediente['operacao']:
        mountpoint=getmountpoint(expediente,imagem,particao)
        mntbindfs=''
        if particao.has_key('bindfs'):
          mntbindfs=getmntbindfs(expediente,imagem,particao)
        if lastddimage!=imagem['path']:
          if options.listdd:
            print(imagem['path'])
          if options.mklinks:
            executar("ln -s '"+imagem['path']+"' '"+os.path.join(mountpoint,'..')+"'")
        lastddimage=imagem['path']
        if options.listmnt:
          print(mountpoint)
        if options.mkdirs:
          if not mountpointexist(mountpoint):
            os.makedirs(mountpoint)
          if particao.has_key('bindfs') and not mountpointexist(mntbindfs):
            os.makedirs(mntbindfs)
        if options.umountdd:
          if particao.has_key('bindfs'):
            result+=umount(mntbindfs)
          result+=umount(mountpoint)
        if options.mountdd:
          result+=ensureddmounted(expediente,imagem,particao)
        if options.checkpartitions:
          if not mountpointmounted(mountpoint):
            sys.stderr.write('mountpoint umounted: '+mountpoint+"\n")
            result+=1
          if particao.has_key('bindfs') and not mountpointmounted(mntbindfs):
            sys.stderr.write('mountpoint umounted: '+mntbindfs+"\n")
            result+=1
        if options.checkfiles:
          if not particao.has_key('nofiles'):
            if not mountpointhasfiles(mountpoint):
              sys.stderr.write('mountpoint has no files: '+mountpoint+"\n")
              result+=1
            if particao.has_key('bindfs') and not mountpointhasfiles(mntbindfs):
              sys.stderr.write('mountpoint has no files: '+mntbindfs+"\n")
              result+=1
  sys.exit(result)
                      
if __name__ == '__main__':
  main()
