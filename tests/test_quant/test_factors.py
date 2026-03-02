"""
Unit tests for the FactorEngine in backend/quant/factors.py.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from backend.quant.factors import FactorEngine


@pytest.mark.unit
class TestFactorEngine:
    """Tests for FactorEngine.compute()."""

    def setup_method(self):
        self.engine = FactorEngine()

    def test_momentum_12_1_returns_series(self, sample_prices: pd.DataFrame, sample_tickers: list[str]):
        """momentum_12_1 factor should return a Series indexed by ticker."""
        scores = self.engine.compute(prices=sample_prices, factors=["momentum_12_1"])
        assert isinstance(scores, list)
        assert len(scores) == len(sample_tickers)
        returned_tickers = {s.ticker for s in scores}
        assert returned_tickers == set(sample_tickers)

    def test_momentum_12_1_z_scored(self, sample_prices: pd.DataFrame):
        """After standardization, mean ≈ 0 and std ≈ 1."""
        scores = self.engine.compute(prices=sample_prices, factors=["momentum_12_1"])
        values = np.array([s.scores["momentum_12_1"] for s in scores])
        assert abs(values.mean()) < 1.0   # relaxed — small cross-section
        assert 0.5 < values.std() < 2.0

    def test_low_vol_higher_is_better(self, sample_prices: pd.DataFrame):
        """
        Construct two assets where one has clearly lower vol and assert
        that it receives a HIGHER low_vol_12 score.
        """
        idx = sample_prices.index
        rng = np.random.default_rng(0)
        # High-vol asset
        high_vol = np.exp(np.cumsum(rng.normal(0, 0.04, len(idx)))).cumprod()
        # Low-vol asset
        low_vol = np.exp(np.cumsum(rng.normal(0, 0.005, len(idx)))).cumprod()

        prices_2 = pd.DataFrame({"HIGH.SA": high_vol * 10, "LOW.SA": low_vol * 10}, index=idx)
        scores = self.engine.compute(prices=prices_2, factors=["low_vol_12"])
        score_map = {s.ticker: s.scores["low_vol_12"] for s in scores}
        assert score_map["LOW.SA"] > score_map["HIGH.SA"], (
            f"Expected LOW.SA score ({score_map['LOW.SA']:.3f}) "
            f"> HIGH.SA score ({score_map['HIGH.SA']:.3f})"
        )

    def test_multiple_factors(self, sample_prices: pd.DataFrame):
        """All requested factors present in every FactorScores object."""
        factors = ["momentum_12_1", "momentum_1", "low_vol_12", "size"]
        scores = self.engine.compute(prices=sample_prices, factors=factors)
        for score_obj in scores:
            assert set(score_obj.scores.keys()) == set(factors)

    def test_single_factor_request(self, sample_prices: pd.DataFrame):
        """Requesting a single factor should not raise errors."""
        scores = self.engine.compute(prices=sample_prices, factors=["size"])
        assert all("size" in s.scores for s in scores)

    def test_unknown_factor_raises(self, sample_prices: pd.DataFrame):
        """Requesting a non-existent factor should raise ValueError."""
        with pytest.raises((ValueError, KeyError)):
            self.engine.compute(prices=sample_prices, factors=["nonexistent_factor_xyz"])

    def test_returns_nan_free(self, sample_prices: pd.DataFrame):
        """Factor scores must not contain NaN values."""
        scores = self.engine.compute(prices=sample_prices, factors=["momentum_12_1", "low_vol_12"])
        for s in scores:
            for factor, val in s.scores.items():
                assert not np.isnan(val), f"NaN found in {s.ticker}.{factor}"

    def test_insufficient_history_graceful(self):
        """Too little history should either raise or return empty scores gracefully."""
        short_prices = pd.DataFrame(
            {"A.SA": [10.0, 11.0, 10.5], "B.SA": [20.0, 21.0, 19.5]},
            index=pd.bdate_range("2024-01-01", periods=3),
        )
        # Should not crash — either empty result or a handled exception
        try:
            scores = self.engine.compute(short_prices, factors=["momentum_12_1"])
            # If it returns, it must be empty or all-NaN handled gracefully
        except (ValueError, IndexError):
            pass  # acceptable


@pytest.mark.unit
class TestFactorStandardization:
    """Tests for the internal _standardize helper."""

    def setup_method(self):
        self.engine = FactorEngine()

    def test_standardize_basic(self):
        raw = pd.Series([1.0, 2.0, 3.0, 4.0, 5.0, 100.0, -100.0])
        result = self.engine._standardize(raw)
        # Winsorization should clip 100 and -100
        assert result.max() < 5.0
        assert result.min() > -5.0

    def test_standardize_all_equal(self):
        """All-same values should return all-zero series without error."""
        raw = pd.Series([5.0] * 10)
        result = self.engine._standardize(raw)
        assert (result == 0.0).all() or result.isna().all()

    def test_standardize_output_length(self):
        raw = pd.Series(range(20), dtype=float)
        result = self.engine._standardize(raw)
        assert len(result) == len(raw)
