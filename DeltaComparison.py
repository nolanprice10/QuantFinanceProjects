"""
three_deltas.py  --  one option, three deltas.

WHAT IT DOES
  For ONE option (one expiration, one strike) it prints three deltas:
    1. "own-vol delta"   : Black-Scholes delta using that option's OWN implied volatility
    2. "flat-vol delta"  : Black-Scholes delta using ONE at-the-money volatility for every strike
    3. "skew-adjusted"   : own-vol delta plus a correction for how volatility changes with strike
                           (assumes the smile moves with the stock: "sticky moneyness")

HOW TO USE (4 steps)
  1. Edit ONLY the block marked "EDIT THIS BLOCK" below, using YOUR real data.
  2. Run:  python3 three_deltas.py
  3. Write down the three numbers it prints.
  4. Put the output next to your data so you can check every number.

SIMPLIFICATIONS (say these out loud if asked)
  - No dividends.
  - European-style Black-Scholes formulas.
  - The slope of volatility vs. strike is estimated from the neighboring strikes in YOUR table.

NO DEPENDENCIES: standard library only.
"""

import math

# ======================= EDIT THIS BLOCK =======================
# WARNING: the numbers below are PLACEHOLDERS so the script runs.
#          Never use output produced from placeholder numbers anywhere.
SPOT = 100.0            # stock price on the day you pick
RATE = 0.04             # risk-free rate as a decimal (0.04 = 4%)
DAYS_TO_EXPIRY = 30     # calendar days until this expiration
OPTION_TYPE = "call"    # "call" or "put"
STRIKE_OF_INTEREST = 95.0   # the ONE strike you want three deltas for

# (strike, implied volatility as a decimal), ONE expiration only, at least 3 rows
SMILE = [
    (90.0, 0.30),
    (95.0, 0.27),
    (100.0, 0.25),
    (105.0, 0.24),
    (110.0, 0.235),
]
# ===============================================================


def norm_cdf(x):
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def norm_pdf(x):
    return math.exp(-0.5 * x * x) / math.sqrt(2.0 * math.pi)


def d1(spot, strike, rate, vol, t):
    return (math.log(spot / strike) + (rate + 0.5 * vol * vol) * t) / (vol * math.sqrt(t))


def bs_delta(spot, strike, rate, vol, t, kind):
    nd1 = norm_cdf(d1(spot, strike, rate, vol, t))
    return nd1 if kind == "call" else nd1 - 1.0


def bs_vega(spot, strike, rate, vol, t):
    # per 1.00 (i.e. 100 vol points) change in volatility
    return spot * norm_pdf(d1(spot, strike, rate, vol, t)) * math.sqrt(t)


def slope_dvol_dstrike(smile, strike):
    """Finite-difference slope of implied vol vs strike at `strike`."""
    smile = sorted(smile)
    strikes = [k for k, _ in smile]
    vols = [v for _, v in smile]
    i = strikes.index(strike)
    if i == 0:
        return (vols[1] - vols[0]) / (strikes[1] - strikes[0])
    if i == len(strikes) - 1:
        return (vols[-1] - vols[-2]) / (strikes[-1] - strikes[-2])
    return (vols[i + 1] - vols[i - 1]) / (strikes[i + 1] - strikes[i - 1])


def main():
    if OPTION_TYPE not in ("call", "put"):
        raise SystemExit('OPTION_TYPE must be "call" or "put"')
    if len(SMILE) < 3:
        raise SystemExit("SMILE needs at least 3 (strike, vol) rows")
    strikes = [k for k, _ in SMILE]
    if STRIKE_OF_INTEREST not in strikes:
        raise SystemExit("STRIKE_OF_INTEREST must be one of the strikes in SMILE")

    t = DAYS_TO_EXPIRY / 365.0
    own_vol = dict(SMILE)[STRIKE_OF_INTEREST]
    atm_strike = min(strikes, key=lambda k: abs(k - SPOT))
    atm_vol = dict(SMILE)[atm_strike]

    # 1. own-vol delta
    delta_own = bs_delta(SPOT, STRIKE_OF_INTEREST, RATE, own_vol, t, OPTION_TYPE)
    # 2. flat-vol delta (one ATM vol for every strike)
    delta_flat = bs_delta(SPOT, STRIKE_OF_INTEREST, RATE, atm_vol, t, OPTION_TYPE)
    # 3. skew-adjusted delta (sticky moneyness): d(vol)/d(spot) = -(K/S) * d(vol)/dK
    dvol_dk = slope_dvol_dstrike(SMILE, STRIKE_OF_INTEREST)
    dvol_dspot = -(STRIKE_OF_INTEREST / SPOT) * dvol_dk
    vega = bs_vega(SPOT, STRIKE_OF_INTEREST, RATE, own_vol, t)
    delta_skew = delta_own + vega * dvol_dspot

    print("INPUTS")
    print(f"  spot={SPOT}  rate={RATE}  days={DAYS_TO_EXPIRY}  type={OPTION_TYPE}  strike={STRIKE_OF_INTEREST}")
    print(f"  own implied vol   = {own_vol:.4f}")
    print(f"  ATM strike / vol  = {atm_strike} / {atm_vol:.4f}")
    print(f"  slope d(vol)/dK   = {dvol_dk:.6f}   (per $1 of strike)")
    print(f"  vega              = {vega:.4f}")
    print()
    print("THREE DELTAS FOR THE SAME OPTION")
    print(f"  1. own-vol delta (Black-Scholes, this option's own vol) : {delta_own:.4f}")
    print(f"  2. flat-vol delta (one ATM vol for every strike)        : {delta_flat:.4f}")
    print(f"  3. skew-adjusted delta (adds the smile-slope correction): {delta_skew:.4f}")


if __name__ == "__main__":
    main()
