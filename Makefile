SUBDIRS=
OPERACAO=
MKFSTAB=/git/triagem/mkfstab.py
MOUNTFSTAB=/git/triagem/mountfstab.py
DEFAULTDDOPTIONS=ro,iocharset=utf8,umask=0227
DEFAULTSQUASHOPTIONS=ro,umask=227,_netdev,noexec,uid=root,gid=root,loop
DDEXTREGEXPR='\.dd$$\|\.img$$\|\.001$$\|\.iso$$\|\.tao$$'
#DEFAULTMNT='equipeXX/itemXX-tipo(HD,pendrive)-NumMaterial/'
DEFAULTMNT='XXX/itemXX-XX-MXXXX/'

.PHONY: checkop dd squash umountdd umountsquash squash subdirs $(SUBDIRS)

#subdirs: $(SUBDIRS) dd
#$(SUBDIRS):
#	$(MAKE) -f $@/Makefile

dd: checkop squash dd.fstab
	$(MOUNTFSTAB) --mkdir -v dd.fstab

checkop:
ifeq ($(strip $(OPERACAO)), )
	@echo preencha o nome da operacao no arquivo Makefile
	exit 1
endif

dd.fstab: dd.list
	sed -e '/^ *$$/d' dd.list | while read ddfile ddmnt ;\
	do mkdir -p $$ddmnt ;\
	$(MKFSTAB) $$ddfile --basemountdir=$$ddmnt \
	  --appendoptions=$(DEFAULTDDOPTIONS),gid=$(OPERACAO) ;\
	done > dd.fstab
	chmod 600 dd.fstab

dd.list:
	$(MAKE) dd.list.example
	@echo Missing file: dd.list
	exit 1

dd.list.example:
	sed -e '/^ *$$/d' squash.list | while read squashfile squashmnt ;\
	do find $$squashmnt -type f | grep $(DDEXTREGEXPR) | \
	  awk '{print $$1" $(DEFAULTMNT)" }' ; \
	done > dd.list.example
	chmod 600 dd.list.example

squash: squash.fstab
	$(MOUNTFSTAB) --mkdir -v squash.fstab

squash.fstab: squash.list
	sed -e '/^ *$$/d' squash.list | while read squashfile squashmnt ;\
	do mkdir -p -m 500 $$squashmnt ;\
	echo $$squashfile $$squashmnt auto $(DEFAULTSQUASHOPTIONS) ;\
	done > squash.fstab
	chmod 600 squash.fstab

squash.list:
	ls *.squash | while read i;\
	do echo $$i $$i.dir ;\
	done > squash.list
	chmod 600 squash.list

umount umountsquash: umountdd
	sed -e '/^ *$$/d' squash.fstab | while read file mnt rest ;\
	do umount -v $$mnt || echo -n ; done

umountdd:
	sed -e '/^ *$$/d' dd.fstab | while read file mnt rest ;\
	do umount -v $$mnt || echo -n; done
