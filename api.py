from __future__ import annotations

from decimal import Decimal, DivisionByZero, InvalidOperation, getcontext
from typing import Literal

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field


getcontext().prec = 28

Operation = Literal["add", "subtract", "multiply", "divide", "percent"]


class CalculationRequest(BaseModel):
    left: Decimal = Field(..., description="Left operand")
    right: Decimal = Field(..., description="Right operand")
    operation: Operation


class CalculationResponse(BaseModel):
    result: str


app = FastAPI(title="Real Calculator API", version="1.0.0")


def format_decimal(value: Decimal) -> str:
    if value == value.to_integral_value():
        return str(value.quantize(Decimal("1")))

    normalized = value.normalize()
    text = format(normalized, "f")
    return text.rstrip("0").rstrip(".")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/calculate", response_model=CalculationResponse)
def calculate(payload: CalculationRequest) -> CalculationResponse:
    try:
        if payload.operation == "add":
            result = payload.left + payload.right
        elif payload.operation == "subtract":
            result = payload.left - payload.right
        elif payload.operation == "multiply":
            result = payload.left * payload.right
        elif payload.operation == "divide":
            if payload.right == 0:
                raise HTTPException(status_code=400, detail="Cannot divide by zero")
            result = payload.left / payload.right
        elif payload.operation == "percent":
            result = payload.left * payload.right / Decimal("100")
        else:
            raise HTTPException(status_code=400, detail="Unsupported operation")
    except (InvalidOperation, DivisionByZero) as exc:
        raise HTTPException(status_code=400, detail="Invalid calculation") from exc

    return CalculationResponse(result=format_decimal(result))
