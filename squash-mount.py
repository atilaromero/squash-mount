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

def executar1(cmd,debug=False,norun=False):
  if norun or debug:
    sys.stderr.write(cmd+"\n")
  if not norun:
    return os.system(cmd)
  else:
    return 0

executar=executar1

def getmountpoint(expediente,imagem,particao):
  return os.path.join(expediente['basemnt'],
                      imagem['equipe'],
                      imagem['alvo'],
                      "item"+str(imagem['item'])+ "-" +
                      imagem['tipo'] + "-" +
                      imagem['id'],
                      particao['letra'])

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
  opcoes=[particao['opcoesextra'],
          config['basicmountoptions'],
          "gid="+expediente['operacao'],
          "offset="+str(particao['offset'])]
  for x in range(opcoes.count('')):
    opcoes.remove('')
  return ",".join(opcoes)

def ensureddmounted(expediente,imagem,particao):
  mountpoint=getmountpoint(expediente,imagem,particao)
  if not mountpointmounted(mountpoint):
    return executar("mount -t "+particao['tipo'] + " "
                    + imagem['path'] + " "
                    + mountpoint
                    + " -o "+getmountoptions(expediente,imagem,particao))
  else:
    return 0

def ensuresquashmounted(expediente):
  if not mountpointmounted(expediente['squashfile']):
    return executar("mount "+
                    expediente['squashfile'] + "\t" +
                    expediente['squashmnt'] + "\t" +
                    "-o ro,umask=227,_netdev,noexec,uid=root,gid=root,loop")
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
  p.add_option('--configfile', '-f',
               default="/etc/squash-mount/squash-mount.conf",
               help="defaults to /etc/squash-mount/squash-mount.conf")
  p.add_option('--norun', '-n',action='store_true',default=False)
  p.add_option('--debug', '-d',action='store_true',default=False,
               help="print commands to stderr")
  options, arguments = p.parse_args()
  global executar
  executar=functools.partial(executar1,debug=options.debug,norun=options.norun)
  if not(options.listsquash or
         options.listdd or
         options.listmnt or
         options.mountdd or
         options.umountdd or
         options.mountsquash or
         options.umountsquash or
         options.checksquash or
         options.checkpartitions or
         options.checkfiles):
    p.print_help()
  else:
    readconfig(options.configfile)
    for filename,expediente in expedientes.iteritems():
      if options.listsquash:
        print(expediente['squashfile'])
      if options.umountsquash:
        result+=umount(expediente['squashfile'])
      if options.mountsquash:
        result+=ensuresquashmounted(expediente)
      if options.checksquash:
        if not mountpointmounted(expediente['squashfile']):
          sys.stderr.write('squash file not mounted: '+
                           expediente['squashfile']+"\n")
          result+=1
    lastddimage=''
    for expediente,imagem,particao in iterexpedientes():
      mountpoint=getmountpoint(expediente,imagem,particao)
      if options.listdd:
        if lastddimage!=imagem['path']:
          print(imagem['path'])
          lastddimage=imagem['path']
      if options.listmnt:
        print(mountpoint)
      if options.umountdd:
        result+=umount(mountpoint)
      if options.mountdd:
        result+=ensureddmounted(expediente,imagem,particao)
      if options.checkpartitions:
        if not mountpointmounted(mountpoint):
          sys.stderr.write('mountpoint umounted: '+mountpoint+"\n")
          result+=1
      if options.checkfiles:
        if not mountpointhasfiles(mountpoint):
          sys.stderr.write('mountpoint has no files: '+mountpoint+"\n")
          result+=1
  sys.exit(result)
                      
if __name__ == '__main__':
  main()
