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
  sys.stderr.write('Type value for '+ var + exstr + defstr +': ')
  result = sys.stdin.readline().strip()
  if result=='':
      return default
  else:
      return result

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
  return particoes

def printparticoes(fpath):
  particoes=readpartitiontable(fpath)
  for x in range(len(particoes)):
    particao=particoes[x]
    notlast=''
    if x < (len(particoes)-1):
      notlast=','
    if config['partitiontypes'].has_key(particao['type']):
      tipo=config['partitiontypes'][particao['type']]
    else:
      tipo='auto'
    if not tipo=='extended':
      offset=particao['offset']
      print("         {'letra':'"+chr(ord('C')+x)+"',")
      print("          'tipo':'"+tipo+"',")
      print("          'offset':'"+str(offset)+"'}"+notlast)

def getmountpoint(id,equipe,alvo,item,tipo):
  if item:
    item="item"+item
  nome=[item,tipo,id]
  for x in range(nome.count('')):
    nome.remove('')
  nomestr='-'.join(nome)
  return os.path.join(equipe,
                      alvo,
                      nomestr)

def printimagens(options,ddfilepaths):
  for x in range(len(ddfilepaths)):
    fpath=ddfilepaths[x]
    notlast=''
    if x < (len(ddfilepaths)-1):
      notlast=','
    sys.stderr.write('\n')
    sys.stderr.write('Processing image ' + fpath + '\n')

    id=options.id
    equipe=options.equipe
    alvo=options.alvo
    item=options.item
    tipo=options.tipo
    if not id:
      id=askvar('id')
    if not equipe:
      equipe=askvar('equipe')
    if not alvo:
      alvo=askvar('alvo')
    if not item:
      item=askvar('item')
    if not tipo:
      tipo=askvar('tipo')
    print("    {'id':'"+id+"',")
    print("     'equipe':'"+equipe+"',")
    print("     'alvo':'"+alvo+"',")
    print("     'item':'"+item+"',")
    print("     'tipo':'"+tipo+"',")
    print("     'path':squashmnt+/'"+fpath+"',")
    print("     'mntpath':basemnt+'/"+getmountpoint(id,equipe,alvo,item,tipo)+"',")
    print("     'particoes':['")
    printparticoes(fpath)
    print("         ]")
    print("     }"+notlast)

def printfile(options,ddfilepaths):
  print('#!/usr/bin/python')
  print('operacao="'+ options.operacao +'"')
  print('squashfile="'+ options.squashfile +'"')
  print('squashmnt="'+ options.squashmnt +'"')
  print('basemnt="'+ options.basemnt +'"')
  print('imagens=[')
  printimagens(options,ddfilepaths)
  print('    ]')

def main():
  p = optparse.OptionParser(usage="usage: %prog [options] <ddfile>")
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
  p.add_option('--configfile', '-f',
               default="/etc/squash-mount/squash-mount.conf",
               help="defaults to /etc/squash-mount/squash-mount.conf")
  p.add_option('--noquestions', action='store_true',default=False)
  options, arguments = p.parse_args()

  if len(arguments) < 1: 
    p.print_help()
    p.error('too few arguments')
  if len(arguments) > 1:
    p.print_help()
    p.error('too many arguments')

  readconfig(options.configfile)
  if not options.noquestions:
    if options.operacao=='':
      options.operacao=askvar('operacao')
    if options.expediente=='':
      options.expediente=askvar('expediente',default=options.operacao)
    if options.squashfile=='':
      options.squashfile=askvar('squashfile',
                                default=config['squashfileprefix'] +
                                options.expediente +
                                config['squashfilesuffix'])
    if options.squashmnt=='':
      options.squashmnt=askvar('squashmnt',
                               default=config['squashmntprefix'] +
                               options.expediente +
                               config['squashmntsuffix'])
    if options.basemnt=='':
      options.basemnt=askvar('basemnt',
                             default=config['basemntprefix'] +
                             options.operacao +
                             config['basemntsuffix'])

  ddfilepaths=arguments
  printfile(options,ddfilepaths)

if __name__ == '__main__':
  main()
