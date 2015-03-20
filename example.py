#!/usr/bin/env python

from optparse import OptionParser
from ubuntu_amis.ami_guesser import Finder


args_options = OptionParser()
args_options.add_option("-r", "--release", dest="release", default="trusty", help="release codeame, eg lucid")
args_options.add_option("--region", dest="region", default="us-east-1", help="aws region name, eg ap-southeast-1")
args_options.add_option("-i", "--instance_arch", dest="instance_arch",
                        help="instance architecture, eg hvm or paravirtual", default="hvm")
args_options.add_option("-c", "--cpu_arch", dest="cpu_arch", help="cpu architecture, i386 or amd64", default="amd64")
args_options.add_option("-b", dest="boot_store", default="instance-store",
                        help="boot/root volume type, eg instance-store or ebs-ssd")
(options, args) = args_options.parse_args()

finder = Finder()

print finder.get_ami(
    release=options.release,
    region=options.region,
    instance_arch=options.instance_arch,
    cpu_arch=options.cpu_arch,
    root_store=options.boot_store,
)
