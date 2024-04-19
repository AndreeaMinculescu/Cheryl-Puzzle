# Credits: https://github.com/sileod/llm-theory-of-mind/

class PropositionalAtom:
    def __init__(self, formula: str):
        """
        Encodes a propositional atom

        :param formula: the formula associated with the propositional atom
        """
        self.formula = formula
        # a propositional atom does not have any operator associated
        self.symbol = None
        # a propositional atom has level 0 ToM
        self.tom_level = 0

    def __str__(self):
        return self.formula


class Operator:
    def __init__(self, symbol: str):
        """
        Encodes an operator

        :param symbol: the symbol associated with the operator
        """
        self.symbol = symbol


class UnaryOperator(Operator):
    def __init__(self, symbol: str, formula: PropositionalAtom | Operator):
        """
        Encodes a unary operator. Inherits from the operator class.

        :param symbol: the symbol associated with the unary operator
        :param formula: the formula that follows the unary operator (must be of type operator or propositional atom)
        """
        # raises exception if the formula is not of type operator or propositional atom
        if not isinstance(formula, PropositionalAtom) and not isinstance(formula, Operator):
            raise TypeError("formula must be of type PropositionalAtom or Operator")

        super().__init__(symbol)
        self.formula = formula
        self.tom_level = self.formula.tom_level

    def __str__(self):
        return f"{self.symbol} {self.formula}"


class NOT(UnaryOperator):
    def __init__(self, formula: PropositionalAtom | Operator):
        """
        Encodes the NOT operator. Inherits from the unary operator class.

        :param formula: the formula that follows the NOT operator (must be of type operator or propositional atom)
        """
        super().__init__("not", formula)


class BinaryOperator(Operator):
    def __init__(self, symbol: str, left_formula: PropositionalAtom | Operator,
                 right_formula: PropositionalAtom | Operator):
        """
        Encodes a binary operator. Inherits from the operator class.

        :param symbol: the symbol associated with the unary operator
        :param left_formula: the formula on the left side of the binary operator
        (must be of type operator or propositional atom)
        :param right_formula: the formula on the right side of the binary operator
        (must be of type operator or propositional atom)
        """
        # raises exception if the left and right-hand side formulas are not of the appropriate types
        if not isinstance(left_formula, PropositionalAtom) and not isinstance(left_formula, Operator):
            raise TypeError("left-side formula must be of type PropositionalAtom or Operator")
        if not isinstance(right_formula, PropositionalAtom) and not isinstance(right_formula, Operator):
            raise TypeError("right-side formula must be of type PropositionalAtom or Operator")

        super().__init__(symbol)
        self.left_formula = left_formula
        self.right_formula = right_formula
        self.tom_level = max(self.left_formula.tom_level, self.right_formula.tom_level)

    def __str__(self):
        return f"({self.left_formula} {self.symbol} {self.right_formula})"


class KNOW(Operator):
    def __init__(self, who: str, what: PropositionalAtom | Operator):
        """
        Encodes a knowledge operator of the type "X knows that Y".

        :param who: the agent that knows some information or X
        :param what: the formula that the egent knows or Y (must be of type operator or propositional atom)
        """
        # raises exception if the formula is not of the appropriate type
        if not isinstance(what, PropositionalAtom) and not isinstance(what, Operator):
            raise TypeError("'what' formula must be of type PropositionalAtom or Operator")

        super().__init__("know")
        self.formula = what
        self.agent = who
        self.tom_level = self.compute_tom_level()

    def compute_tom_level(self):
        """
        Given a knowledge formula, computes the ToM level by recursively counting the number of consecutive knowledge
        formulas with different agents

        :return: the ToM level of the formula
        """
        if isinstance(self.formula, KNOW):
            # if the previous agent is the same as the current, then don't increase the ToM level
            if self.formula.agent == self.agent:
                return self.formula.tom_level
        return self.formula.tom_level + 1

    def __str__(self):
        return f"{self.agent} knows that {self.formula}"


if __name__ == "__main__":
    k = KNOW("a", KNOW("a", PropositionalAtom("c")))
    print(k)
    print(k.tom_level)