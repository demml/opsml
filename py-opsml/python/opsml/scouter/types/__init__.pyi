class DriftType:
    Spc: "DriftType"
    Psi: "DriftType"
    Custom: "DriftType"
    LLM = "DriftType"

    def value(self) -> str: ...
    @staticmethod
    def from_value(value: str) -> "DriftType": ...

class CommonCrons:
    Every1Minute: "CommonCrons"
    Every5Minutes: "CommonCrons"
    Every15Minutes: "CommonCrons"
    Every30Minutes: "CommonCrons"
    EveryHour: "CommonCrons"
    Every6Hours: "CommonCrons"
    Every12Hours: "CommonCrons"
    EveryDay: "CommonCrons"
    EveryWeek: "CommonCrons"

    @property
    def cron(self) -> str:
        """Return the cron"""

    def get_next(self) -> str:
        """Return the next cron time"""

class DataType:
    Pandas: "DataType"
    Polars: "DataType"
    Numpy: "DataType"
    Arrow: "DataType"
