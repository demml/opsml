from typing import List, Type


class DependentVariable:
    def __init__(self, name: str, level: str):
        self.name = name.upper()
        self.level = level.upper()

    @property
    def column_name(self) -> str:
        raise NotImplementedError

    @property
    def eval_flg(self) -> str:
        raise NotImplementedError

    @property
    def eval_outlier(self) -> str:
        raise NotImplementedError

    @staticmethod
    def validate(level: str) -> bool:
        return True


class BundleVariable(DependentVariable):
    @property
    def column_name(self) -> str:
        return f"{self.level}_{self.name}_TIME"

    @property
    def eval_flg(self) -> str:
        return f"{self.name}_EVAL_FLG"

    @property
    def eval_outlier(self) -> str:
        return f"{self.name}_EVAL_OUTLIER"

    @staticmethod
    def validate(level: str) -> bool:
        if level.upper() == "BUNDLE":
            return True
        return False


class OrderVariable(DependentVariable):
    @property
    def column_name(self) -> str:
        return f"{self.name}_TIME"

    @property
    def eval_flg(self) -> str:
        return f"{self.name}_EVAL_FLG"

    @property
    def eval_outlier(self) -> str:
        return f"{self.name}_EVAL_OUTLIER"

    @staticmethod
    def validate(level: str) -> bool:
        if level.upper() == "ORDER":
            return True
        return False


class StopVariable(DependentVariable):
    @property
    def column_name(self) -> str:
        return f"{self.name}_TIME"

    @property
    def eval_flg(self) -> str:
        return "EVAL_FLG"

    @property
    def eval_outlier(self) -> str:
        return "EVAL_OUTLIER"

    @staticmethod
    def validate(level: str) -> bool:
        if level.upper() == "STOP":
            return True
        return False


class DependentVariables:
    def __init__(self, level: str, dependent_vars: List[str]):
        self.level = level
        self.dependent_vars = self.get_dependent_variable_attrs(dependent_vars=dependent_vars)

    def get_dependent_variable_attrs(self, dependent_vars: List[str]):

        var_model = self.get_variable_type()

        return [var_model(name=depen_var, level=self.level) for depen_var in dependent_vars]

    def get_variable_type(self) -> Type[DependentVariable]:

        var_model = next(
            var_model
            for var_model in DependentVariable.__subclasses__()
            if var_model.validate(
                level=self.level,
            )
        )
        return var_model

    @property
    def column_names(self):
        return [depen_var.column_name for depen_var in self.dependent_vars]

    @property
    def eval_flgs(self):
        return [depen_var.eval_flg for depen_var in self.dependent_vars]

    @property
    def eval_outlier(self):
        return [depen_var.eval_outlier for depen_var in self.dependent_vars]
