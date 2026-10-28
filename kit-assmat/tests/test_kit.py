"""Checks the workbook against the worked examples of the official DREETS / Pajemploi guides.
Run: python3 tests/test_kit.py   (needs LibreOffice)"""
import datetime as dt
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))
import build_kit as K  # noqa: E402
from recalc import errors, recalc  # noqa: E402

D = dt.date
T = dt.time
FAILS = []


def run(name, ov):
    path = os.path.join(tempfile.mkdtemp(), f"{name}.xlsx")
    K.build(path, overrides=ov)
    wb = recalc(path)
    errs = errors(wb)
    if errs:
        FAILS.append(f"{name}: formula errors {errs[:5]}")
    return wb


def eq(name, got, want, tol=0.005):
    ok = (abs(got - want) <= tol) if isinstance(want, (int, float)) and isinstance(got, (int, float)) else got == want
    print(f"  {'OK ' if ok else 'BAD'} {name}: {got!r} (attendu {want!r})")
    if not ok:
        FAILS.append(f"{name}: {got!r} != {want!r}")


def contract(start, typ, hours_by_day, rate, rate_kind="brut", weeks=None, extra=None):
    ov = {("Contrat", "C11"): start, ("Contrat", "C12"): K.TYPES[typ], ("Contrat", "C30"): rate,
          ("Contrat", "D30"): rate_kind}
    if weeks:
        ov[("Contrat", "C13")] = weeks
    for i, h in enumerate(hours_by_day):
        if h:
            ov[("Contrat", f"F{19 + i}")] = h
    ov.update(extra or {})
    return ov


def day(month, d):  # row of a day in a month sheet
    return K.R0 + d - 1


# 1. DREETS fiche 07 — 52 semaines, 40 h, 4,50 € ; absence sans solde ; entretien ; CP 1re période
print("1. Accueil 52 semaines (DREETS fiche 07)")
ov = contract(D(2026, 1, 1), 0, [8, 8, 8, 8, 8], 4.5, extra={
    ("Contrat", "B49"): K.PERIOD_TYPES[3], ("Contrat", "C49"): D(2027, 2, 8), ("Contrat", "D49"): D(2027, 2, 13),
    ("Contrat", "C37"): 3.92,
    ("Juin 2026", f"E{day(6, 2)}"): T(7, 0), ("Juin 2026", f"F{day(6, 2)}"): T(18, 0),
    ("Congés payés", "C10"): 3714.29})
wb = run("t1", ov)
eq("salaire mensualisé", wb["Contrat"]["L10"].value, 780.00)
eq("heures mensualisées", wb["Contrat"]["L8"].value, 173.33)
eq("retenue février (40 h / 160 h)", wb["Février 2027"]["AB9"].value, 195.00)
eq("entretien 11 h à 3,92 €", wb["Juin 2026"][f"M{day(6, 2)}"].value, 4.79)
eq("2 h en plus le 02/06", wb["Juin 2026"]["E8"].value, 3.0)
eq("14 juillet = férié chômé payé", wb["Juillet 2026"][f"I{day(7, 14)}"].value, K.FCP)
eq("pas de retenue en juillet", wb["Juillet 2026"]["F7"].value, 0)
eq("CP acquis (5 mois → 13 j)", wb["Congés payés"]["C8"].value, 13)
eq("CP maintien 13/26 × 780", wb["Congés payés"]["C12"].value, 390.00)
eq("CP dixième", wb["Congés payés"]["C13"].value, 371.43)
eq("CP dû", wb["Congés payés"]["C14"].value, 390.00)

