# -*- coding: utf-8 -*-
"""Models for API requests & responses."""
import dataclasses
import datetime
import logging
import typing as t

from ....exceptions import ApiError
from ....tools import coerce_int, dt_now, dt_parse
from ..base import BaseModel

LOGGER = logging.getLogger(__name__)


@dataclasses.dataclass
class AssetTypeHistoryDate(BaseModel):
    """Human exposure of history date for a specific asset type."""

    date_api: str
    date_api_exact: str
    asset_type: str
    document_meta: t.Optional[dict] = dataclasses.field(default_factory=dict)

    @property
    def days_ago(self) -> int:
        """Number of days since date_api passed."""
        return self.delta.days

    @property
    def delta(self) -> datetime.timedelta:
        """Pass."""
        return dt_now() - self.date

    def calculate_delta(self, value: datetime.datetime) -> datetime.timedelta:
        """Calculate the delta between the date property and a given datetime object."""
        return abs(self.date - value)

    def calculate_days_ago(self, value: datetime.datetime) -> int:
        """Calculate the number of days between the date property and a given datetime object."""
        return self.calculate_delta(value=value).days

    @property
    def date(self) -> datetime.datetime:
        """Get the history date as datetime object."""
        if not hasattr(self, "_date"):
            setattr(self, "_date", dt_parse(obj=self.date_api_exact, default_tz_utc=True))
        return getattr(self, "_date")

    def __str__(self) -> str:
        """Pass."""
        return f"date={self.date}, days_ago={self.days_ago}"

    @staticmethod
    def get_schema_cls() -> t.Any:
        """Get the schema for this model."""
        return None


@dataclasses.dataclass
class AssetTypeHistoryDates(BaseModel):
    """Human exposure of history dates for a specific asset type."""

    asset_type: str
    values: dict
    document_meta: t.Optional[dict] = dataclasses.field(default_factory=dict)

    DATE_ONLY_FMT: t.ClassVar[str] = "%Y-%m-%d"
    DATE_ONLY_VALID_FMTS: t.ClassVar[t.List[str]] = ["YYYY-MM-DD", "YYYYMMDD"]

    @property
    def dates(self) -> t.List[AssetTypeHistoryDate]:
        """Get the valid history dates for this asset type."""
        if not hasattr(self, "_dates"):
            # noinspection PyAttributeOutsideInit
            self._dates = [
                AssetTypeHistoryDate(date_api=k, date_api_exact=v, asset_type=self.asset_type)
                for k, v in self.values.items()
            ]
        return self._dates

    @property
    def dates_by_days_ago(self) -> t.Dict[int, AssetTypeHistoryDate]:
        """Get the valid history dates for this asset type keyed by days_ago."""
        return {x.days_ago: x for x in self.dates}

    def get_date_nearest(
        self, value: t.Union[str, bytes, datetime.timedelta, datetime.datetime]
    ) -> t.Optional[AssetTypeHistoryDate]:
        """Get a valid history date that is nearest to the supplied value."""
        nearest: t.Optional[AssetTypeHistoryDate] = None
        if self.dates:
            pivot: datetime.datetime = dt_parse(obj=value, default_tz_utc=True)
            nearest: AssetTypeHistoryDate = min(self.dates, key=lambda x: x.calculate_delta(pivot))
            LOGGER.info(f"Closest {self.asset_type} history date to {pivot} found: {nearest}")
        return nearest

    def get_date_nearest_days_ago(self, value: int) -> t.Optional[AssetTypeHistoryDate]:
        """Get a valid history date that is nearest to the supplied value."""
        nearest: t.Optional[AssetTypeHistoryDate] = None

        if self.dates:
            pivot: int = coerce_int(value)
            nearest = min(
                self.dates,
                key=lambda x: x.days_ago - pivot if x.days_ago >= pivot else pivot - x.days_ago,
            )
            LOGGER.info(f"Closest {self.asset_type} history days ago to {pivot} found: {nearest}")
        return nearest

    def get_date_by_date(
        self,
        value: t.Optional[t.Union[str, datetime.timedelta, datetime.datetime]] = None,
        exact: bool = True,
    ) -> t.Optional[str]:
        """Get a valid history date.

        Args:
            value: date to get history date for
            exact: if True, raise error if date is not valid, else return nearest valid date
        """
        if value:
            try:
                dt: datetime.datetime = dt_parse(obj=value, default_tz_utc=True)
            except Exception:
                valid = " or ".join(self.DATE_ONLY_VALID_FMTS)
                raise ApiError(f"Invalid history date format {value!r}, format must be {valid}")

            date_api: str = dt.strftime(self.DATE_ONLY_FMT)
            if date_api in self.values:
                return self.values[date_api]

            if exact:
                err = f"Invalid exact history date {date_api!r}"
                raise ApiError(f"{err}\n\n{self}\n\n{err}")

            nearest: t.Optional[AssetTypeHistoryDate] = self.get_date_nearest(value=dt)
            if isinstance(nearest, AssetTypeHistoryDate):
                return nearest.date_api_exact

    def get_date_by_days_ago(
        self, value: t.Optional[t.Union[int, str]] = None, exact: bool = True
    ) -> t.Optional[str]:
        """Get date by number of days ago.

        Args:
            value: days ago to get history date for
            exact: if True, raise error if days ago is not valid, else return nearest valid date
        """
        if value is not None:
            value: int = coerce_int(value)
            if value in self.dates_by_days_ago:
                return self.dates_by_days_ago[value].date_api_exact

            if exact and value != 0:
                nums = sorted(list(self.dates_by_days_ago))
                err = f"Invalid exact days ago {value!r} (highest={nums[-1]}, lowest={nums[0]})"
                raise ApiError(f"{err}\n{self}\n\n{err}")

            nearest: t.Optional[AssetTypeHistoryDate] = self.get_date_nearest_days_ago(value=value)
            if isinstance(nearest, AssetTypeHistoryDate):
                return nearest.date_api_exact

    def get_date(
        self,
        date: t.Optional[t.Union[str, datetime.timedelta, datetime.datetime]] = None,
        days_ago: t.Optional[t.Union[int, str]] = None,
        exact: bool = True,
    ) -> t.Optional[str]:
        """Get a valid history date by a specific date or number of days ago.

        Args:
            date: date to get history date for
            days_ago: days ago to get history date for
            exact: if True, raise error if date is not valid, else return nearest valid date
        """
        return self.get_date_by_date(value=date, exact=exact) or self.get_date_by_days_ago(
            value=days_ago, exact=exact
        )

    @staticmethod
    def get_schema_cls() -> t.Any:
        """Get the schema for this model."""
        return None

    def __repr__(self) -> str:
        """Pass."""
        return f"asset_type={self.asset_type}, count={len(self.dates)}"

    def __str__(self) -> str:
        """Pass."""
        items = [
            f"Valid history dates for {self.asset_type}:",
            *[f"{x}" for x in self.dates],
        ]
        return "\n".join(items)
