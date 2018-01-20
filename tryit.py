dict = {"key1": "val1",
        "key2": "val2"}
class a:
    text = "old text"


xa = a()
xb = xa
print(xa.text)
print(xb.text)

xa.text = "new text"
print(xb.text)

