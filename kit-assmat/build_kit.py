#!/usr/bin/env python3
"""Builds « Kit Parent Employeur Assmat 2026-2027 » (xlsx for Excel, Google Sheets, LibreOffice).

Rules: CCN IDCC 3239 (socle assistant maternel), DREETS BFC guide (juin 2026), DREETS PdL fiche (12/06/2026),
Pajemploi bulletin n°6 and primo-déclarant guide. See SOURCES.md.

    python3 build_kit.py                 -> dist/Kit-Assmat-2026-2027.xlsx (blank)
    python3 build_kit.py --example       -> dist/Kit-Assmat-2026-2027-EXEMPLE.xlsx (filled example)
"""
import datetime as dt
import os
import sys

from openpyxl import Workbook
from openpyxl.chart import BarChart, Reference
from openpyxl.formatting.rule import FormulaRule
from openpyxl.styles import Alignment, Border, Font, PatternFill, Protection, Side
from openpyxl.workbook.defined_name import DefinedName
from openpyxl.worksheet.datavalidation import DataValidation

BRAND = "Nid Serein"
EDITION = "Édition 2026-2027"
PERIOD_START = dt.date(2026, 6, 1)
MONTH_FR = ["Janvier", "Février", "Mars", "Avril", "Mai", "Juin", "Juillet", "Août",
            "Septembre", "Octobre", "Novembre", "Décembre"]
MONTHS = [(2026, m) for m in range(6, 13)] + [(2027, m) for m in range(1, 6)]
MNAMES = [f"{MONTH_FR[m - 1]} {y}" for y, m in MONTHS]

# Day statuses (dropdown + formulas must use the exact same strings)
ACC, ABSP, MAL, AAS = "Accueil", "Absence enfant – payée", "Maladie enfant – retenue", "Absence assmat – non payée"
CP, CSS, FCP, FT = "Congé payé assmat", "Congé sans solde assmat", "Férié chômé payé", "Férié travaillé (+10 %)"
MAI, SNP, HC, REP = "1er mai travaillé", "Semaine non programmée", "Hors contrat", "Repos"
STATUSES = [ACC, ABSP, MAL, AAS, CP, CSS, FCP, FT, MAI, SNP]
PERIOD_TYPES = ["Congés payés de l'assmat", "Semaine(s) non programmée(s)", "Absence de l'enfant – payée",
                "Congé sans solde de l'assmat"]
TYPES = ["52 semaines (année complète)", "46 semaines ou moins (année incomplète)"]
CP_MODES = ["En une fois au mois de juin", "Lors de la prise principale des congés",
            "Au fur et à mesure de la prise des congés"]
REPAS = ["Les parents", "L'assistante maternelle"]
M_RET, M_DEM, M_AGR = "Retrait de l'enfant (décision des parents)", "Démission de l'assistante maternelle", \
    "Suspension ou retrait d'agrément"
M_FG, M_DEC, M_RTR = "Faute grave", "Décès de l'enfant", "Départ volontaire à la retraite"
MOTIFS = [M_RET, M_DEM, M_AGR, M_FG, M_DEC, M_RTR]
FERIES = [(dt.date(2026, 7, 14), "Fête nationale", ""), (dt.date(2026, 8, 15), "Assomption", ""),
          (dt.date(2026, 11, 1), "Toussaint", ""), (dt.date(2026, 11, 11), "Armistice 1918", ""),
          (dt.date(2026, 12, 25), "Noël", ""), (dt.date(2026, 12, 26), "Saint-Étienne", "Alsace-Moselle"),
          (dt.date(2027, 1, 1), "Jour de l'an", ""), (dt.date(2027, 3, 26), "Vendredi saint", "Alsace-Moselle"),
          (dt.date(2027, 3, 29), "Lundi de Pâques", ""), (dt.date(2027, 5, 1), "Fête du Travail", ""),
          (dt.date(2027, 5, 6), "Ascension", ""), (dt.date(2027, 5, 8), "Victoire 1945", ""),
          (dt.date(2027, 5, 17), "Lundi de Pentecôte", "")]

# ---------- style ----------
C = dict(ink="1F2A2B", teal="1F4D4A", teal2="2F6B66", sage="DCEAE4", sage2="F1F7F4", cream="FBF7F1",
         terra="C8643F", apricot="F7DCCB", butter="FFF6DE", butterb="E2BE6A", grey="6E7C7B", line="D3DEDA",
         white="FFFFFF", blue="DDEBF8", lav="ECE6F7", rose="FBE0D4", mint="E2F1E8", stone="EFEFEC",
         gold="B7862C")
FONT = "Calibri"
EUR = '#,##0.00 "€";-#,##0.00 "€";"–"'
EUR0 = '#,##0.00 "€"'
HRS = '0.00 "h";-0.00 "h";"–"'
NUM = '0;-0;"–"'
DATE = "dd/mm/yyyy"


def F(size=11, bold=False, color="ink", italic=False):
    return Font(name=FONT, size=size, bold=bold, italic=italic, color=C.get(color, color))


def fill(c):
    return PatternFill("solid", fgColor=C.get(c, c))


def side(c="line", style="thin"):
    return Side(style=style, color=C.get(c, c))


BOX = Border(left=side(), right=side(), top=side(), bottom=side())
INBOX = Border(left=side("butterb"), right=side("butterb"), top=side("butterb"), bottom=side("butterb"))
UNDER = Border(bottom=side())
LEFT = Alignment(horizontal="left", vertical="center", wrap_text=True)
CENTER = Alignment(horizontal="center", vertical="center", wrap_text=True)
RIGHT = Alignment(horizontal="right", vertical="center")


def q(s):
    """Excel string literal."""
    return '"' + s.replace('"', '""') + '"'


def put(ws, ref, value=None, font=None, fill_=None, fmt=None, align=None, border=None, merge=None):
    c = ws[ref]
    if value is not None:
        c.value = value
    c.font = font or F()
    if fill_:
        c.fill = fill(fill_)
    if fmt:
        c.number_format = fmt
    c.alignment = align or LEFT
    if border:
        c.border = border
    if merge:
        ws.merge_cells(f"{ref}:{merge}")
        if fill_ or border:
            for row in ws[f"{ref}:{merge}"]:
                for cell in row:
                    if fill_:
                        cell.fill = fill(fill_)
                    if border:
                        cell.border = border
    return c


def inp(ws, ref, value=None, fmt=None, align=None, merge=None):
    """Yellow input cell, unlocked."""
    c = put(ws, ref, value, F(11, color="ink"), "butter", fmt, align or LEFT, INBOX, merge)
    cells = [c] if not merge else [x for row in ws[f"{ref}:{merge}"] for x in row]
    for x in cells:
        x.protection = Protection(locked=False)
    return c


def label(ws, ref, text, merge=None, size=11, color="ink", bold=False):
    return put(ws, ref, text, F(size, bold, color), align=LEFT, merge=merge)


def name(wb, n, ref):
    wb.defined_names[n] = DefinedName(n, attr_text=ref)


def sheet(wb, title, widths, tab=None):
    ws = wb.create_sheet(title)
    ws.sheet_view.showGridLines = False
    ws.sheet_view.zoomScale = 100
    for col, w in widths.items():
        ws.column_dimensions[col].width = w
    if tab:
        ws.sheet_properties.tabColor = C[tab]
    ws.page_setup.orientation = "landscape"
    ws.page_setup.paperSize = ws.PAPERSIZE_A4
    ws.page_setup.fitToWidth = 1
    ws.page_setup.fitToHeight = 0
    ws.sheet_properties.pageSetUpPr.fitToPage = True
    ws.print_options.horizontalCentered = True
    ws.page_margins.left = ws.page_margins.right = 0.4
    ws.page_margins.top = ws.page_margins.bottom = 0.5
    return ws


def header(ws, title, subtitle, last_col="N"):
    ws.row_dimensions[1].height = 10
    ws.row_dimensions[2].height = 34
    put(ws, "B2", title, F(22, True, "teal"), align=Alignment(vertical="bottom"))
    put(ws, f"{last_col}2", f"{BRAND} · {EDITION}", F(9, False, "grey"),
        align=Alignment(horizontal="right", vertical="bottom"))
    put(ws, "B3", subtitle, F(11, False, "grey"), align=Alignment(vertical="top"))
    ws.row_dimensions[3].height = 20


def section(ws, ref, text, merge):
    put(ws, ref, text.upper(), F(10, True, "white"), "teal", align=Alignment(vertical="center", indent=1),
        merge=merge)
    ws.row_dimensions[ws[ref].row].height = 22


def calc(ws, ref, formula, fmt=None, bold=False, size=11, color="ink", fill_=None, align=None, merge=None):
    return put(ws, ref, formula, F(size, bold, color), fill_, fmt, align or RIGHT, None, merge)


def protect(ws):
    ws.protection.sheet = True
    ws.protection.formatColumns = False
    ws.protection.formatRows = False
    ws.protection.selectLockedCells = False
    ws.protection.selectUnlockedCells = False


def dv_list(ws, src, cells):
    dv = DataValidation(type="list", formula1=src, allow_blank=True, showErrorMessage=True,
                        errorTitle="Valeur non reconnue", error="Choisissez une valeur dans la liste.")
    ws.add_data_validation(dv)
    dv.add(cells)


