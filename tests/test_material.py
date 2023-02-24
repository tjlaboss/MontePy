from unittest import TestCase

import mcnpy

from mcnpy.data_inputs.element import Element
from mcnpy.data_inputs.isotope import Isotope
from mcnpy.data_inputs.material import Material
from mcnpy.data_inputs.material_component import MaterialComponent
from mcnpy.data_inputs.thermal_scattering import ThermalScatteringLaw
from mcnpy.errors import MalformedInputError, UnknownElement
from mcnpy.input_parser.block_type import BlockType
from mcnpy.input_parser.mcnp_input import Input, Comment


class testMaterialClass(TestCase):
    def test_material_init(self):
        # test invalid material number
        input_card = Input(["Mfoo"], BlockType.DATA)
        with self.assertRaises(MalformedInputError):
            Material(input_card, None)
        input_card = Input(["M-20"], BlockType.DATA)
        with self.assertRaises(MalformedInputError):
            Material(input_card, None)

        in_str = "M20 1001.80c 0.5 8016.80c 0.5"
        input_card = Input([in_str], BlockType.DATA)
        material = Material(input_card, None)
        self.assertEqual(material.number, 20)
        self.assertEqual(material.old_number, 20)
        self.assertTrue(material.is_atom_fraction)
        for component in material.material_components:
            self.assertEqual(material.material_components[component].fraction, 0.5)

        in_str = "M20 1001.80c -0.5 8016.80c -0.5"
        input_card = Input([in_str], BlockType.DATA)
        material = Material(input_card, None)
        self.assertFalse(material.is_atom_fraction)
        for component in material.material_components:
            self.assertEqual(material.material_components[component].fraction, 0.5)

        # test bad fraction
        in_str = "M20 1001.80c foo"
        input_card = Input([in_str], BlockType.DATA)
        with self.assertRaises(MalformedInputError):
            material = Material(input_card, None)
        # test mismatch fraction
        in_str = "M20 1001.80c 0.5 8016.80c -0.5"
        input_card = Input([in_str], BlockType.DATA)
        with self.assertRaises(MalformedInputError):
            material = Material(input_card, None)
        # test parameters
        in_str = "M20 1001.80c 0.5 8016.80c 0.5 Gas=1"
        input_card = Input([in_str], BlockType.DATA)
        material = Material(input_card, None)

        self.assertEqual(material.parameter_string, "Gas=1")

    def test_material_validator(self):
        material = Material()
        with self.assertRaises(mcnpy.errors.IllegalState):
            material.validate()
        with self.assertRaises(mcnpy.errors.IllegalState):
            material.format_for_mcnp_input((6, 2, 0))

    def test_material_setter(self):
        in_str = "M20 1001.80c 0.5 8016.80c 0.5"
        input_card = Input([in_str], BlockType.DATA)
        material = Material(input_card, None)
        material.number = 30
        self.assertEqual(material.number, 30)
        with self.assertRaises(TypeError):
            material.number = "foo"
        with self.assertRaises(ValueError):
            material.number = -5

    def test_material_str(self):
        in_str = "M20 1001.80c 0.5 8016.80c 0.4 94239.80c 0.1"
        input_card = Input([in_str], BlockType.DATA)
        material = Material(input_card, None)
        answers = """MATERIAL: 20 fractions: atom
 H-1   (80c) (Value, 0.5, padding: (Padding, [' ']))
 O-16  (80c) (Value, 0.4, padding: (Padding, [' ']))
Pu-239 (80c) (Value, 0.1, padding: None)
"""
        output = repr(material)
        print(output)
        self.assertEqual(output, answers)
        output = str(material)
        self.assertEqual(output, "MATERIAL: 20, ['hydrogen', 'oxygen', 'plutonium']")

    def test_material_sort(self):
        in_str = "M20 1001.80c 0.5 8016.80c 0.5"
        input_card = Input([in_str], BlockType.DATA)
        material1 = Material(input_card, None)
        in_str = "M30 1001.80c 0.5 8016.80c 0.5"
        input_card = Input([in_str], BlockType.DATA)
        material2 = Material(input_card, None)
        sort_list = sorted([material2, material1])
        answers = [material1, material2]
        for i, mat in enumerate(sort_list):
            self.assertEqual(mat, answers[i])

    def test_material_format_mcnp(self):
        in_strs = ["M20 1001.80c 0.5", "     8016.80c         0.5"]
        input_card = Input(in_strs, BlockType.DATA)
        material = Material(input_card, None)
        material.number = 25
        answers = ["M25 1001.80c 0.5", "     8016.80c         0.5"]
        output = material.format_for_mcnp_input((6, 2, 0))
        self.assertEqual(len(answers), len(output))
        for i, line in enumerate(output):
            self.assertEqual(line, answers[i])

    def test_material_comp_init(self):
        # test fraction test
        with self.assertRaises(ValueError):
            MaterialComponent(Isotope("1001.80c"), -0.1)

        # test bad fraction
        with self.assertRaises(TypeError):
            MaterialComponent(Isotope("1001.80c"), "hi")

    def test_material_card_pass_through(self):
        in_str = "M20 1001.80c 0.5 8016.80c 0.5"
        input_card = Input([in_str], BlockType.DATA)
        material = Material(input_card, None)
        self.assertEqual(material.format_for_mcnp_input((6, 2, 0)), [in_str])
        material.number = 5
        self.assertNotIn("8016", material.format_for_mcnp_input((6, 2, 0)))


