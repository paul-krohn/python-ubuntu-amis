#!/usr/bin/env python


from ubuntu_amis.ami_guesser import Finder


finder = Finder()

print finder.get_ami(release='trusty', region='us-east-1')
