"""Portfolio optimization routes."""

from fastapi import APIRouter, HTTPException
from loguru import logger

from backend.quant.models import OptimizationRequest, OptimizationResponse

router = APIRouter()


@router.post("/optimize", response_model=OptimizationResponse)
async def optimize_portfolio(request: OptimizationRequest) -> OptimizationResponse:
    """
    Optimize portfolio weights using PyPortfolioOpt.

    Supported methods: max_sharpe, min_volatility, risk_parity, equal_weight.
    """
    try:
        from backend.quant.optimizer import PortfolioOptimizer

        optimizer = PortfolioOptimizer()
        result = optimizer.optimize(
            tickers=request.tickers,
            method=request.method,
            start=request.start,
            end=request.end,
            constraints=request.constraints,
        )
        return OptimizationResponse(
            method=request.method,
            weights=result["weights"],
            expected_return=result.get("expected_return"),
            expected_volatility=result.get("expected_volatility"),
            sharpe_ratio=result.get("sharpe_ratio"),
        )
    except Exception as exc:
        logger.error(f"Portfolio optimization failed: {exc}")
        raise HTTPException(status_code=500, detail=str(exc)) from exc
