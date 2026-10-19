from explicit_record import make_explicit
t = "Title: As des Augustus\nCreator: Augustus <Römisches Reich, Kaiser> ( - )\nInstitution: BLM"
assert make_explicit(t) == "Title: As des Augustus\nDate of making: not recorded in this record.\nCreator: Augustus <Römisches Reich, Kaiser> ( - )\nInstitution: BLM"
r = make_explicit(t, {"Creator": "Issuing authority (not the maker)"})
assert "Issuing authority (not the maker): Augustus" in r and "Maker: not recorded in this record." in r
t2 = "Title: Πλαστήρι\nDate: Βασιλεία Γεωργίου Α’\nInstitution: Faltaits"
r2 = make_explicit(t2, {"Date": "Period label (not a date of making)"})
assert r2.splitlines()[1:3] == ["Date of making: not recorded in this record.", "Maker: not recorded in this record."] or "Maker: not recorded" in r2
assert make_explicit("Title: X\nCreator: A\nDate: 1900") == "Title: X\nCreator: A\nDate: 1900"
print("all tests passed")