class TestIsotope(TestCase):
    def test_isotope_init(self):
        isotope = Isotope("1001.80c")
        self.assertEqual(isotope.ZAID, "1001")
        self.assertEqual(isotope.Z, 1)
        self.assertEqual(isotope.A, 1)
        self.assertEqual(isotope.element.Z, 1)
        self.assertEqual(isotope.library, "80c")
        with self.assertRaises(ValueError):
            Isotope("1001.80c.5")
        with self.assertRaises(ValueError):
            Isotope("hi.80c")
        with self.assertRaises(MalformedInputError):
            Isotope("1001")

    def test_isotope_metastable_init(self):
        isotope = Isotope("13426.02c")
        self.assertEqual(isotope.ZAID, "13426")
        self.assertEqual(isotope.Z, 13)
        self.assertEqual(isotope.A, 26)
        self.assertTrue(isotope.is_metastable)
        self.assertEqual(isotope.meta_state, 1)
        isotope = Isotope("92635.02c")
        self.assertEqual(isotope.A, 235)
        self.assertEqual(isotope.meta_state, 1)
        isotope = Isotope("92935.02c")
        self.assertEqual(isotope.A, 235)
        self.assertEqual(isotope.meta_state, 4)
        self.assertEqual(isotope.mcnp_str(), "92935.02c")
        edge_cases = [
            ("4412", 4, 12, 1),
            ("4413", 4, 13, 1),
            ("4414", 4, 14, 1),
            ("36569", 36, 69, 2),
            ("77764", 77, 164, 3),
        ]
        for ZA, Z_ans, A_ans, isomer_ans in edge_cases:
            isotope = Isotope(ZA + ".80c")
            self.assertEqual(isotope.Z, Z_ans)
            self.assertEqual(isotope.A, A_ans)
            self.assertEqual(isotope.meta_state, isomer_ans)
        with self.assertRaises(ValueError):
            isotope = Isotope("13826.02c")

    def test_isotope_get_base_zaid(self):
        isotope = Isotope("92635.02c")
        self.assertEqual(isotope.get_base_zaid(), 92235)

    def test_isotope_library_setter(self):
        isotope = Isotope("1001.80c")
        isotope.library = "70c"
        self.assertEqual(isotope.library, "70c")
        with self.assertRaises(TypeError):
            isotope.library = 1

    def test_isotope_str(self):
        isotope = Isotope("1001.80c")
        self.assertEqual(isotope.mcnp_str(), "1001.80c")
        self.assertEqual(str(isotope), " H-1   (80c)")
        self.assertEqual(
            repr(isotope), "ZAID=1001, Z=1, A=1, element=hydrogen, library=80c"
        )
        isotope = Isotope("94239.80c")
        self.assertEqual(isotope.mcnp_str(), "94239.80c")
        self.assertEqual(str(isotope), "Pu-239 (80c)")


