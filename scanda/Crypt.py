#!/usr/bin/env python
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

'''
# No es necesario, pero si RECOMENDADO antes de cifrar pasar el token a base64, el cifrado solo trabaja con caracteres ASCII
app = Crypt()

# Ejemplo para 'encriptar una cadena'
print repr(
        app.obfuscate(
            base64.b64encode('f-taP7WG2wAAAAAAAAAAEPgxbzHQ7EDctvivjSJCqLwCA0tcsgyuRT7H9vnxqwVK')
        ).encode('utf-8')
    )

# Ejemplo para 'desencriptar una cadena'
print base64.b64decode(
    repr(
        app.obfuscate(
            '*]BC.f3W&\x04\x10\n\x13\x004&!a51&e4&!a55"w\x16P)Z\x03:"d\x16""s=C\x13]\x1eV\x11X=8&\x034)\x14\x04=1:x \x0e\x13\x06\x17F\x13f81>\x04\x14F\x13]GP\x13l\x17$$GOY'.decode('utf-8')
            )
        )
    )
'''