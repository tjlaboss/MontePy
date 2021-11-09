from abc import ABC, abstractmethod
import textwrap


class MCNP_Card(ABC):
    """
    Abstract class for semantic representations of MCNP input cards.
    """

    def __init__(self, comment=None):
        if comment:
            self.__comment = comment

    @abstractmethod
    def format_for_mcnp_input(self):
        """
        Creates a string representation of this card that can be
        written to file.

        :return: a list of strings for the lines that this card will occupy.
        :rtype: list
        """
        pass

    @property
    def comment(self):
        """
        The preceding comment block to this card if any.

        :rtype: Comment
        """
        if hasattr(self, "_MCNP_Card__comment"):
            return self.__comment

    @staticmethod
    def wrap_words_for_mcnp(words, mcnp_version, is_first_line):
        """
        Wraps the list of the words to be a well formed MCNP input.

        multi-line cards will be handled by using the indentation format,
        and not the "&" method.

        :param words: A list of the "words" or data-grams that needed to added to this card.
                      Each word will be separated by at least one space.
        :type words: list
        :param mcnp_version: the tuple for the MCNP that must be formatted for.
        :type mcnp_version: tuple
        :param is_first_line: If true this will be the beginning of an MCNP card.
                             The first line will not be indented.
        :type is_first_line: bool
        :returns: A list of strings that can be written to an input file, one item to a line.
        :rtype: list
        """
        string = " ".join(words)
        return MCNP_Card.wrap_string_for_mcnp(string, mcnp_version, is_first_line)

    @staticmethod
    def wrap_string_for_mcnp(string, mcnp_version, is_first_line):
        """
        Wraps the list of the words to be a well formed MCNP input.

        multi-line cards will be handled by using the indentation format,
        and not the "&" method.

        :param string: A long string that needs to be chunked appropriately for MCNP inputs
        :type string: str
        :param mcnp_version: the tuple for the MCNP that must be formatted for.
        :type mcnp_version: tuple
        :param is_first_line: If true this will be the beginning of an MCNP card.
                             The first line will not be indented.
        :type is_first_line: bool
        :returns: A list of strings that can be written to an input file, one item to a line.
        :rtype: list
        """
        line_length = 0
        indent_length = 0
        if mcnp_version[0] == 6.2:
            line_length = 128
            indent_length = 5
        if is_first_line:
            initial_indent = 0
        else:
            initial_indent = indent_length
        wrapper = textwrap.TextWrapper(
            width=line_length,
            initial_indent=" " * initial_indent,
            subsequent_indent=" " * indent_length,
        )
        return wrapper.wrap(string)