# 2. DREETS fiche 08 — 46 semaines, 36 sem., 40 h, 4,50 € ; CP au fur et à mesure (675 €)
print("2. Accueil 46 semaines ou moins (DREETS fiche 08)")
ov = contract(D(2025, 1, 1), 1, [8, 8, 8, 8, 8], 4.5, weeks=36, extra={
    ("Contrat", "C44"): K.CP_MODES[2],
    ("Contrat", "B49"): K.PERIOD_TYPES[0], ("Contrat", "C49"): D(2026, 9, 7), ("Contrat", "D49"): D(2026, 9, 26),
    ("Contrat", "B50"): K.PERIOD_TYPES[0], ("Contrat", "C50"): D(2026, 12, 7), ("Contrat", "D50"): D(2026, 12, 12),
    ("Congés payés", "C7"): 30, ("Congés payés", "C10"): 6750})
wb = run("t2", ov)
eq("salaire mensualisé", wb["Contrat"]["L10"].value, 540.00)
eq("CP dû (dixième)", wb["Congés payés"]["C14"].value, 675.00)
eq("CP maintien 30/26 × 540", wb["Congés payés"]["C12"].value, 623.08)
eq("septembre : 3 semaines = 18 j", wb["Septembre 2026"]["K8"].value, 18)
eq("septembre : 18/30 × 675", wb["Septembre 2026"]["F11"].value, 405.00)
eq("septembre : pas de retenue", wb["Septembre 2026"]["F7"].value, 0)
eq("décembre : 6/30 × 675", wb["Décembre 2026"]["F11"].value, 135.00)
eq("décembre : salaire brut 540 + 135", wb["Décembre 2026"]["F15"].value, 675.00)

# 3. Pajemploi guide — 40 h sur 4 j, 37 semaines, 3 € net ; semaine de 50 h (5 compl. + 5 major. à 3,50 €)
print("3. Exemple du guide Pajemploi")
ov = contract(D(2026, 1, 5), 1, [10, 10, 0, 10, 10], 3.0, "net", weeks=37, extra={
    ("Contrat", "C34"): 0.5 / 3})
for d_ in (7, 8, 10, 11):
    ov[("Septembre 2026", f"E{day(9, d_)}")] = T(7, 0)
    ov[("Septembre 2026", f"F{day(9, d_)}")] = T(19, 30)
wb = run("t3", ov)
eq("net mensualisé", wb["Contrat"]["L11"].value, 370.00)
eq("jours d'activité", wb["Contrat"]["L15"].value, 13)
eq("heures complémentaires", wb["Septembre 2026"]["K9"].value, 5.0)
eq("heures majorées", wb["Septembre 2026"]["K10"].value, 5.0)
eq("salaire net total", wb["Septembre 2026"]["K11"].value, 402.50, tol=0.011)

# 4. DREETS fiche 11-III — fin de contrat, 52 semaines, 45 h, 4 €
print("4. Fin de contrat 52 semaines (DREETS fiche 11)")
ov = contract(D(2025, 9, 1), 0, [9, 9, 9, 9, 9], 4.0, extra={
    ("Contrat", "B49"): K.PERIOD_TYPES[0], ("Contrat", "C49"): D(2026, 6, 8), ("Contrat", "D49"): D(2026, 6, 27),
    ("Congés payés", "C10"): 7020,
    ("Fin de contrat", "C6"): K.M_RET, ("Fin de contrat", "C7"): D(2026, 7, 31),
    ("Fin de contrat", "C8"): D(2026, 8, 31), ("Fin de contrat", "C35"): 7020})
wb = run("t4", ov)
f = wb["Fin de contrat"]
eq("CP acquis au 31/05 (9 mois)", wb["Congés payés"]["C8"].value, 23)
eq("CP dû au 31/05 (dixième 702)", wb["Congés payés"]["C14"].value, 702.00)
eq("pas de retenue en juin (congés)", wb["Juin 2026"]["F7"].value, 0)
eq("préavis", f["C12"].value, "15 jours")
eq("CP acquis non pris : 702 − 540", f["C27"].value, 162.00)
eq("CP en cours : 8 jours", f["C28"].value, 8)
eq("CP en cours maintien", f["C29"].value, 240.00)
eq("CP en cours dixième", f["C30"].value, 234.00)
eq("indemnité compensatrice totale", f["C31"].value, 402.00)
eq("droit indemnité de rupture", f["C34"].value, "Oui")
eq("indemnité de rupture (9360/80)", f["C37"].value, 117.00)
eq("fin de contrat reportée sur août", wb["Août 2026"]["F12"].value, 402.00)
eq("septembre hors contrat", wb["Septembre 2026"]["F15"].value, 0)

