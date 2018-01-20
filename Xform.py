import re


class Xform:

    encodes = {
        "I'M ": "a01",
        "I AM ": "a01",
        "I ": "b01"
    }

    decodes = {
        "a01": "ARE YOU ",
        "b01": "DO YOU "
    }

    encodes_context = {
        "I'M ": "x01",
        "I AM ": "x02"
    }

    decodes_context = {
        "x01": "YOU'RE ",
        "x02": "YOU ARE "
    }

    @staticmethod
    def xform(txt, haystack):
        for k, v in haystack.items():
            if re.match(k, txt):
                return v + txt[len(k):]
        return ""

    @staticmethod
    def encode(txt):
        etxt = Xform.xform(txt, Xform.encodes)
        for eFrom, eTo in Xform.encodes_context.items():
            etxt = etxt.replace(eFrom, eTo)
        etxt.replace(" ", "_")
        return etxt

    @staticmethod
    def decode(txt):
        dtxt = Xform.xform(txt, Xform.decodes)
        for dFrom, dTo in Xform.decodes_context.items():
            dtxt = dtxt.replace(dFrom, dTo)
        dtxt.replace("_", " ")
        return dtxt