class TestThermalScattering(TestCase):
    def test_thermal_scattering_init(self):
        # test wrong input type assertion
        input_card = Input(["M20"], BlockType.DATA)
        with self.assertRaises(MalformedInputError):
            ThermalScatteringLaw(input_card)

        input_card = Input(["Mt20 grph.20t"], BlockType.DATA)
        card = ThermalScatteringLaw(input_card)
        self.assertEqual(card.old_number, 20)
        self.assertEqual(card.thermal_scattering_laws, ["grph.20t"])

        input_card = Input(["Mtfoo"], BlockType.DATA)
        with self.assertRaises(MalformedInputError):
            ThermalScatteringLaw(input_card, None)
        input_card = Input(["Mt-20"], BlockType.DATA)
        with self.assertRaises(MalformedInputError):
            ThermalScatteringLaw(input_card, None)
        in_str = "M20 1001.80c 0.5 8016.80c 0.5"
        input_card = Input([in_str], BlockType.DATA)
        material = Material(input_card, None)
        comment = Comment(["c foo"], ["foo"])
        card = ThermalScatteringLaw(comments=comment, material=material)
        self.assertEqual(card.parent_material, material)

    def test_thermal_scatter_validate(self):
        thermal = ThermalScatteringLaw()
        with self.assertRaises(mcnpy.errors.IllegalState):
            thermal.validate()
        with self.assertRaises(mcnpy.errors.IllegalState):
            thermal.format_for_mcnp_input((6, 2, 0))
        material = Material()
        material.number = 1
        thermal._old_material_number = 1
        material.update_pointers([thermal])
        with self.assertRaises(mcnpy.errors.IllegalState):
            thermal.validate()

    def test_thermal_scattering_add(self):
        in_str = "Mt20 grph.20t"
        input_card = Input([in_str], BlockType.DATA)
        card = ThermalScatteringLaw(input_card)
        card.add_scattering_law("grph.21t")
        self.assertEqual(len(card.thermal_scattering_laws), 2)
        self.assertEqual(card.thermal_scattering_laws, ["grph.20t", "grph.21t"])
        card.thermal_scattering_laws = ["grph.22t"]
        self.assertEqual(card.thermal_scattering_laws, ["grph.22t"])

    def test_thermal_scattering_setter(self):
        in_str = "Mt20 grph.20t"
        input_card = Input([in_str], BlockType.DATA)
        card = ThermalScatteringLaw(input_card)
        laws = ["grph.21t"]
        card.thermal_scattering_laws = laws
        self.assertEqual(card.thermal_scattering_laws, laws)
        with self.assertRaises(TypeError):
            card.thermal_scattering_laws = 5
        with self.assertRaises(TypeError):
            card.thermal_scattering_laws = [5]

    def test_thermal_scattering_material_add(self):
        in_str = "M20 1001.80c 1.0"
        input_card = Input([in_str], BlockType.DATA)
        card = Material(input_card)
        card.add_thermal_scattering("grph.21t")
        self.assertEqual(len(card.thermal_scattering.thermal_scattering_laws), 1)
        self.assertEqual(card.thermal_scattering.thermal_scattering_laws, ["grph.21t"])
        card.thermal_scattering_laws = ["grph.22t"]
        self.assertEqual(card.thermal_scattering_laws, ["grph.22t"])
        with self.assertRaises(TypeError):
            card.add_thermal_scattering(5)

    def test_thermal_scattering_format_mcnp(self):
        in_str = "Mt20 grph.20t"
        input_card = Input([in_str], BlockType.DATA)
        card = ThermalScatteringLaw(input_card)
        in_str = "M20 1001.80c 0.5 8016.80c 0.5"
        input_card = Input([in_str], BlockType.DATA)
        material = Material(input_card, None)
        material.update_pointers([card])
        material.thermal_scattering.thermal_scattering_laws = ["grph.20t"]
        self.assertEqual(card.format_for_mcnp_input((6, 2, 0)), ["Mt20 grph.20t"])

    def test_thermal_str(self):
        in_str = "Mt20 grph.20t"
        input_card = Input([in_str], BlockType.DATA)
        card = ThermalScatteringLaw(input_card)
        self.assertEqual(str(card), "THERMAL SCATTER: ['grph.20t']")
        self.assertEqual(
            repr(card),
            "THERMAL SCATTER: material: None, old_num: 20, scatter: ['grph.20t']",
        )


class TestElement(TestCase):
    def test_element_init(self):
        for Z in range(1, 119):
            element = Element(Z)
            self.assertEqual(element.Z, Z)

        with self.assertRaises(UnknownElement):
            Element(119)

        spot_check = {
            1: ("H", "hydrogen"),
            40: ("Zr", "zirconium"),
            92: ("U", "uranium"),
            94: ("Pu", "plutonium"),
            29: ("Cu", "copper"),
            13: ("Al", "aluminum"),
        }
        for z, (symbol, name) in spot_check.items():
            element = Element(z)
            self.assertEqual(z, element.Z)
            self.assertEqual(symbol, element.symbol)
            self.assertEqual(name, element.name)

    def test_element_str(self):
        element = Element(1)
        self.assertEqual(str(element), "hydrogen")
        self.assertEqual(repr(element), "Z=1, symbol=H, name=hydrogen")

    def test_get_by_symbol(self):
        element = Element.get_by_symbol("Hg")
        self.assertEqual(element.name, "mercury")
        with self.assertRaises(UnknownElement):
            Element.get_by_symbol("Hi")

    def test_get_by_name(self):
        element = Element.get_by_name("mercury")
        self.assertEqual(element.symbol, "Hg")
        with self.assertRaises(UnknownElement):
            Element.get_by_name("hudrogen")


class TestParticle(TestCase):
    def test_particle_str(self):
        part = mcnpy.Particle("N")
        self.assertEqual(str(part), "neutron")
