class RSIStrategy:
    def __init__(self, lower=30, upper=70):
        self.lower = lower
        self.upper = upper

    def generate_signal(self, rsi_value):
        if rsi_value is None:
            return "hold"
        if rsi_value < self.lower:
            return "buy"
        elif rsi_value > self.upper:
            return "sell"
        else:
            return "hold"
