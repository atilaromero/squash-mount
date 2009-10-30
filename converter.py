#!/usr/bin/python
import sys

f=open('fstab-mnt','r')
oldexpediente=''
nf=''
oldimagem=''
for line in f:
    a=line.strip().split()
    if a and len(a)>1:
        imagem,mnt,sisarq,opcoes,n1,n2=iter(a)
        expediente = imagem.split('/')[3]
        material=imagem.split('/')[4]
        operacao=mnt.split('/')[3]
        path="/"+"/".join(imagem.split('/')[4:])
        letra=mnt.split('/')[-1]
        mytemp=mnt.split('/')[-2].split("-")
        if len(mytemp)==3:
            item,tipo,n3=iter(mytemp)
        elif len(mytemp)>3:
            tipo=mytemp[-2]
            item="-".join(mytemp[:-2])
        elif len(mytemp)==2:
            item=mytemp[0]
            tipo=mytemp[1]
        else:
            print(mnt,mytemp)
            item=''
            tipo=''
        item=item.lstrip("item")
        equipe=''
        alvo=mnt.split('/')[-3]
        if len(mnt.split('/'))>8:
            equipe=mnt.split('/')[-4]
        offset=0
        mytemp=opcoes.split("offset=")
        if mytemp and len(mytemp)>0:
            offset=opcoes.split("offset=")[-1]
        if expediente!=oldexpediente:
            oldimagem=''
            if nf != '':
                nf.write("         ]}]\n")
                nf.close()
            nf=open("conf/"+expediente+'.conf','w')
            nf.write("#!/usr/bin/python\n")
            nf.write("operacao='" + operacao + "'\n")
            nf.write("squashfile='/storage1/" + expediente +".squash'\n")
            nf.write("squashmnt='/storage/mnt/" + expediente +"'\n")
            nf.write("basemnt='/mnt/operacoes/" + operacao +"/arquivos'\n")
            nf.write("imagens=[\n")
        else:
            if oldimagem!=imagem:
                nf.write("    ]},\n")
        if oldimagem!=imagem:
            nf.write("    {'id':'"+material+"',\n")
            nf.write("     'path':squashmnt+'"+path+"',\n")
            nf.write("     'equipe':'"+equipe+"',\n")
            nf.write("     'alvo':'"+alvo+"',\n")
            nf.write("     'item':'"+item+"',\n")
            nf.write("     'tipo':'"+tipo+"',\n")
            nf.write("     'particoes':[\n")
        else:
            nf.write("         ,\n")
        nf.write("         {'letra':'"+letra+"',\n")
        nf.write("          'tipo':'"+sisarq+"',\n")
        nf.write("          'offset':'"+offset+"',\n")
        nf.write("          'opcoesextra':'iocharset=utf8'}\n")
        
        oldimagem=imagem
        oldexpediente=expediente


if nf != '':
    nf.write("         ]}]\n")
    nf.close()
