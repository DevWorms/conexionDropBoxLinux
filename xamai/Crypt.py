#!/usr/bin/env python2.6
# -*- coding: utf-8 -*-

'''
Importante!
NO cambiar mask, si lo hace debe volver a cifrarse el token y cambiarlo en upload.py
'''
class Crypt():
    mask = 'p4ssw0rd'
    nmask = [ord(c) for c in mask]
    lmask = len(mask)

    def obfuscate(self, s):
        return ''.join([chr(ord(c) ^ self.nmask[i % self.lmask])
                        for i, c in enumerate(s)])
