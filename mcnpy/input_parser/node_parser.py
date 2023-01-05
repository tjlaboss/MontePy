from mcnpy.input_parser.tokens import MCNP_Lexer
from sly import Parser
import sly

_dec = sly.yacc._decorator


class MetaBuilder(sly.yacc.ParserMeta):
    protected_names = {
        "debugfile",
        "errok",
        "error",
        "index_position",
        "line_position",
        "log",
        "parse",
        "restart",
        "tokens",
    }

    def __new__(meta, classname, bases, attributes):
        if classname != "MCNP_Parser":
            for attr_name in dir(MCNP_Parser):
                if (
                    not attr_name.startswith("_")
                    and attr_name not in MetaBuilder.protected_names
                ):
                    func = getattr(MCNP_Parser, attr_name)
                    attributes[attr_name] = func
        cls = super().__new__(meta, classname, bases, attributes)
        return cls


class MCNP_Parser(Parser, metaclass=MetaBuilder):
    tokens = MCNP_Lexer.tokens

    @_("NUMBER padding")
    def number_phrase(self, p):
        return p

    @_("NULL padding")
    def null_phrase(self, p):
        return p

    @_("SPACE")
    def padding(self, p):
        return p

    @_("padding SPACE")
    def padding(self, p):
        return p

    @_("padding DOLLAR_COMMENT")
    def padding(self, p):
        return p

    @_("padding COMMENT")
    def padding(self, p):
        return p

    @_('padding "&"')
    def padding(self, p):
        return p


class CellParser(MCNP_Parser):
    debugfile = "parser.out"

    @_("number_phrase material geometry_expr parameters")
    def cell(self, p):
        return p

    @_("number_phrase material geometry_expr")
    def cell(self, p):
        return p

    @_("null_phrase")
    def material(self, p):
        return p

    @_("number_phrase number_phrase")
    def material(self, p):
        return p

    @_('":"')
    def union(self, p):
        return p

    @_("union padding")
    def union(self, p):
        return p

    @_("geometry_expr union geometry_term")
    def geometry_expr(self, p):
        return p

    @_("geometry_expr padding")
    def geometry_expr(self, p):
        return p

    @_("geometry_term")
    def geometry_expr(self, p):
        return p.geometry_term

    @_("geometry_term padding geometry_factor")
    def geometry_term(self, p):
        return p

    @_("geometry_term padding")
    def geometry_term(self, p):
        return p

    @_("geometry_factor")
    def geometry_term(self, p):
        return p.geometry_factor

    @_("geometry_factory")
    def geometry_factor(self, p):
        return p.geometry_factory

    @_("COMPLEMENT geometry_factory")
    def geometry_factor(self, p):
        return p

    @_("NUMBER")
    def geometry_factory(self, p):
        return p

    @_('"(" geometry_expr ")"')
    def geometry_factory(self, p):
        return p

    @_("parameter")
    def parameters(self, p):
        return p

    @_("parameters parameter")
    def parameters(self, p):
        return p

    @_('KEYWORD "=" number_phrase')
    def parameter(self, p):
        return p

    @_('KEYWORD PARTICLE_DESIGNATOR "=" number_phrase')
    def parameter(self, p):
        return p