# ---------- sheets ----------
def build_baremes(wb):
    ws = sheet(wb, "Barèmes", {"A": 2, "B": 50, "C": 2, "D": 14, "E": 70, "F": 13, "G": 2,
                               "H": 30, "I": 30, "J": 40, "K": 30, "L": 12, "M": 12, "N": 40, "O": 40},
               tab="grey")
    header(ws, "Barèmes et références", "Valeurs en vigueur au 1er juin 2026. Si un texte change, mettez à jour "
                                        "les cellules jaunes : tout le classeur suit.", last_col="E")
    section(ws, "B5", "Paramètre", "B5")
    section(ws, "D5", "Valeur", "D5")
    section(ws, "E5", "Source", "E5")
    rows = [
        ("SMIC horaire brut", 12.31, EUR0, "Arrêté du 22 mai 2026 — SMIC au 1er juin 2026", "Smic"),
        ("Minimum garanti (MG)", 4.35, EUR0, "Au 1er juin 2026 (fiche DREETS Pays de la Loire du 12/06/2026)", "MG"),
        ("Salaire horaire minimum légal (0,281 × SMIC)", "=ROUND(0.281*D6,2)", EUR0,
         "Art. D.423-9 du code de l'action sociale et des familles", "MinLegal"),
        ("Salaire horaire minimum conventionnel (brut)", 4.20, EUR0,
         "Avenant n°10 du 5 février 2026 à l'annexe 5 de la CCN, étendu par arrêté du 4 mai 2026", "MinConv"),
        ("Minimum conventionnel, titre « AM – garde d'enfants »", 4.37, EUR0, "Même avenant (+4 %)", "MinConvTitre"),
        ("Indemnité d'entretien minimale pour 9 h d'accueil", "=ROUND(0.9*D7+0.0000001,2)", EUR0,
         "Art. 114-1 CCN : 90 % du minimum garanti", "Ent9Min"),
        ("Plancher d'indemnité d'entretien par journée", 2.65, EUR0, "Art. 114-1 CCN, quelle que soit la durée",
         "PlancherEnt"),
        ("Seuil des heures majorées (heures par semaine)", 45, "0", "Art. 110 CCN", "SeuilMaj"),
        ("Majoration minimale des heures au-delà de 45 h", 0.10, "0%", "Art. 110 CCN (au moins 10 %)", "MajSupMin"),
        ("Majoration d'un jour férié travaillé", 0.10, "0%", "Art. 47-2 CCN", "MajFerie"),
        ("Cotisations salariales (taux indicatif)", 0.2188, "0.00%",
         "Déduit des minima officiels : 4,20 € brut = 3,28 € net. Pajemploi calcule le net exact.", "TxCotis"),
        ("Cotisations salariales Alsace-Moselle (indicatif)", 0.2318, "0.00%",
         "4,20 € brut = 3,23 € net en Alsace-Moselle", "TxCotisAM"),
        ("Coefficient brut → net appliqué", "=1-IF(AlsaceMoselle=\"Oui\",D17,D16)", "0.0000",
         "Calculé selon votre réponse « Alsace-Moselle » dans l'onglet Contrat", "CoefNet"),
        ("Jours ouvrables de congés acquis par mois", 2.5, "0.0", "Art. L.3141-3 C. trav. et 48-1-1-1 CCN",
         "JoursCPMois"),
        ("Plafond annuel de congés payés (jours ouvrables)", 30, "0", "5 semaines", "PlafondCP"),
    ]
    for i, (lab, val, fmt, src, nm) in enumerate(rows):
        r = 6 + i
        label(ws, f"B{r}", lab)
        is_formula = isinstance(val, str)
        if is_formula:
            calc(ws, f"D{r}", val, fmt)
        else:
            inp(ws, f"D{r}", val, fmt, RIGHT)
        put(ws, f"E{r}", src, F(9, color="grey"))
        for col in "BDE":
            ws[f"{col}{r}"].border = UNDER
        name(wb, nm, f"'Barèmes'!$D${r}")

    section(ws, "B22", "Jours fériés de la période", "B22")
    section(ws, "D22", "Date", "D22")
    section(ws, "E22", "Zone", "E22")
    section(ws, "F22", "Pris en compte", "F22")
    for i, (d, lab, zone) in enumerate(FERIES):
        r = 23 + i
        label(ws, f"B{r}", lab)
        inp(ws, f"D{r}", d, DATE, CENTER)
        put(ws, f"E{r}", zone or "Toute la France", F(10, color="grey"))
        calc(ws, f"F{r}", f'=IF(AND(E{r}="Alsace-Moselle",AlsaceMoselle<>"Oui"),"",D{r})', DATE, align=CENTER)
    name(wb, "FeriesEff", f"'Barèmes'!$F$23:$F${22 + len(FERIES)}")

    # dropdown lists (hidden zone)
    lists = {"H": ("Statuts du jour", STATUSES), "I": ("Périodes", PERIOD_TYPES), "J": ("Paiement CP", CP_MODES),
             "K": ("Mois", MNAMES), "L": ("Oui/Non", ["Non", "Oui"]), "M": ("Taux", ["brut", "net"]),
             "N": ("Type d'accueil", TYPES), "O": ("Motifs", MOTIFS), "P": ("Repas", REPAS)}
    put(ws, "H39", "Listes utilisées par les menus déroulants — ne pas modifier", F(9, True, "grey"))
    refs = {}
    for col, (title, values) in lists.items():
        put(ws, f"{col}40", title, F(9, True, "grey"))
        for i, v in enumerate(values):
            put(ws, f"{col}{41 + i}", v, F(9, color="grey"))
        refs[title] = f"'Barèmes'!${col}$41:${col}${40 + len(values)}"
    for col in "HIJKLMNOP":
        ws.column_dimensions[col].hidden = True
    protect(ws)
    return refs


