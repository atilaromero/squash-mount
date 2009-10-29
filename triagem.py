#!/usr/bin/python
import os

def importConfig(configfile):
  a={}
  b={}
  execfile(configfile,a,b)
  return b

confpath="/etc/triagem/triagem.conf"
config=importConfig(confpath)

expedientes={}
for f in os.listdir(config['direxpedientes']):
  expedientes[f]=importConfig(os.path.join(config['direxpedientes'],f))

def getmountpoint(expediente,imagem,particao):
  return os.path.join(expediente['basemnt'],
                      imagem['equipe'],
                      imagem['alvo'],
                      "item"+str(imagem['item'])+ "-" +
                      imagem['tipo'] + "-" +
                      imagem['id'],
                      particao['letra'])

def checkpaths(expediente):
  exppaths=[]
  for imagem in expediente['imagens']:
    for particao in imagem['particoes']:
      mountpoint=getmountpoint(expediente,imagem,particao)
      if os.path.exists(mountpoint) and os.path.isdir(mountpoint):
        print(mountpoint," existe")
      else:
        print(mountpoint," nao existe")
        
  

for filename,expediente in expedientes.iteritems():
  checkpaths(expediente)
