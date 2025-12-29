"""Base filter interface for pipe-and-filter architecture."""

from abc import ABC, abstractmethod
import pandas as pd


class Filter(ABC):
    """
    Abstract base class for data processing filters.
    """
    
    @abstractmethod
    def apply(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Apply the filter transformation to the input DataFrame.
        """
        pass