# 5. DREETS fiche 11-III — fin de contrat, 46 semaines, 32 h, 36 sem., 4 €
print("5. Fin de contrat 46 semaines (DREETS fiche 11)")
ov = contract(D(2025, 9, 1), 1, [8, 8, 8, 8], 4.0, weeks=36, extra={
    ("Contrat", "C44"): K.CP_MODES[2],
    ("Contrat", "B49"): K.PERIOD_TYPES[0], ("Contrat", "C49"): D(2026, 6, 8), ("Contrat", "D49"): D(2026, 6, 27),
    ("Congés payés", "C10"): 3456,
    ("Fin de contrat", "C6"): K.M_RET, ("Fin de contrat", "C7"): D(2026, 7, 31),
    ("Fin de contrat", "C8"): D(2026, 8, 31), ("Fin de contrat", "C21"): 10000})
wb = run("t5", ov)
f = wb["Fin de contrat"]
eq("salaire mensualisé", wb["Contrat"]["L10"].value, 384.00)
eq("CP dû au 31/05", wb["Congés payés"]["C14"].value, 345.60)
eq("CP payés en juin (18/23)", wb["Juin 2026"]["F11"].value, 270.47)
eq("CP acquis non pris", f["C27"].value, 75.13)
eq("CP en cours maintien", f["C29"].value, 118.15)
eq("CP en cours dixième", f["C30"].value, 142.25)
eq("régularisation (écart négatif)", f["C24"].value, 0)

# 6. Régularisation (DREETS fiche 11-IV) — 30 h sur 5 j, 36 sem., 4 € ; juin-juillet + 2 semaines d'août
print("6. Régularisation année incomplète")
ov = contract(D(2026, 6, 1), 1, [6, 6, 6, 6, 6], 4.0, weeks=36, extra={
    ("Contrat", "B49"): K.PERIOD_TYPES[1], ("Contrat", "C49"): D(2026, 8, 17), ("Contrat", "D49"): D(2026, 8, 31),
    ("Fin de contrat", "C6"): K.M_RET, ("Fin de contrat", "C7"): D(2026, 8, 10),
    ("Fin de contrat", "C8"): D(2026, 8, 31)})
wb = run("t6", ov)
f = wb["Fin de contrat"]
eq("heures effectuées (132 + 138 + 60)", f["C18"].value, 330)
eq("heures payées (3 × 90)", f["C19"].value, 270)
eq("régularisation 60 h × 4 €", f["C24"].value, 240.00)
eq("préavis < 3 mois", f["C12"].value, "8 jours")
eq("pas d'indemnité de rupture (< 9 mois)", f["C34"].value, "Non")
eq("CP en cours : dixième sur 1 080 + 240", f["C31"].value, 132.00)

# 7. Début en cours de mois (52 semaines) : 15/06, retenue des jours avant l'embauche
print("7. Embauche en cours de mois")
wb = run("t7", contract(D(2026, 6, 15), 0, [8, 8, 8, 8, 8], 4.5))
eq("retenue juin 780 × 80/176", wb["Juin 2026"]["AB9"].value, 354.55)
eq("salaire de juin", wb["Juin 2026"]["F15"].value, 425.45)

print()
if FAILS:
    print(f"{len(FAILS)} échec(s) :")
    for x in FAILS:
        print(" -", x)
    sys.exit(1)
print("Tous les contrôles passent.")
