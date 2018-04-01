import re


class Xform:
    encodes = {
        "I'M ": "A01",
        "I AM ": "A01",
        "I ": "B01",
        "MY ": "C01"
    }

    decodes = {
        "A01": "ARE YOU ",
        "B01": "DO YOU ",
        "C01": "M01 YOUR "
    }

    guess_decodes = {
        # "A01": "THAT YOU ARE ",
        # "B01": "THAT YOU ARE "
        "A01": "ARE YOU ",
        "B01": "ARE YOU "
    }

    encodes_context = {
        "I'M": "X01",
        "I AM": "X02",
        " I ": "X03",
        " ME ": "X04",
        " ARE ": "Y01",
        " IS ": "Y02"
    }

    decodes_context = {
        "X01": "YOU'RE",
        "X02": "YOU ARE",
        "X03": " YOU ",
        "X04": " YOU ",
        "Y01": " ",
        "Y02": " "
    }

    @staticmethod
    def xform(txt, haystack):
        for k, v in haystack.items():
            if re.match(k, txt):
                return v + txt[len(k):]
        return ""

    @staticmethod
    def encode(txt):
        encode_txt = Xform.xform(txt, Xform.encodes)
        encode_txt = Xform.context_encode(encode_txt)
        encode_txt.replace(" ", "_")
        return encode_txt

    @staticmethod
    def decode(txt):
        decode_txt = Xform.xform(txt, Xform.decodes)
        if re.match("M01 ", decode_txt):
            if decode_txt.count("Y01"):
                decode_txt = decode_txt.replace("M01 ", "ARE ")
            if decode_txt.count("Y02"):
                decode_txt = decode_txt.replace("M01 ", "IS ")
        decode_txt = Xform.context_decode(decode_txt)
        decode_txt.replace("_", " ")
        return decode_txt

    @staticmethod
    def context_encode(txt):
        encode_txt = txt
        for eFrom, eTo in Xform.encodes_context.items():
            encode_txt = encode_txt.replace(eFrom, eTo)
        return encode_txt

    @staticmethod
    def context_decode(txt):
        decode_txt = txt
        for dFrom, dTo in Xform.decodes_context.items():
            decode_txt = decode_txt.replace(dFrom, dTo)
        return decode_txt

    @staticmethod
    def form_question(txt):
        return Xform.decode(Xform.encode(txt))

    @staticmethod
    def guess_decode(txt):
        decode_txt = Xform.xform(txt, Xform.guess_decodes)
        for dFrom, dTo in Xform.decodes_context.items():
            decode_txt = decode_txt.replace(dFrom, dTo)
        decode_txt.replace("_", " ")
        return decode_txt


def main():
    while(True):
        txt = input("say something: ").upper() + " "
        if txt == "":
            break
        etxt = Xform.encode(txt)
        dtxt = Xform.decode(etxt)
        print("ENCODED TEXT: " + etxt)
        print("DECODED TEXT: " + dtxt)
    print("DECODED TEXT: " + dtxt)


if __name__ == "__main__":
    # execute only if run as a script
    main()