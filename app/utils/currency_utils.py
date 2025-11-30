def format_currency(amount: float, currency: str = "USD") -> str:
    if currency == "USD":
        return f"${amount:,.2f}"
    elif currency == "EUR":
        return f"€{amount:,.2f}"
    else:
        return f"{amount:,.2f} {currency}"

def convert_currency(amount: float, from_currency: str, to_currency: str) -> float:
    rates = {"USD": 1.0, "EUR": 0.85, "GBP": 0.73}
    
    if from_currency == to_currency:
        return amount
    
    usd_amount = amount / rates.get(from_currency, 1.0)
    return usd_amount * rates.get(to_currency, 1.0)