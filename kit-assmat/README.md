# Kit Parent Employeur Assmat 2026-2027 (Nid Serein)

Digital product for French parents employing an assistante maternelle: an Excel / Google Sheets workbook
(contract, 12 monthly sheets with the Pajemploi box, paid leave, end of contract), a 16-page PDF guide and
5 Word letter templates. Etsy listing copy and images are in `etsy/`.

Rules: CCN IDCC 3239, DREETS guides (juin 2026), Pajemploi. Values in force on 1 June 2026.

```bash
python3 build_kit.py && python3 build_kit.py --example     # dist/*.xlsx
python3 build_courriers.py                                 # dist/Modèles de courriers.docx
NODE_PATH=$(npm root -g) node tools/render.js pdf guide/guide.html "dist/Guide du parent employeur 2026-2027.pdf"
NODE_PATH=$(npm root -g) node tools/slides.js etsy/visuels.html etsy/images
python3 tests/test_kit.py                                  # 50 checks against official worked examples (LibreOffice)
```

Next edition (2027-2028): shift `MONTHS`, `PERIOD_START`, the holidays in `FERIES` and the June-May dates in
the Congés payés / Fin de contrat formulas, update the Barèmes values, rerun the tests.
