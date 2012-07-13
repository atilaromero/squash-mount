#!/usr/bin/python
import optparse
import pyparsing as pp
import subprocess

def main():
    p=optparse.OptionParser(usage="usage: %prog [options] <fstabfile>")
    p.add_option('--mkdir', action='store_true',default=False)
    p.add_option('--umount', '-u',action='store_true',default=False)
    p.add_option('--norun', '-n',action='store_true',default=False)
    p.add_option('--verbose', '-v',action='store_true',default=False,
                 help="print commands to stderr")
    options, arguments = p.parse_args()
    if len(arguments)<1:
        p.error('fstab filepath is not optional')
    for path in arguments:
        mount(path,
              verbose=options.verbose,
              norun=options.norun,
              umount=options.umount,
              mkdir=options.mkdir)

def mount(fstabpath,verbose=False,norun=False,umount=False,mkdir=False):
    content=pp.OneOrMore(pp.QuotedString('"',escChar='\\') | 
                         pp.QuotedString("'",escChar='\\') | 
                         pp.Word(pp.printables.replace('#','')))
    with open(fstabpath) as f:
        indent=0
        for line in f:
            if len(line.strip())>0:
                lineindent=len(line)-len(line.lstrip(' \t'))
                tokens=content.parseString(line)
                if len(tokens)>0:
                    if tokens[0].startswith('!include'):
                        ret=mount(tokens[1],verbose,norun)
                    else:
                        src,dst,typ,ops=tokens[:4]
                        if not umount:
                            if mkdir:
                                cmd(['mkdir','-p',dst])
                            ret=cmd(['mount',src,dst,'-t',typ,'-o',ops],verbose,norun)
                        else:
                            ret=cmd(['umount',dst],verbose,norun)
                    #if not ret==0:
                            
            
def cmd(args,verbose=False,norun=False):
    if verbose:
        print args
    if not norun:
        return subprocess.call(args)
    return 0

if __name__=="__main__":
    main()

