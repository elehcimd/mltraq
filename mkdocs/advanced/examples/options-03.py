from pprint import pprint

from mltraq.utils.base_options import BaseOptions


class OptionsA(BaseOptions):
    pass


class OptionsB(BaseOptions):
    pass


options_a = OptionsA.instance()
options_a.set("hello", 123)

options_b = OptionsB.instance()
options_b.set("world", 456)

options_a.set("options_b", options_b.values)

pprint(options_a.values, width=70)