def build_contrat(wb, L):
    ws = sheet(wb, "Contrat", {"A": 2, "B": 44, "C": 11, "D": 26, "E": 11, "F": 14, "G": 6, "H": 3,
                               "I": 36, "J": 3, "K": 3, "L": 16}, tab="terra")
    header(ws, "Votre contrat", "À remplir une seule fois. Les cellules jaunes sont à compléter, tout le reste "
                                "se calcule.", last_col="L")
    ws.column_dimensions["G"].hidden = True

    section(ws, "B5", "1 · Les personnes", "F5")
    for r, lab, nm in [(6, "Parent employeur", "ParentNom"), (7, "Assistante maternelle", "AssmatNom"),
                       (8, "Enfant accueilli (1 fichier par enfant)", "EnfantNom")]:
        label(ws, f"B{r}", lab)
        inp(ws, f"C{r}", None, merge=f"F{r}")
        name(wb, nm, f"'Contrat'!$C${r}")

    section(ws, "B10", "2 · Le contrat", "F10")
    label(ws, "B11", "Date de début du contrat (embauche)")
    inp(ws, "C11", None, DATE, CENTER)
    name(wb, "DateDebut", "'Contrat'!$C$11")
    label(ws, "B12", "Type d'accueil")
    inp(ws, "C12", TYPES[0], merge="F12")
    name(wb, "TypeAccueil", "'Contrat'!$C$12")
    calc(ws, "G12", '=IF(LEFT(C12,2)="52",1,2)')
    name(wb, "TypeCode", "'Contrat'!$G$12")
    label(ws, "B13", "Semaines d'accueil programmées sur 12 mois")
    inp(ws, "C13", None, "0", CENTER)
    put(ws, "D13", "année incomplète uniquement (46 max.)", F(9, color="grey"), merge="F13")
    name(wb, "Semaines", "'Contrat'!$C$13")
    label(ws, "B14", "Domicile de l'assmat en Alsace-Moselle ?")
    inp(ws, "C14", "Non", align=CENTER)
    name(wb, "AlsaceMoselle", "'Contrat'!$C$14")
    label(ws, "B15", "Date de fin du contrat")
    calc(ws, "C15", "=IF(DateFin=\"\",\"\",DateFin)", DATE, align=CENTER)
    put(ws, "D15", "se renseigne dans l'onglet « Fin de contrat »", F(9, color="grey"), merge="F15")

    section(ws, "B17", "3 · La semaine type", "F17")
    for col, t in zip("BCDEF", ["Jour", "Arrivée", "Départ", "Heures", "ou heures/jour"]):
        put(ws, f"{col}18", t, F(9, True, "grey"), align=CENTER if col != "B" else LEFT)
    for i, d in enumerate(["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]):
        r = 19 + i
        label(ws, f"B{r}", d)
        inp(ws, f"C{r}", None, "hh:mm", CENTER)
        inp(ws, f"D{r}", None, "hh:mm", CENTER)
        calc(ws, f"E{r}", f'=IF(F{r}<>"",F{r},IF(AND(C{r}<>"",D{r}<>""),ROUND(MOD(D{r}-C{r},1)*24,2),0))', HRS)
        inp(ws, f"F{r}", None, "0.00", CENTER)
    name(wb, "PlanH", "'Contrat'!$E$19:$E$25")
    label(ws, "B26", "Total par semaine", bold=True)
    calc(ws, "E26", "=SUM(E19:E25)", HRS, bold=True)
    name(wb, "HSem", "'Contrat'!$E$26")
    label(ws, "B27", "Jours d'accueil par semaine")
    calc(ws, "E27", '=COUNTIF(E19:E25,">0")', "0")
    name(wb, "JSem", "'Contrat'!$E$27")

    section(ws, "B29", "4 · La rémunération", "F29")
    label(ws, "B30", "Taux horaire convenu au contrat")
    inp(ws, "C30", None, EUR0, RIGHT)
    inp(ws, "D30", "brut", align=CENTER)
    put(ws, "E30", "← brut ou net", F(9, color="grey"), merge="F30")
    label(ws, "B31", "   → taux horaire brut", color="grey")
    calc(ws, "C31", '=IF(C30="",0,IF(D30="net",C30/CoefNet,C30))', '#,##0.000 "€"')
    name(wb, "TauxBrut", "'Contrat'!$C$31")
    label(ws, "B32", "   → taux horaire net (estimé)", color="grey")
    calc(ws, "C32", '=IF(D30="net",C30,C31*CoefNet)', '#,##0.000 "€"')
    name(wb, "TauxNet", "'Contrat'!$C$32")
    label(ws, "B33", "Majoration des heures complémentaires (facultative)")
    inp(ws, "C33", 0, "0%", RIGHT)
    name(wb, "MajCompl", "'Contrat'!$C$33")
    label(ws, "B34", "Majoration des heures au-delà de 45 h (10 % min.)")
    inp(ws, "C34", 0.10, "0%", RIGHT)
    name(wb, "MajSup", "'Contrat'!$C$34")

    section(ws, "B36", "5 · Les indemnités", "F36")
    label(ws, "B37", "Indemnité d'entretien pour une journée de 9 h")
    inp(ws, "C37", "=Ent9Min", EUR0, RIGHT)
    put(ws, "D37", "proratisée selon la durée, 2,65 € min./jour", F(9, color="grey"), merge="F37")
    name(wb, "Entretien9h", "'Contrat'!$C$37")
    label(ws, "B38", "Les repas sont fournis par")
    inp(ws, "C38", REPAS[0], merge="F38")
    name(wb, "FournitRepas", "'Contrat'!$C$38")
    label(ws, "B39", "Prix d'un repas fourni par l'assmat")
    inp(ws, "C39", 0, EUR0, RIGHT)
    name(wb, "PrixRepas", "'Contrat'!$C$39")
    label(ws, "B40", "Repas par jour d'accueil (par défaut)")
    inp(ws, "C40", 1, "0", RIGHT)
    name(wb, "RepasParJour", "'Contrat'!$C$40")
    label(ws, "B41", "Indemnité kilométrique (€ par km)")
    inp(ws, "C41", 0, '#,##0.000 "€"', RIGHT)
    name(wb, "TarifKm", "'Contrat'!$C$41")

    section(ws, "B43", "6 · Congés payés (année incomplète)", "F43")
    label(ws, "B44", "Mode de paiement prévu au contrat")
    inp(ws, "C44", CP_MODES[2], merge="F44")
    name(wb, "ModeCP", "'Contrat'!$C$44")
    calc(ws, "G44", f"=IFERROR(MATCH(C44,{L['Paiement CP']},0),3)")
    name(wb, "ModeCode", "'Contrat'!$G$44")
    label(ws, "B45", "Mois de la prise principale (si ce mode est choisi)")
    inp(ws, "C45", MNAMES[2], merge="D45")
    calc(ws, "G45", f'=IFERROR(EDATE(DATE(2026,6,1),MATCH(C45,{L["Mois"]},0)-1),"")', DATE)
    name(wb, "MoisCPDate", "'Contrat'!$G$45")

    section(ws, "B47", "7 · Périodes sans accueil prévues (vacances, congés)", "F47")
    for col, t in zip("BCDE", ["Type de période", "Du", "Au", "Commentaire"]):
        put(ws, f"{col}48", t, F(9, True, "grey"), align=LEFT if col in "BE" else CENTER)
    for r in range(49, 61):
        inp(ws, f"B{r}", None)
        inp(ws, f"C{r}", None, DATE, CENTER)
        inp(ws, f"D{r}", None, DATE, CENTER)
        inp(ws, f"E{r}", None, merge=f"F{r}")
        calc(ws, f"G{r}", f"=IFERROR(MATCH(B{r},{L['Périodes']},0),0)")
    name(wb, "PerDu", "'Contrat'!$C$49:$C$60")
    name(wb, "PerAu", "'Contrat'!$D$49:$D$60")
    name(wb, "PerCode", "'Contrat'!$G$49:$G$60")
    put(ws, "B61", "Les dates « Du » et « Au » sont incluses. Les périodes ne doivent pas se chevaucher. "
                   "Les jours de ces périodes sont préremplis dans les feuilles mensuelles.",
        F(9, italic=True, color="grey"), merge="F61")
    ws.row_dimensions[61].height = 28

    # Summary card
    for r in range(5, 33):
        for col in "IJKL":
            ws[f"{col}{r}"].fill = fill("sage2")
    put(ws, "I5", "VOTRE MENSUALISATION", F(10, True, "white"), "teal2", align=Alignment(vertical="center", indent=1),
        merge="L5")
    card = [
        (6, "Semaines d'accueil retenues", "=IF(TypeCode=1,52,N(Semaines))", "0", "SemRet"),
        (7, "Heures par semaine", "=HSem", HRS, None),
        (8, "Heures mensualisées", "=ROUND(HSem*SemRet/12,2)", HRS, "HeuresMens"),
        (9, "Jours d'activité mensualisés", "=ROUND(JSem*SemRet/12,2)", "0.00", "JoursMens"),
        (10, "Salaire mensualisé brut",
         "=ROUND(TauxBrut*(MIN(HSem,SeuilMaj)+MAX(0,HSem-SeuilMaj)*(1+MajSup))*SemRet/12,2)", EUR0, "SalMensBrut"),
        (11, "Salaire mensualisé net (estimé)", "=ROUND(SalMensBrut*CoefNet,2)", EUR0, "SalMensNet"),
    ]
    for r, lab, f, fmt, nm in card:
        put(ws, f"I{r}", lab, F(11, color="ink"), "sage2", merge=f"K{r}")
        calc(ws, f"L{r}", f, fmt, bold=r in (10, 11), fill_="sage2")
        if nm:
            name(wb, nm, f"'Contrat'!$L${r}")
    ws["L10"].font = F(13, True, "teal")
    put(ws, "I13", "SUR PAJEMPLOI, CHAQUE MOIS", F(9, True, "teal2"), "sage2", merge="L13")
    put(ws, "I14", "Nombre d'heures normales", F(), "sage2", merge="K14")
    calc(ws, "L14", "=ROUND(HeuresMens,0)", "0", True, fill_="sage2")
    put(ws, "I15", "Nombre de jours d'activité", F(), "sage2", merge="K15")
    calc(ws, "L15", "=ROUNDUP(JoursMens,0)", "0", True, fill_="sage2")
    put(ws, "I16", "Valeurs prévues par la mensualisation (hors absences retenues, qui sont "
                   "déduites automatiquement chaque mois).", F(9, italic=True, color="grey"), "sage2", merge="L17")
    ws["I16"].alignment = Alignment(wrap_text=True, vertical="top")
    put(ws, "I19", "CONTRÔLES DE CONFORMITÉ", F(9, True, "teal2"), "sage2", merge="L19")
    checks = [
        '=IF(DateDebut="","• Saisissez la date de début du contrat.","✓ Date de début renseignée")',
        '=IF(HSem=0,"• Complétez la semaine type.",IF(HSem>48,"⚠ Plus de 48 h par semaine : vérifiez la durée '
        'maximale autorisée.","✓ "&FIXED(HSem,2)&" h par semaine sur "&JSem&" jour(s)"))',
        '=IF(TauxBrut=0,"• Saisissez le taux horaire.",IF(TauxBrut<MinConv,"⚠ Taux brut inférieur au minimum '
        'conventionnel ("&FIXED(MinConv,2)&" € brut)","✓ Taux conforme au minimum conventionnel"))',
        '=IF(TypeCode=1,"✓ Accueil 52 semaines : congés payés inclus dans le salaire",IF(OR(N(Semaines)=0,'
        'Semaines>46),"⚠ Année incomplète : indiquez 46 semaines d\'accueil ou moins","✓ Année incomplète sur "&'
        'Semaines&" semaines"))',
        '=IF(Entretien9h<Ent9Min,"⚠ Entretien inférieur au minimum ("&FIXED(Ent9Min,2)&" € pour 9 h)",'
        '"✓ Indemnité d\'entretien conforme")',
        '=IF(MajSup<MajSupMin,"⚠ Majoration au-delà de 45 h : 10 % minimum","✓ Majoration au-delà de 45 h conforme")',
        '=IF(AND(FournitRepas="L\'assistante maternelle",PrixRepas=0),"• Indiquez le prix d\'un repas.",'
        '"✓ Repas : "&LOWER(FournitRepas))',
    ]
    for i, f in enumerate(checks):
        r = 20 + i
        put(ws, f"I{r}", f, F(10, color="ink"), "sage2", merge=f"L{r}")
    ws.conditional_formatting.add("I20:L26", FormulaRule(formula=['LEFT($I20,1)="⚠"'], font=F(10, True, "terra")))
    ws.conditional_formatting.add("I20:L26", FormulaRule(formula=['LEFT($I20,1)="•"'], font=F(10, False, "gold")))

    dv_list(ws, L["Type d'accueil"], "C12")
    dv_list(ws, L["Oui/Non"], "C14")
    dv_list(ws, L["Taux"], "D30")
    dv_list(ws, L["Repas"], "C38")
    dv_list(ws, L["Paiement CP"], "C44")
    dv_list(ws, L["Mois"], "C45")
    dv_list(ws, L["Périodes"], "B49:B60")
    dv = DataValidation(type="whole", operator="between", formula1="1", formula2="52", allow_blank=True,
                        showErrorMessage=True, error="Entre 1 et 52 semaines.")
    ws.add_data_validation(dv)
    dv.add("C13")
    dvd = DataValidation(type="date", operator="between", formula1="DATE(2000,1,1)", formula2="DATE(2040,12,31)",
                         allow_blank=True, showErrorMessage=True, error="Saisissez une date (jj/mm/aaaa).")
    ws.add_data_validation(dvd)
    dvd.add("C11")
    dvd.add("C49:D60")
    ws.freeze_panes = "A4"
    protect(ws)
    return ws


R0, R1 = 18, 48  # day rows in month sheets


def build_month(wb, idx, y, m, L):
    title = MNAMES[idx]
    ws = sheet(wb, title, {"A": 2, "B": 11, "C": 6, "D": 25, "E": 8, "F": 8, "G": 7, "H": 7, "I": 23,
                           "J": 8, "K": 11, "L": 9, "M": 12, "N": 22}, tab="teal")
    header(ws, title, "", last_col="N")
    ws.page_setup.orientation = "portrait"
    ws.page_setup.fitToHeight = 1
    ws["B3"] = (f'="Présence, salaire et déclaration Pajemploi"&IF(EnfantNom<>""," — "&EnfantNom,"")'
                f'&IF(AssmatNom<>""," chez "&AssmatNom,"")')
    ws["AB2"] = dt.date(y, m, 1)
    ws["AB2"].number_format = DATE
    ws["AB3"] = "=DAY(EOMONTH(AB2,0))"

    # --- cards ---
    for r in range(5, 16):
        for col in "BCDEFG":
            ws[f"{col}{r}"].fill = fill("white")
            ws[f"{col}{r}"].border = Border()
        for col in "IJK":
            ws[f"{col}{r}"].fill = fill("sage2")
        for col in "MN":
            ws[f"{col}{r}"].fill = fill("teal")
    put(ws, "B5", "SALAIRE DU MOIS (BRUT)", F(10, True, "teal"), align=Alignment(vertical="center"), merge="G5")
    ws["B5"].border = Border(bottom=side("teal", "medium"))
    lines = [(6, "Salaire mensualisé", None), (7, "Retenue pour absence(s)", None),
             (8, "Heures complémentaires", "=AB17"), (9, "Heures majorées (au-delà de 45 h)", "=AB18"),
             (10, "Jours fériés travaillés", None), (11, "Congés payés versés ce mois-ci", None),
             (12, "Fin de contrat (régularisation, congés)", None), (13, "Autre somme brute (prime, rappel…)", None)]
    for r, lab, hrs in lines:
        put(ws, f"B{r}", lab, F(10), merge=f"D{r}")
        if hrs:
            calc(ws, f"E{r}", hrs, HRS, size=10, color="grey")
        for col in "BCDEFG":
            ws[f"{col}{r}"].border = Border(bottom=side("stone"))
    calc(ws, "F6", "=IF(AB19=1,SalMensBrut,0)", EUR, merge="G6")
    calc(ws, "F7", "=IF(AB19=1,-AB9,0)", EUR, merge="G7")
    calc(ws, "F8", "=ROUND(E8*TauxBrut*(1+MajCompl),2)", EUR, merge="G8")
    calc(ws, "F9", "=ROUND(E9*TauxBrut*(1+MajSup),2)", EUR, merge="G9")
    calc(ws, "F10", f"=ROUND(SUM(AA{R0}:AA{R1})*TauxBrut,2)", EUR, merge="G10")
    calc(ws, "F11", f"='Congés payés'!E{34 + idx}", EUR, merge="G11")
    calc(ws, "F12", "=IF(AB14=1,FinSoumis,0)", EUR, merge="G12")
    inp(ws, "F13", None, EUR, RIGHT, merge="G13")
    put(ws, "B15", "Salaire brut du mois", F(11, True, "teal"), merge="D15")
    calc(ws, "F15", "=SUM(F6:F13)", EUR0, True, 12, "teal", merge="G15")
    for col in "BCDEFG":
        ws[f"{col}15"].border = Border(top=side("teal", "medium"))

    put(ws, "I5", "À DÉCLARER SUR PAJEMPLOI", F(10, True, "white"), "teal2",
        align=Alignment(vertical="center", indent=1), merge="K5")
    pj = [(6, "Nombre d'heures normales", "=IFERROR(IF(F6=0,0,ROUND(HeuresMens+F7/TauxBrut,0)),0)", "0"),
          (7, "Nombre de jours d'activité", "=IF(F6=0,0,ROUNDUP(JoursMens*(F6+F7)/F6,0))", "0"),
          (8, "Jours de congés payés", f"='Congés payés'!F{34 + idx}", NUM),
          (9, "Heures complémentaires", "=E8", HRS), (10, "Heures majorées", "=E9", HRS),
          (11, "Salaire net total", "=ROUND(F15*CoefNet,2)", EUR0),
          (12, "Indemnités d'entretien", f"=SUM(M{R0}:M{R1})", EUR),
          (13, "Indemnités de repas", f"=ROUND(SUM(Y{R0}:Y{R1})*PrixRepas,2)", EUR),
          (14, "Indemnités kilométriques", f"=ROUND(SUM(H{R0}:H{R1})*TarifKm,2)", EUR),
          (15, "Indemnité de rupture", "=IF(AB14=1,IndemRupture,0)", EUR)]
    for r, lab, f, fmt in pj:
        put(ws, f"I{r}", lab, F(10, r == 11), "sage2", merge=f"J{r}")
        calc(ws, f"K{r}", f, fmt, bold=True, size=12 if r == 11 else 11, color="teal" if r == 11 else "ink",
             fill_="sage2")
        for col in "IJK":
            ws[f"{col}{r}"].border = Border(bottom=side("sage"))

    put(ws, "M5", "À VERSER À L'ASSMAT", F(10, True, "white"), "teal", align=Alignment(vertical="center", indent=1),
        merge="N5")
    put(ws, "M6", "Salaire net (estimé)", F(9, color="sage"), "teal", merge="N6")
    calc(ws, "M7", "=K11", EUR0, True, 13, "white", "teal", merge="N7")
    put(ws, "M8", "Indemnités (non imposables)", F(9, color="sage"), "teal", merge="N8")
    calc(ws, "M9", "=SUM(K12:K15)", EUR0, True, 13, "white", "teal", merge="N9")
    put(ws, "M10", "TOTAL DU MOIS", F(9, True, "apricot"), "teal", merge="N10")
    calc(ws, "M11", "=M7+M9", EUR0, True, 20, "white", "teal", merge="N12")
    put(ws, "M13", "Avec Pajemploi+, ce montant (moins votre CMG) est prélevé puis versé à l'assmat "
                   "par Pajemploi.", F(8, italic=True, color="sage"), "teal", merge="N15")
    ws["M13"].alignment = Alignment(wrap_text=True, vertical="top")

    msg_out = "Mois hors contrat (avant le début ou après la fin) : rien à déclarer ce mois-ci."
    msg_over = "⚠ Deux périodes de l'onglet Contrat se chevauchent : corrigez-les."
    msg_mal = ("⚠ Plus de 5 jours de maladie de l'enfant retenus : au-delà de 5 jours par an (absences courtes), "
               "le salaire est dû, sauf absence d'au moins 14 jours consécutifs.")
    put(ws, "B16", f'=IF(AB19=0,{q(msg_out)},IF(AB20>4,{q(msg_over)},IF(AB11>5,{q(msg_mal)},"")))',
        F(10, True, "terra"), merge="N16")
    ws.row_dimensions[16].height = 20

    # --- day table ---
    heads = [("B", "Date"), ("C", "Jour"), ("D", "✎ Statut (si différent)"), ("E", "✎ Arrivée"),
             ("F", "✎ Départ"), ("G", "✎ Repas"), ("H", "✎ Km"), ("I", "Statut retenu"), ("J", "Prévu"),
             ("K", "Réalisé"), ("L", "Retenue"), ("M", "Entretien"), ("N", "✎ Notes")]
    for col, t in heads:
        is_in = t.startswith("✎")
        put(ws, f"{col}17", t, F(9, True, "ink" if is_in else "white"), "apricot" if is_in else "teal", align=CENTER)
    ws.row_dimensions[17].height = 26
    st = lambda s: q(s)
    work = f'OR(I{{r}}={st(ACC)},I{{r}}={st(FT)},I{{r}}={st(MAI)})'
    for r in range(R0, R1 + 1):
        d = r - R0 + 1
        w = work.format(r=r)
        ws[f"B{r}"] = f'=IF({d}<=$AB$3,$AB$2+{d}-1,"")'
        ws[f"C{r}"] = f'=IF(B{r}="","",CHOOSE(WEEKDAY(B{r},2),"lun","mar","mer","jeu","ven","sam","dim"))'
        ws[f"P{r}"] = f'=IF(B{r}="","",B{r}-WEEKDAY(B{r},2)+1)'
        ws[f"Q{r}"] = f'=IF(B{r}="",0,INDEX(PlanH,WEEKDAY(B{r},2)))'
        ws[f"R{r}"] = (f'=IF(B{r}="",0,IF(AND(OR(DateDebut="",B{r}>=DateDebut),OR(DateFin="",B{r}<=DateFin)),1,0))')
        ws[f"S{r}"] = f'=IF(B{r}="",0,SUMPRODUCT((PerDu<=B{r})*(PerAu>=B{r})*PerCode))'
        ws[f"T{r}"] = f'=IF(B{r}="",0,IF(COUNTIF(FeriesEff,B{r})>0,1,0))'
        ws[f"U{r}"] = f'=IF(AND(E{r}<>"",F{r}<>""),1,0)'
        ws[f"I{r}"] = (
            f'=IF(B{r}="","",IF(R{r}=0,{st(HC)},IF(D{r}<>"",D{r},'
            f'IF(U{r}=1,IF(T{r}=1,IF(AND(DAY(B{r})=1,MONTH(B{r})=5),{st(MAI)},{st(FT)}),{st(ACC)}),'
            f'IF(S{r}=1,IF(OR(WEEKDAY(B{r},2)=7,T{r}=1),IF(AND(T{r}=1,Q{r}>0),{st(FCP)},{st(REP)}),{st(CP)}),'
            f'IF(S{r}=4,IF(Q{r}>0,{st(CSS)},{st(REP)}),'
            f'IF(Q{r}=0,{st(REP)},'
            f'IF(S{r}=2,{st(SNP)},'
            f'IF(S{r}=3,{st(ABSP)},'
            f'IF(T{r}=1,{st(FCP)},{st(ACC)}))))))))))')
        ws[f"J{r}"] = f'=IF({w},IF(OR(S{r}=1,S{r}=2),0,Q{r}),0)'
        ws[f"K{r}"] = f'=IF({w},IF(U{r}=1,ROUND(MOD(F{r}-E{r},1)*24,2),J{r}),0)'
        ws[f"L{r}"] = f'=IF(OR(I{r}={st(MAL)},I{r}={st(AAS)},I{r}={st(CSS)},I{r}={st(HC)}),Q{r},0)'
        ws[f"M{r}"] = f'=IF(K{r}>0,ROUND(MAX(PlancherEnt,Entretien9h/9*K{r}),2),0)'
        ws[f"V{r}"] = f'=MAX(0,K{r}-J{r})'
        ws[f"W{r}"] = f'=IF(L{r}>0,1,0)'
        ws[f"X{r}"] = f'=IF(Q{r}>0,1,0)'
        ws[f"Y{r}"] = f'=IF(FournitRepas={st(REPAS[1])},IF(G{r}<>"",G{r},IF(K{r}>0,RepasParJour,0)),0)'
        ws[f"Z{r}"] = f'=IF(I{r}={st(CP)},IF(AND(WEEKDAY(B{r},2)<=6,T{r}=0),1,0),0)'
        ws[f"AA{r}"] = f'=IF(I{r}={st(FT)},K{r}*MajFerie,IF(I{r}={st(MAI)},K{r},0))'
        ws[f"AC{r}"] = (f'=IF(B{r}="",0,IF(B{r}<AnnivRegul,0,IF({w},MIN(K{r},J{r}),'
                        f'IF(OR(I{r}={st(ABSP)},I{r}={st(FCP)}),Q{r},0))))')
        ws[f"AD{r}"] = f'=IF(I{r}={st(MAL)},1,0)'
        for col, fmt, al in [("B", "dd/mm", CENTER), ("C", None, CENTER), ("I", None, LEFT), ("J", HRS, RIGHT),
                             ("K", HRS, RIGHT), ("L", HRS, RIGHT), ("M", EUR, RIGHT)]:
            c = ws[f"{col}{r}"]
            c.font = F(10, col == "K")
            c.alignment = al
            if fmt:
                c.number_format = fmt
            c.border = Border(bottom=side("stone"))
        for col, fmt in [("D", None), ("E", "hh:mm"), ("F", "hh:mm"), ("G", "0"), ("H", "0.0"), ("N", None)]:
            c = inp(ws, f"{col}{r}", None, fmt, CENTER if col not in "DN" else LEFT)
            c.font = F(10)
    calc(ws, f"I{R1 + 1}", "Totaux du mois", bold=True, align=RIGHT)
    for col, f, fmt in [("G", f"=SUM(Y{R0}:Y{R1})", NUM), ("H", f"=SUM(H{R0}:H{R1})", '0.0;-0.0;"–"'),
                        ("J", f"=SUM(J{R0}:J{R1})", HRS), ("K", f"=SUM(K{R0}:K{R1})", HRS),
                        ("L", f"=SUM(L{R0}:L{R1})", HRS), ("M", f"=SUM(M{R0}:M{R1})", EUR)]:
        calc(ws, f"{col}{R1 + 1}", f, fmt, bold=True)
    for col in "BCDEFGHIJKLMN":
        ws[f"{col}{R1 + 1}"].border = Border(top=side("teal", "medium"))

    # status colours (calculated columns only, inputs keep their yellow)
    rng = f"B{R0}:C{R1} I{R0}:M{R1}"
    for s, col in [(CP, "blue"), (ABSP, "mint"), (MAL, "rose"), (AAS, "rose"), (CSS, "rose"), (FCP, "lav"),
                   (FT, "lav"), (MAI, "lav"), (SNP, "stone"), (HC, "stone")]:
        ws.conditional_formatting.add(rng, FormulaRule(formula=[f'$I{R0}={q(s)}'], fill=fill(col)))
    ws.conditional_formatting.add(rng, FormulaRule(formula=[f'$I{R0}={q(REP)}'], font=F(10, color="grey")))
    ws.conditional_formatting.add(f"K{R0}:K{R1}", FormulaRule(formula=[f"$V{R0}>0"], font=F(10, True, "terra")))

    # --- weeks ---
    wr = R1 + 3  # 51
    section(ws, f"B{wr}", "Heures par semaine (calcul des heures complémentaires et majorées)", f"H{wr}")
    for col, t in zip("BCDEFGH", ["Semaine du", "au", "Réalisées", "Au planning", "En plus", "dont compl.",
                                  "dont major."]):
        put(ws, f"{col}{wr + 1}", t, F(9, True, "grey"), align=CENTER)
    for i in range(6):
        r = wr + 2 + i
        if i == 0:
            ws[f"B{r}"] = "=$AB$2-WEEKDAY($AB$2,2)+1"
        else:
            ws[f"B{r}"] = f'=IF(B{r - 1}="","",IF(B{r - 1}+7<=EOMONTH($AB$2,0),B{r - 1}+7,""))'
        ws[f"C{r}"] = f'=IF(B{r}="","",MIN(B{r}+6,EOMONTH($AB$2,0)))'
        ws[f"D{r}"] = f'=IF(B{r}="",0,SUMIFS($K${R0}:$K${R1},$P${R0}:$P${R1},B{r}))'
        ws[f"E{r}"] = f'=IF(B{r}="",0,SUMIFS($J${R0}:$J${R1},$P${R0}:$P${R1},B{r}))'
        ws[f"F{r}"] = f'=IF(B{r}="",0,SUMIFS($V${R0}:$V${R1},$P${R0}:$P${R1},B{r}))'
        ws[f"H{r}"] = f'=IF(B{r}="",0,MIN(F{r},MAX(0,D{r}-SeuilMaj)))'
        ws[f"G{r}"] = f'=IF(B{r}="",0,F{r}-H{r})'
        for col, fmt in [("B", "dd/mm"), ("C", "dd/mm"), ("D", HRS), ("E", HRS), ("F", HRS), ("G", HRS),
                         ("H", HRS)]:
            ws[f"{col}{r}"].number_format = fmt
            ws[f"{col}{r}"].font = F(10)
            ws[f"{col}{r}"].alignment = CENTER
            ws[f"{col}{r}"].border = Border(bottom=side("stone"))
    tr = wr + 8
    for col in "DEFGH":
        calc(ws, f"{col}{tr}", f"=SUM({col}{wr + 2}:{col}{wr + 7})", HRS, bold=True, align=CENTER)
    put(ws, f"I{wr + 1}", "Une heure est « en plus » dès qu'elle dépasse le planning du jour. Jusqu'à 45 h dans la "
                          "semaine, elle est complémentaire (taux normal, sauf majoration prévue au contrat). "
                          "Au-delà de 45 h, elle est majorée (10 % minimum).", F(9, italic=True, color="grey"),
        merge=f"N{wr + 4}")
    ws[f"I{wr + 1}"].alignment = Alignment(wrap_text=True, vertical="top", indent=1)

    # --- signatures ---
    sr = tr + 3
    put(ws, f"B{sr}", "Signature du parent employeur", F(9, color="grey"), merge=f"F{sr}")
    put(ws, f"I{sr}", "Signature de l'assistante maternelle", F(9, color="grey"), merge=f"N{sr}")
    for col in "BCDEF":
        ws[f"{col}{sr + 3}"].border = Border(bottom=side("grey"))
    for col in "IJKLMN":
        ws[f"{col}{sr + 3}"].border = Border(bottom=side("grey"))

    # --- monthly helpers (hidden) ---
    helpers = {
        "AB5": f"=SUM(Q{R0}:Q{R1})", "AB6": f"=SUM(L{R0}:L{R1})", "AB7": f"=SUM(X{R0}:X{R1})",
        "AB8": f"=SUM(W{R0}:W{R1})",
        "AB9": "=ROUND(IF(TypeCode=1,IF(AB5>0,SalMensBrut*AB6/AB5,0),IF(AB7>0,SalMensBrut*AB8/AB7,0)),2)",
        "AB10": f"=SUM(Z{R0}:Z{R1})", "AB11": f"=SUM(AD{R0}:AD{R1})", "AB12": f"=SUM(AC{R0}:AC{R1})",
        "AB13": "=IF(OR(AB19=0,SalMensBrut=0),0,HeuresMens*(F6+F7)/SalMensBrut)",
        "AB14": '=IF(DateFin="",0,IF(AND(DateFin>=AB2,DateFin<=EOMONTH(AB2,0)),1,0))',
        "AB15": "=SUM(F6:F11)+F13", "AB16": f"=SUM(K{R0}:K{R1})", "AB17": f"=G{tr}", "AB18": f"=H{tr}",
        "AB19": f"=MAX(R{R0}:R{R1})", "AB20": f"=MAX(S{R0}:S{R1})",
    }
    for ref, f in helpers.items():
        ws[ref] = f
    for col in ["O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z", "AA", "AB", "AC", "AD"]:
        ws.column_dimensions[col].hidden = True

    dv_list(ws, L["Statuts du jour"], f"D{R0}:D{R1}")
    dvt = DataValidation(type="time", operator="between", formula1="0", formula2="0.999988", allow_blank=True,
                         showErrorMessage=True, error="Saisissez une heure, par exemple 8:30")
    ws.add_data_validation(dvt)
    dvt.add(f"E{R0}:F{R1}")
    ws.freeze_panes = f"A{R0}"
    ws.print_area = f"A1:N{sr + 3}"
    ws.print_title_rows = "17:17"
    protect(ws)
    return ws


def build_cp(wb, L):
    ws = sheet(wb, "Congés payés", {"A": 2, "B": 58, "C": 14, "D": 14, "E": 16, "F": 16, "G": 12, "H": 40},
               tab="teal2")
    header(ws, "Congés payés", "Droits acquis, méthode la plus favorable (maintien de salaire ou dixième) "
                               "et calendrier de paiement.", last_col="H")
    ws.column_dimensions["G"].hidden = True
    section(ws, "B5", "A · Congés acquis du 1er juin 2025 au 31 mai 2026 — à prendre et payer cette année", "F5")
    label(ws, "B7", "Jours ouvrables acquis au 31 mai 2026 (si vous les connaissez)")
    inp(ws, "C7", None, "0", CENTER)
    put(ws, "D7", '="suggestion : "&F7&" j"', F(9, italic=True, color="grey"), merge="E7")
    calc(ws, "F7", '=IF(DateDebut="",30,IF(DateDebut<=DATE(2025,6,1),30,IF(DateDebut>=DATE(2026,6,1),0,'
                   'MIN(30,ROUNDUP(2.5*DATEDIF(DATE(YEAR(DateDebut),MONTH(DateDebut),1),DATE(2026,6,1),"m"),0)))))',
         "0", color="white")
    label(ws, "B8", "   → jours retenus pour le calcul", color="grey")
    calc(ws, "C8", '=IF(C7="",F7,C7)', "0", True, align=CENTER)
    name(wb, "CPA_J", "'Congés payés'!$C$8")
    label(ws, "B9", "Salaire mensualisé brut sur cette période (vide = salaire actuel)")
    inp(ws, "C9", None, EUR0, RIGHT)
    calc(ws, "D9", '=IF(C9="",SalMensBrut,C9)', EUR0, color="grey")
    name(wb, "CPA_Sal", "'Congés payés'!$D$9")
    label(ws, "B10", "Total des salaires bruts du 01/06/2025 au 31/05/2026 (hors indemnités)")
    inp(ws, "C10", None, EUR0, RIGHT)
    calc(ws, "D10", '=IF(C10="",ROUND(CPA_Sal*IF(DateDebut="",12,IF(DateDebut<=DATE(2025,6,1),12,'
                    'IF(DateDebut>=DATE(2026,6,1),0,DATEDIF(DATE(YEAR(DateDebut),MONTH(DateDebut),1),'
                    'DATE(2026,6,1),"m")))),2),C10)', EUR0, color="grey")
    put(ws, "E10", '=IF(C10="","estimation : remplacez-la par le vrai total (bulletins Pajemploi)","")',
        F(9, italic=True, color="terra"), merge="H10")
    for r, lab, f, nm in [(12, "Méthode du maintien de salaire (salaire ÷ 26 × jours)",
                           "=ROUND(CPA_Sal/26*CPA_J,2)", "CPA_Maint"),
                          (13, "Méthode du dixième (10 % des salaires bruts de la période)",
                           "=ROUND(D10*0.1,2)", "CPA_Dix"),
                          (14, "Indemnité de congés payés due (la plus favorable)", "=MAX(C12,C13)", "CPA_Due")]:
        put(ws, f"B{r}", lab, F(11, r == 14), "sage2")
        calc(ws, f"C{r}", f, EUR0, r == 14, 12 if r == 14 else 11, "teal" if r == 14 else "ink", "sage2")
        name(wb, nm, f"'Congés payés'!$C${r}")
    put(ws, "D12", '=IF(C13>C12,"","← retenue")', F(9, True, "teal2"), "sage2")
    put(ws, "D13", '=IF(C13>C12,"← retenue","")', F(9, True, "teal2"), "sage2")
    msg52 = ("Accueil 52 semaines : les congés sont payés par le maintien du salaire mensualisé au moment où ils sont "
             "pris. Si le dixième est plus favorable, le complément est ajouté automatiquement le mois où le dernier "
             "jour de congé acquis est pris.")
    put(ws, "B15", f'=IF(TypeCode=1,{q(msg52)},"Accueil 46 semaines ou moins : l\'indemnité s\'ajoute au salaire '
                   f'mensualisé, selon le mode prévu au contrat : "&LOWER(ModeCP)&".")',
        F(9, italic=True, color="grey"), merge="H16")
    ws["B15"].alignment = Alignment(wrap_text=True, vertical="top")
    ws.row_dimensions[15].height = 18
    ws.row_dimensions[16].height = 18

    section(ws, "B19", "B · Congés en cours d'acquisition (1er juin 2026 – 31 mai 2027)", "F19")
    label(ws, "B20", "Mois sous contrat sur la période (même partiellement)")
    calc(ws, "C20", "=SUM(RecapActive)", "0", align=CENTER)
    label(ws, "B21", "Ajustement (+ jours pour enfant à charge, fractionnement ; − mois non travaillés)")
    inp(ws, "C21", 0, "0", CENTER)
    label(ws, "B22", "Jours ouvrables acquis", bold=True)
    calc(ws, "C22", "=MAX(0,MIN(PlafondCP,ROUNDUP(JoursCPMois*C20,0))+N(C21))", "0", True, align=CENTER)
    name(wb, "CPB_J", "'Congés payés'!$C$22")
    label(ws, "B23", "Salaires bruts de la période (congés payés inclus, hors indemnités)")
    calc(ws, "C23", "=SUM(RecapBrutHF)", EUR0)
    name(wb, "CPB_Brut", "'Congés payés'!$C$23")
    label(ws, "B24", "Maintien de salaire")
    calc(ws, "C24", "=ROUND(SalMensBrut/26*CPB_J,2)", EUR0)
    label(ws, "B25", "Dixième")
    calc(ws, "C25", "=ROUND(CPB_Brut*0.1,2)", EUR0)
    put(ws, "B26", "Indemnité prévisionnelle (la plus favorable)", F(11, True), "sage2")
    calc(ws, "C26", "=MAX(C24,C25)", EUR0, True, 12, "teal", "sage2")
    put(ws, "B27", "Montant définitif au 31 mai 2027 : reportez-le dans la section A de l'édition 2027-2028.",
        F(9, italic=True, color="grey"), merge="H27")

    section(ws, "B31", "C · Calendrier de paiement des congés acquis au 31 mai 2026", "F31")
    for col, t in zip("BCDEF", ["Mois", "Jours de CP pris", "Cumul", "Indemnité versée (brut)",
                                "Jours CP Pajemploi"]):
        put(ws, f"{col}33", t, F(9, True, "grey"), align=CENTER if col != "B" else LEFT)
    for i, mn in enumerate(MNAMES):
        r = 34 + i
        sm = f"'{mn}'"
        label(ws, f"B{r}", mn)
        ws[f"G{r}"] = dt.date(*MONTHS[i], 1)
        ws[f"G{r}"].number_format = DATE
        calc(ws, f"C{r}", f"={sm}!AB10", NUM, align=CENTER)
        calc(ws, f"D{r}", f"=SUM(C$34:C{r})", NUM, align=CENTER)
        calc(ws, f"E{r}",
             f"=IF({sm}!$AB$19=0,0,IF(TypeCode=1,IF(AND(CPA_J>0,D{r}>=CPA_J,D{r}-C{r}<CPA_J),"
             f"ROUND(MAX(0,CPA_Dix-CPA_Maint),2),0),CHOOSE(ModeCode,IF(G{r}=DATE(2026,6,1),CPA_Due,0),"
             f"IF(G{r}=MoisCPDate,CPA_Due,0),IF(CPA_J>0,ROUND(CPA_Due*MIN(D{r},CPA_J)/CPA_J,2)"
             f"-ROUND(CPA_Due*MIN(D{r}-C{r},CPA_J)/CPA_J,2),0))))", EUR)
        calc(ws, f"F{r}",
             f"=IF({sm}!$AB$19=0,0,IF(TypeCode=1,0,CHOOSE(ModeCode,IF(G{r}=DATE(2026,6,1),CPA_J,0),"
             f"IF(G{r}=MoisCPDate,CPA_J,0),MIN(D{r},CPA_J)-MIN(D{r}-C{r},CPA_J))))", NUM, align=CENTER)
        for col in "BCDEF":
            ws[f"{col}{r}"].border = Border(bottom=side("stone"))
    label(ws, "B46", "Total", bold=True)
    for col, fmt in [("C", NUM), ("E", EUR0), ("F", NUM)]:
        calc(ws, f"{col}46", f"=SUM({col}34:{col}45)", fmt, True, align=CENTER if col != "E" else RIGHT)
    name(wb, "CPTaken", "'Congés payés'!$C$46")
    name(wb, "CPPaid", "'Congés payés'!$E$46")
    over = ('=IF(AND(CPA_J>0,CPTaken>CPA_J),"⚠ "&(CPTaken-CPA_J)&" jour(s) de congé au-delà des droits acquis : '
            'notez-les « Congé sans solde assmat »"&IF(TypeCode=1," (ils seront retenus sur le salaire).",'
            '" (ils ne sont pas rémunérés)."),"")')
    put(ws, "B47", over, F(10, True, "terra"), merge="H47")
    put(ws, "B48", "Les jours de congé pris sont comptés automatiquement dans les feuilles mensuelles (jours "
                   "ouvrables, du lundi au samedi, hors jours fériés).", F(9, italic=True, color="grey"), merge="H48")
    ws.page_setup.orientation = "portrait"
    ws.page_setup.fitToHeight = 1
    protect(ws)
    return ws


def build_fin(wb, L):
    ws = sheet(wb, "Fin de contrat", {"A": 2, "B": 62, "C": 18, "D": 3, "E": 60}, tab="terra")
    header(ws, "Fin de contrat", "Préavis, régularisation, congés payés et indemnité de rupture : le solde de "
                                 "tout compte en un coup d'œil.", last_col="E")
    put(ws, "B4", '=IF(AND(DateFin<>"",OR(DateFin<DATE(2026,6,1),DateFin>DATE(2027,5,31))),"⚠ La date de fin '
                  'est en dehors de la période de ce fichier (1er juin 2026 – 31 mai 2027).","")',
        F(10, True, "terra"), merge="E4")
    section(ws, "B5", "La rupture", "E5")
    label(ws, "B6", "Motif")
    inp(ws, "C6", None, merge="E6")
    name(wb, "Motif", "'Fin de contrat'!$C$6")
    label(ws, "B7", "Date d'envoi ou de remise de la lettre")
    inp(ws, "C7", None, DATE, CENTER)
    name(wb, "DateNotif", "'Fin de contrat'!$C$7")
    label(ws, "B8", "Dernier jour du contrat (fin du préavis)")
    inp(ws, "C8", None, DATE, CENTER)
    name(wb, "DateFin", "'Fin de contrat'!$C$8")
    put(ws, "E8", "Laissez vide tant que le contrat continue.", F(9, italic=True, color="grey"))

    section(ws, "B10", "Préavis", "E10")
    label(ws, "B11", "Ancienneté à la date de la lettre (mois)")
    calc(ws, "C11", '=IF(OR(DateNotif="",DateDebut=""),"",DATEDIF(DateDebut,DateNotif,"m"))', "0", align=CENTER)
    label(ws, "B12", "Durée du préavis")
    calc(ws, "C12", f'=IF(OR(C11="",Motif=""),"",IF(OR(Motif={q(M_RET)},Motif={q(M_DEC)}),IF(C11<3,'
                    f'"8 jours",IF(C11<12,"15 jours","1 mois")),IF(Motif={q(M_DEM)},IF(C11<3,"Aucun",IF(C11<12,'
                    f'"15 jours","1 mois")),IF(Motif={q(M_RTR)},IF(C11<6,"Selon usages",IF(C11<24,"1 mois",'
                    f'"2 mois")),"Aucun"))))', align=CENTER, bold=True)
    put(ws, "E12", f'=IF(Motif={q(M_DEC)},"Rupture au jour du décès ; le préavis est payé sous forme '
                   f'd\'indemnité.",IF(OR(Motif={q(M_AGR)},Motif={q(M_FG)}),"Pas de préavis.","Jours calendaires,'
                   f' à compter de la première présentation de la lettre."))', F(9, italic=True, color="grey"))
    label(ws, "B13", "Fin de préavis (indicative)")
    calc(ws, "C13", '=IF(OR(C12="",DateNotif=""),"",IF(C12="8 jours",DateNotif+7,IF(C12="15 jours",DateNotif+14,'
                    'IF(C12="1 mois",EDATE(DateNotif,1)-1,IF(C12="2 mois",EDATE(DateNotif,2)-1,"")))))',
         DATE, align=CENTER)
    put(ws, "E13", "Des congés payés pris pendant le préavis le prolongent d'autant.", F(9, italic=True, color="grey"))
    label(ws, "B14", "Durée d'accueil totale (mois)")
    calc(ws, "C14", '=IF(OR(DateFin="",DateDebut=""),"",DATEDIF(DateDebut,DateFin+1,"m"))', "0", align=CENTER)

    section(ws, "B16", "Régularisation de salaire (accueil sur 46 semaines ou moins)", "E16")
    label(ws, "B17", "Dernière date anniversaire du contrat")
    calc(ws, "C17", '=IF(OR(DateFin="",DateDebut=""),"",EDATE(DateDebut,12*DATEDIF(DateDebut,DateFin,"y")))',
         DATE, align=CENTER)
    ws["D17"] = '=IF(C17="",DATE(2000,1,1),C17)'
    ws["D17"].font = F(color="white")
    name(wb, "AnnivRegul", "'Fin de contrat'!$D$17")
    label(ws, "B18", "Heures effectuées depuis cette date (dans ce fichier)")
    calc(ws, "C18", '=IF(C17="",0,SUM(RecapEff))', HRS)
    put(ws, "E18", "planning hors heures en plus + jours fériés chômés + absences payées", F(9, italic=True,
                                                                                          color="grey"))
    label(ws, "B19", "Heures de base payées sur la même période (dans ce fichier)")
    calc(ws, "C19", '=IF(C17="",0,SUMPRODUCT((RecapStart>=DATE(YEAR(C17),MONTH(C17),1))*RecapPaid)'
                    '-SUMPRODUCT((RecapStart=DATE(YEAR(C17),MONTH(C17),1))*RecapPaid)*(DAY(C17)-1)'
                    '/DAY(EOMONTH(C17,0)))', HRS)
    label(ws, "B20", "Heures effectuées avant le 1er juin 2026, depuis la date anniversaire")
    inp(ws, "C20", None, "0.00", RIGHT)
    label(ws, "B21", "Heures de base payées avant le 1er juin 2026, depuis la date anniversaire")
    inp(ws, "C21", None, "0.00", RIGHT)
    label(ws, "B22", "Solde des régularisations prévisionnelles antérieures (heures, + pour l'assmat)")
    inp(ws, "C22", None, "0.00", RIGHT)
    label(ws, "B23", "Écart (heures effectuées − heures payées)")
    calc(ws, "C23", "=C18+N(C20)-C19-N(C21)+N(C22)", '0.00 "h";-0.00 "h";"0 h"')
    put(ws, "B24", "Régularisation due à l'assmat (brut)", F(11, True), "sage2")
    calc(ws, "C24", '=IF(OR(TypeCode=1,DateFin=""),0,ROUND(MAX(0,C23)*TauxBrut,2))', EUR0, True, 12, "teal", "sage2")
    name(wb, "Regul", "'Fin de contrat'!$C$24")
    put(ws, "E24", '=IF(TypeCode=1,"Sans objet pour un accueil sur 52 semaines.",IF(C23<0,"Écart négatif : '
                   'rien à reprendre, le « trop-perçu » reste acquis à l\'assmat.",""))',
        F(9, italic=True, color="grey"))

    section(ws, "B26", "Congés payés", "E26")
    label(ws, "B27", "Congés acquis au 31 mai 2026 non encore payés")
    calc(ws, "C27", '=IF(DateFin="",0,MAX(0,ROUND(CPA_Due-IF(TypeCode=1,CPA_Sal/26*MIN(CPTaken,CPA_J),0)'
                    '-CPPaid,2)))', EUR0)
    label(ws, "B28", "Congés acquis depuis le 1er juin 2026 (jours ouvrables)")
    calc(ws, "C28", '=IF(DateFin="",0,CPB_J)', "0")
    label(ws, "B29", "   · maintien de salaire", color="grey")
    calc(ws, "C29", "=ROUND(SalMensBrut/26*C28,2)", EUR0)
    label(ws, "B30", "   · dixième (salaires de la période + régularisation)", color="grey")
    calc(ws, "C30", '=IF(DateFin="",0,ROUND((CPB_Brut+Regul)*0.1,2))', EUR0)
    put(ws, "B31", "Indemnité compensatrice de congés payés", F(11, True), "sage2")
    calc(ws, "C31", '=IF(DateFin="",0,C27+MAX(C29,C30))', EUR0, True, 12, "teal", "sage2")

    section(ws, "B33", "Indemnité de rupture", "E33")
    label(ws, "B34", "Droit à l'indemnité")
    calc(ws, "C34", f'=IF(DateFin="","",IF(AND(OR(Motif={q(M_RET)},Motif={q(M_DEC)}),N(C14)>=9),"Oui","Non"))',
         align=CENTER, bold=True)
    put(ws, "E34", "Due si les parents retirent l'enfant (ou décès) après au moins 9 mois d'accueil — pas en "
                   "cas de démission, retraite, faute grave ou retrait d'agrément.", F(9, italic=True, color="grey"))
    ws["E34"].alignment = Alignment(wrap_text=True, vertical="center")
    ws.row_dimensions[34].height = 30
    label(ws, "B35", "Salaires bruts perçus avant le 1er juin 2026 (depuis le début du contrat)")
    inp(ws, "C35", None, EUR0, RIGHT)
    label(ws, "B36", "Salaires bruts perçus depuis le 1er juin 2026 (+ régularisation)")
    calc(ws, "C36", "=CPB_Brut+Regul", EUR0)
    put(ws, "B37", "Indemnité de rupture (1/80e, sans cotisations)", F(11, True), "sage2")
    calc(ws, "C37", '=IF(C34="Oui",ROUND((N(C35)+C36)/80,2),0)', EUR0, True, 12, "teal", "sage2")
    name(wb, "IndemRupture", "'Fin de contrat'!$C$37")

    section(ws, "B39", "Solde de tout compte", "E39")
    put(ws, "B40", "Régularisation + congés payés (brut, soumis à cotisations)")
    calc(ws, "C40", "=Regul+C31", EUR0, True)
    name(wb, "FinSoumis", "'Fin de contrat'!$C$40")
    put(ws, "E40", "→ ajouté automatiquement au salaire du dernier mois", F(9, italic=True, color="grey"))
    put(ws, "B41", "Indemnité de rupture (case « indemnité de rupture » sur Pajemploi)")
    calc(ws, "C41", "=IndemRupture", EUR0, True)
    put(ws, "B42", "Total brut de fin de contrat", F(12, True, "teal"))
    calc(ws, "C42", "=C40+C41", EUR0, True, 13, "teal")
    put(ws, "B43", "Estimation nette", F(11, color="grey"))
    calc(ws, "C43", "=ROUND(C40*CoefNet,2)+C41", EUR0, color="grey")

    section(ws, "B45", "Documents à remettre", "E45")
    docs = ["Dernier bulletin de salaire (édité par Pajemploi après la déclaration)",
            "Certificat de travail (dates, emploi, portabilité de la prévoyance IRCEM)",
            "Reçu pour solde de tout compte (détail des sommes ci-dessus)",
            "Attestation France Travail (à demander à France Travail)"]
    for i, d in enumerate(docs):
        put(ws, f"B{46 + i}", "☐  " + d, F(10), merge=f"E{46 + i}")
    dv_list(ws, L["Motifs"], "C6")
    dvd = DataValidation(type="date", operator="between", formula1="DATE(2000,1,1)", formula2="DATE(2040,12,31)",
                         allow_blank=True, showErrorMessage=True, error="Saisissez une date (jj/mm/aaaa).")
    ws.add_data_validation(dvd)
    dvd.add("C7:C8")
    ws.page_setup.orientation = "portrait"
    ws.page_setup.fitToHeight = 1
    protect(ws)
    return ws


def build_recap(wb):
    ws = sheet(wb, "Récap annuel", {"A": 2, "B": 17, **{c: 11 for c in "CDEFGHIJKLMNOPQ"}}, tab="gold")
    header(ws, "Récapitulatif annuel", "Toute l'année d'un coup d'œil — utile pour la déclaration d'impôts "
                                       "et les congés payés.", last_col="Q")
    tiles = [("B", "D", "Total versé à l'assmat", "=L23"), ("F", "H", "Salaires nets déclarés", "=H23"),
             ("J", "L", "Indemnités versées", "=I23+J23+K23+IndemRupture"),
             ("N", "Q", "Heures d'accueil réalisées", "=P23")]
    for c0, c1, lab, f in tiles:
        put(ws, f"{c0}5", lab.upper(), F(9, True, "sage"), "teal", align=Alignment(vertical="center", indent=1),
            merge=f"{c1}5")
        calc(ws, f"{c0}6", f, EUR0 if "Heures" not in lab else HRS, True, 18, "white", "teal",
             Alignment(horizontal="left", vertical="center", indent=1), merge=f"{c1}7")
    heads = ["Mois", "Salaire brut", "dont retenues", "H. compl.", "H. major.", "CP versés", "Net déclaré",
             "Entretien", "Repas", "Km", "Total versé", "Heures norm. (Paj.)", "Jours activité", "Jours CP (Paj.)",
             "Heures réalisées", "Maladie enfant (j)"]
    for i, h in enumerate(heads):
        col = chr(ord("B") + i)
        put(ws, f"{col}10", h, F(9, True, "white"), "teal", align=CENTER)
    ws.row_dimensions[10].height = 30
    src = {"C": ("F15", EUR), "D": ("F7", EUR), "E": ("E8", HRS), "F": ("E9", HRS), "G": ("F11", EUR),
           "H": ("K11", EUR), "I": ("K12", EUR), "J": ("K13", EUR), "K": ("K14", EUR), "L": ("M11", EUR),
           "M": ("K6", NUM), "N": ("K7", NUM), "O": ("K8", NUM), "P": ("AB16", HRS), "Q": ("AB11", NUM),
           "R": ("AB2", DATE), "S": ("AB12", "0.00"), "T": ("AB13", "0.00"), "U": ("AB15", "0.00"),
           "V": ("AB19", "0")}
    for i, mn in enumerate(MNAMES):
        r = 11 + i
        put(ws, f"B{r}", mn, F(10, True, "teal2")).hyperlink = f"#'{mn}'!A1"
        for col, (cell, fmt) in src.items():
            calc(ws, f"{col}{r}", f"='{mn}'!{cell}", fmt, size=10, fill_="sage2" if i % 2 else None,
                 bold=col == "L")
        if i % 2:
            ws[f"B{r}"].fill = fill("sage2")
    put(ws, "B23", "Total", F(11, True, "teal"))
    for col in "CDEFGHIJKLMNOPQ":
        fmt = src[col][1]
        calc(ws, f"{col}23", f"=SUM({col}11:{col}22)", fmt, True)
        ws[f"{col}23"].border = Border(top=side("teal", "medium"))
    ws["B23"].border = Border(top=side("teal", "medium"))
    for col in "RSTUV":
        ws.column_dimensions[col].hidden = True
    for nm, col in [("RecapStart", "R"), ("RecapEff", "S"), ("RecapPaid", "T"), ("RecapBrutHF", "U"),
                    ("RecapActive", "V")]:
        name(wb, nm, f"'Récap annuel'!${col}$11:${col}$22")
    mal_ok = "✓ Retenues pour maladie de l'enfant dans la limite de 5 jours."
    put(ws, "B25", f'=IF(Q23>5,"⚠ "&Q23&" jours de maladie de l\'enfant retenus sur la période : la convention '
                   f'limite ces retenues à 5 jours par an (absences courtes) ; au-delà le salaire est dû, sauf '
                   f'absence d\'au moins 14 jours consécutifs.",{q(mal_ok)})', F(10, True, "teal2"), merge="Q25")
    ws.conditional_formatting.add("B25", FormulaRule(formula=['LEFT($B$25,1)="⚠"'], font=F(10, True, "terra")))

    ch = BarChart()
    ch.type = "col"
    ch.title = "Montant versé chaque mois (salaire net + indemnités)"
    ch.style = 10
    ch.height, ch.width = 8, 26
    data = Reference(ws, min_col=12, min_row=10, max_row=22)
    cats = Reference(ws, min_col=2, min_row=11, max_row=22)
    ch.add_data(data, titles_from_data=True)
    ch.set_categories(cats)
    ch.legend = None
    ch.y_axis.numFmt = '#,##0 "€"'
    ch.y_axis.majorGridlines = None
    ch.series[0].graphicalProperties.solidFill = C["teal2"]
    ch.series[0].graphicalProperties.line.solidFill = C["teal2"]
    ws.add_chart(ch, "B27")
    protect(ws)
    return ws


def build_welcome(wb):
    ws = sheet(wb, "Bienvenue", {"A": 3, "B": 5, "C": 30, "D": 5, "E": 30, "F": 5, "G": 30, "H": 5, "I": 30,
                                 "J": 3}, tab="teal")
    for r in range(1, 37):
        for col in "ABCDEFGHIJ":
            ws[f"{col}{r}"].fill = fill("cream")
    ws.row_dimensions[2].height = 22
    put(ws, "B2", BRAND.upper() + "  ·  OUTILS POUR PARENTS EMPLOYEURS", F(10, True, "terra"), "cream",
        merge="I2")
    ws.row_dimensions[3].height = 44
    put(ws, "B3", "Kit Parent Employeur — Assistante maternelle", F(28, True, "teal"), "cream", merge="I3")
    ws.row_dimensions[4].height = 22
    put(ws, "B4", f"{EDITION}  ·  du 1er juin 2026 au 31 mai 2027  ·  barèmes au 1er juin 2026",
        F(12, color="grey"), "cream", merge="I4")
    put(ws, "B6", "EN 4 ÉTAPES", F(10, True, "teal2"), "cream", merge="I6")
    steps = [("1", "Votre contrat", "Une seule fois : planning, taux horaire, indemnités, vacances prévues."),
             ("2", "Chaque mois", "Notez seulement les exceptions : absence, heures en plus, jour férié… "
                                  "Le reste est prérempli."),
             ("3", "Pajemploi", "Recopiez le cadre vert « À déclarer sur Pajemploi ». Les chiffres sont prêts."),
             ("4", "Congés et fin", "Congés payés, régularisation, préavis, indemnité de rupture : tout est "
                                    "calculé.")]
    for i, (n, t, txt) in enumerate(steps):
        cn, ct = "BDFH"[i], "CEGI"[i]
        put(ws, f"{cn}7", n, F(22, True, "terra"), "white", align=Alignment(horizontal="center", vertical="top"),
            merge=f"{cn}9")
        put(ws, f"{ct}7", t, F(13, True, "teal"), "white", align=Alignment(vertical="bottom"))
        put(ws, f"{ct}8", txt, F(10, color="ink"), "white", align=Alignment(wrap_text=True, vertical="top"),
            merge=f"{ct}9")
    ws.row_dimensions[7].height = 24
    ws.row_dimensions[8].height = 30
    ws.row_dimensions[9].height = 30

    put(ws, "B11", "SOMMAIRE", F(10, True, "teal2"), "cream", merge="E11")
    toc = [("Contrat", "À remplir en premier"), ("Récap annuel", "L'année en un coup d'œil")] + \
          [(m, "Présence + déclaration du mois") for m in MNAMES] + \
          [("Congés payés", "Droits et paiements"), ("Fin de contrat", "Préavis, régularisation, solde"),
           ("Barèmes", "Taux légaux et sources")]
    for i, (sh, desc) in enumerate(toc):
        r = 12 + i
        c = put(ws, f"C{r}", "→  " + sh, F(11, True, "teal2"), "cream")
        c.hyperlink = f"#'{sh}'!A1"
        put(ws, f"E{r}", desc, F(10, color="grey"), "cream")
    put(ws, "G11", "LÉGENDE", F(10, True, "teal2"), "cream", merge="I11")
    legend = [("butter", "Cellule à remplir"), ("sage2", "Résultat calculé"), ("blue", "Congé payé"),
              ("mint", "Absence de l'enfant payée"), ("rose", "Absence retenue sur le salaire"),
              ("lav", "Jour férié"), ("stone", "Semaine non programmée / hors contrat")]
    for i, (col, txt) in enumerate(legend):
        r = 12 + i
        put(ws, f"G{r}", "", fill_=col, border=BOX if col == "butter" else None)
        if col == "butter":
            ws[f"G{r}"].border = INBOX
        put(ws, f"H{r}", txt, F(10), "cream", merge=f"I{r}")
    put(ws, "G20", "BON À SAVOIR", F(10, True, "teal2"), "cream", merge="I20")
    tips = ["Un fichier par enfant : depuis janvier 2026, Pajemploi demande une déclaration par enfant.",
            "Déclaration entre le 25 du mois et le 5 du mois suivant.",
            "Le net affiché est une estimation : Pajemploi calcule le net exact à partir du brut.",
            "Les cellules calculées sont protégées contre les fausses manipulations (sans mot de passe).",
            "Fonctionne avec Excel, Google Sheets (Fichier › Importer) et LibreOffice."]
    for i, t in enumerate(tips):
        put(ws, f"G{21 + i * 2}", "•  " + t, F(10), "cream", align=Alignment(wrap_text=True, vertical="top"),
            merge=f"I{22 + i * 2}")
    disc = ("Outil d'aide au calcul fondé sur la convention collective des particuliers employeurs et de l'emploi à "
            "domicile (IDCC 3239) et sur les fiches officielles DREETS et Pajemploi en vigueur au 1er juin 2026. "
            "Il ne remplace pas un conseil juridique. En cas de doute : votre relais petite enfance (RPE), la DREETS "
            "de votre région ou Pajemploi.")
    put(ws, "B33", disc, F(9, italic=True, color="grey"), "cream", align=Alignment(wrap_text=True, vertical="top"),
        merge="I35")
    ws.page_setup.fitToHeight = 1
    ws.print_area = "A1:J36"
    protect(ws)
    return ws


def fill_example(wb):
    c = wb["Contrat"]
    vals = {"C6": "Camille et Thomas Martin", "C7": "Sophie Bernard", "C8": "Léo",
            "C11": dt.date(2025, 9, 1), "C12": TYPES[1], "C13": 42, "C30": 4.80, "C37": 4.00,
            "C38": REPAS[1], "C39": 3.50, "C44": CP_MODES[2], "C45": MNAMES[2]}
    for k, v in vals.items():
        c[k] = v
    for r in (19, 20, 22, 23):  # lun, mar, jeu, ven
        c[f"C{r}"] = dt.time(8, 0)
        c[f"D{r}"] = dt.time(17, 30)
    periods = [(PERIOD_TYPES[1], dt.date(2026, 7, 27), dt.date(2026, 8, 2), "Vacances des parents"),
               (PERIOD_TYPES[0], dt.date(2026, 8, 3), dt.date(2026, 8, 22), "Congés d'été de Sophie"),
               (PERIOD_TYPES[1], dt.date(2026, 8, 24), dt.date(2026, 8, 29), ""),
               (PERIOD_TYPES[1], dt.date(2026, 10, 19), dt.date(2026, 10, 31), "Toussaint"),
               (PERIOD_TYPES[0], dt.date(2026, 12, 21), dt.date(2026, 12, 26), "Congés de Noël de Sophie"),
               (PERIOD_TYPES[1], dt.date(2026, 12, 28), dt.date(2027, 1, 2), ""),
               (PERIOD_TYPES[1], dt.date(2027, 2, 15), dt.date(2027, 2, 20), "Vacances d'hiver")]
    for i, (t, d1, d2, com) in enumerate(periods):
        r = 49 + i
        c[f"B{r}"], c[f"C{r}"], c[f"D{r}"], c[f"E{r}"] = t, d1, d2, com
    wb["Congés payés"]["C10"] = 5745.60
    sep = wb["Septembre 2026"]
    sep["E40"], sep["F40"], sep["N40"] = dt.time(8, 0), dt.time(17, 0), "Mercredi exceptionnel"  # 23/09
    nov = wb["Novembre 2026"]
    for day in (5, 6):
        nov[f"D{R0 + day - 1}"] = MAL
        nov[f"N{R0 + day - 1}"] = "Certificat médical"
    nov[f"E{R0 + 15}"], nov[f"F{R0 + 15}"] = dt.time(7, 30), dt.time(18, 30)  # 16/11
    nov[f"E{R0 + 16}"], nov[f"F{R0 + 16}"] = dt.time(8, 0), dt.time(18, 0)  # 17/11
    nov[f"D{R0 + 23}"], nov[f"N{R0 + 23}"] = ABSP, "Gardé par les grands-parents"


def build(path, example=False, overrides=None):
    wb = Workbook()
    wb.remove(wb.active)
    build_welcome(wb)
    L = build_baremes(wb)
    build_contrat(wb, L)
    build_recap(wb)
    for i, (y, m) in enumerate(MONTHS):
        build_month(wb, i, y, m, L)
    build_cp(wb, L)
    build_fin(wb, L)
    order = ["Bienvenue", "Contrat", "Récap annuel"] + MNAMES + ["Congés payés", "Fin de contrat", "Barèmes"]
    wb._sheets = [wb[n] for n in order]
    wb.active = 0
    if example:
        fill_example(wb)
    for (sh, ref), v in (overrides or {}).items():
        wb[sh][ref] = v
    wb.calculation.fullCalcOnLoad = True
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    wb.save(path)
    return path


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    ex = "--example" in sys.argv
    out = os.path.join(here, "dist", "Kit-Assmat-2026-2027" + ("-EXEMPLE" if ex else "") + ".xlsx")
    print(build(out, example=ex))
