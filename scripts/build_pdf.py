"""County data PDF modeled on Nebraska_93_County_Democratic_Registration_and_Vote_Change.pdf."""
import os, json
import pandas as pd
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
H = os.path.dirname(os.path.abspath(__file__)); D = f"{H}/../data"
OUT = f"{H}/../pdf/North_Carolina_100_County_Democratic_Registration_and_Vote_Change.pdf"
F = "/usr/share/fonts/truetype/liberation/"
pdfmetrics.registerFont(TTFont("DV", F + "LiberationSans-Regular.ttf")); pdfmetrics.registerFont(TTFont("DVB", F + "LiberationSans-Bold.ttf"))
pdfmetrics.registerFont(TTFont("DVI", F + "LiberationSans-Italic.ttf")); pdfmetrics.registerFont(TTFont("DVBI", F + "LiberationSans-BoldItalic.ttf"))
from reportlab.pdfbase.pdfmetrics import registerFontFamily
registerFontFamily("DV", normal="DV", bold="DVB", italic="DVI", boldItalic="DVBI"); registerFontFamily("DVI", normal="DVI", bold="DVBI", italic="DVI", boldItalic="DVBI")
df = pd.read_csv(f"{D}/nc_senate_2022_2026_by_population.csv"); S = json.load(open(f"{D}/summary.json"))
df = df.sort_values(["R26", "county"], ascending=[False, True]).reset_index(drop=True)
NAVY = colors.HexColor("#1f2d4d"); BLUE = colors.HexColor("#dbe8f5"); ORANGE = colors.HexColor("#fbe3cf")
i = lambda v: f"{int(v):,}"
sn = lambda v: ("+" if v > 0 else "") + f"{int(v):,}"
sp = lambda v, d=1: ("+" if v > 0 else "") + f"{v:.{d}f}%"
pc = lambda v, d=1: f"{v:.1f}%"
spt = lambda v: ("+" if v > 0 else "") + f"{v:.2f}"
rose = df.loc[df.regdem26 > df.regdem22, "county"].tolist(); vfell = df.loc[df.dem26 < df.dem22, "county"].tolist()
T = lambda s, sz=6.4, fn="DV": ParagraphStyle("x", fontName=fn, fontSize=sz, leading=sz * 1.25)
title = ParagraphStyle("t", fontName="DVB", fontSize=12, leading=15)
sub = ParagraphStyle("s", fontName="DVI", fontSize=6.6, leading=8.4)
hdr = ParagraphStyle("h", fontName="DVB", fontSize=6.3, leading=7.6, textColor=colors.white, alignment=1)
NOTE = ("*2026 figures are UNOFFICIAL: NC State Board of Elections (SBOE) results site, statewide results labeled \"UNOFFICIAL\" (statewide page last updated Nov 19, 2026 11:19 am ET; "
        f"retrieved 19 Nov 2026 11:52 am CST); the state canvass has not been completed. {S['county_official26']} of 100 county results pages were marked OFFICIAL, "
        f"{len(S['unofficial_counties26'])} unofficial ({', '.join(S['unofficial_counties26'])}). 2022 votes and ballots: SBOE results site, OFFICIAL/certified. "
        "Registration: SBOE voter_stats files for each election date (11/08/2022 and 11/03/2026; all parties: DEM, REP, UNA, LIB, GRE), downloaded 19 Nov 2026. "
        "<b>Race: U.S. Senate, substituted for governor</b> (North Carolina elects its governor in presidential years; no governor race in 2022 or 2026): "
        "2022 Beasley (D) vs. Budd (R); 2026 Cooper (D) vs. Whatley (R). Votes are votes for the Democratic Senate candidate, not a count of registered Democrats who voted.")
def hrow(cols): return [Paragraph(c, hdr) for c in cols]
def style(n, hi):
    st = [("FONT", (0, 1), (-1, -1), "DV", 6.6), ("BACKGROUND", (0, 0), (-1, 0), NAVY), ("ALIGN", (1, 1), (-1, -1), "RIGHT"),
          ("VALIGN", (0, 0), (-1, 0), "MIDDLE"), ("GRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#9a9a9a")),
          ("TOPPADDING", (0, 1), (-1, -1), 0.6), ("BOTTOMPADDING", (0, 1), (-1, -1), 0.6), ("LEFTPADDING", (0, 0), (-1, -1), 2.5), ("RIGHTPADDING", (0, 0), (-1, -1), 2.5),
          ("FONT", (0, n), (-1, n), "DVB", 6.6), ("LINEABOVE", (0, n), (-1, n), 1.0, colors.black)]
    for r, c in hi: st.append(("BACKGROUND", (0, r), (-1, r), c))
    return TableStyle(st)
tot = {k: int(df[k].sum()) for k in ("regdem22", "regdem26", "dem22", "dem26", "ballots22", "ballots26", "regtot22", "regtot26")}
assert tot["dem26"] == S["dem26"] and tot["ballots26"] == S["ballots26"] and tot["regdem22"] == S["regdem22"]
# ---- table 1
cols1 = ["County", "Dem Reg Share 2026 %", "Dem Reg 2022 (11/08/2022)", "Dem Reg 2026 (11/03/2026)", "Reg Change #", "Reg Change %", "Dem Senate Votes 2022",
         "Dem Senate Votes 2026*", "Vote Change #", "Vote Change % (on 2022 base)", "Total Ballots 2022", "Total Ballots 2026*", "Ballot Change #", "Ballot Change %"]
rows1 = [hrow(cols1)]; hi1 = []
for k, r in df.iterrows():
    rows1.append([r.county, pc(r.R26), i(r.regdem22), i(r.regdem26), sn(r.regdem26 - r.regdem22), sp((r.regdem26 / r.regdem22 - 1) * 100), i(r.dem22), i(r.dem26),
                  sn(r.dem26 - r.dem22), sp((r.dem26 / r.dem22 - 1) * 100), i(r.ballots22), i(r.ballots26), sn(r.ballots26 - r.ballots22), sp((r.ballots26 / r.ballots22 - 1) * 100)])
    if r.county in rose: hi1.append((k + 1, BLUE))
    if r.county in vfell: hi1.append((k + 1, ORANGE))
R26s = tot["regdem26"] / tot["regtot26"] * 100
rows1.append(["Statewide total", pc(R26s), i(tot["regdem22"]), i(tot["regdem26"]), sn(tot["regdem26"] - tot["regdem22"]), sp((tot["regdem26"] / tot["regdem22"] - 1) * 100),
              i(tot["dem22"]), i(tot["dem26"]), sn(tot["dem26"] - tot["dem22"]), sp((tot["dem26"] / tot["dem22"] - 1) * 100), i(tot["ballots22"]), i(tot["ballots26"]),
              sn(tot["ballots26"] - tot["ballots22"]), sp((tot["ballots26"] / tot["ballots22"] - 1) * 100)])
w1 = [70, 48, 52, 52, 46, 44, 52, 52, 50, 56, 52, 52, 50, 46]
t1 = Table(rows1, colWidths=w1, repeatRows=1); t1.setStyle(style(len(rows1) - 1, hi1))
legend = Table([["Legend:", f"Democratic registration rose ({', '.join(rose)})", "Democratic Senate votes fell (" + (", ".join(vfell) if vfell else "none in North Carolina") + ")"]],
               colWidths=[50, 260, 260])
legend.setStyle(TableStyle([("FONT", (0, 0), (-1, -1), "DV", 6.6), ("FONT", (0, 0), (0, 0), "DVB", 6.6), ("BACKGROUND", (1, 0), (1, 0), BLUE), ("BACKGROUND", (2, 0), (2, 0), ORANGE),
                            ("BOX", (1, 0), (2, 0), 0.3, colors.grey), ("TOPPADDING", (0, 0), (-1, -1), 1), ("BOTTOMPADDING", (0, 0), (-1, -1), 1)]))
# ---- table 2
cols2 = ["County", "Dem Share of Ballots 2022 %", "Dem Share of Ballots 2026* %", "Change (pts)", "Dem Share of Registration 2022 %", "Total Registered 2022 (11/08/2022)",
         "Dem Share of Registration 2026 %", "Total Registered 2026 (11/03/2026)"]
rows2 = [hrow(cols2)]; hi2 = []
for k, r in df.iterrows():
    rows2.append([r.county, pc(r.S22), pc(r.S26), spt(r.S26 - r.S22), pc(r.R22), i(r.regtot22), pc(r.R26), i(r.regtot26)])
    if r.county in rose: hi2.append((k + 1, BLUE))
S22s = tot["dem22"] / tot["ballots22"] * 100; S26s = tot["dem26"] / tot["ballots26"] * 100
rows2.append(["Statewide total", pc(S22s), pc(S26s), spt(S26s - S22s), pc(tot["regdem22"] / tot["regtot22"] * 100), i(tot["regtot22"]), pc(R26s), i(tot["regtot26"])])
t2 = Table(rows2, colWidths=[90, 72, 72, 60, 80, 80, 80, 80], repeatRows=1); t2.setStyle(style(len(rows2) - 1, hi2))
from reportlab.pdfgen import canvas as rlcanvas
class NumberedCanvas(rlcanvas.Canvas):
    def __init__(self, *a, **k):
        super().__init__(*a, **k); self._saved = []
    def showPage(self):
        self._saved.append(dict(self.__dict__)); self._startPage()
    def save(self):
        n = len(self._saved)
        for st in self._saved:
            self.__dict__.update(st)
            self.setFont("DVI", 6.5)
            self.drawString(36, 20, "*2026 figures unofficial (NC SBOE, state canvass pending). U.S. Senate race, substituted for governor.")
            self.drawRightString(756, 20, f"Page {self._pageNumber} of {n}")
            super().showPage()
        super().save()
class Doc(BaseDocTemplate):
    def __init__(self, fn, **kw):
        super().__init__(fn, pagesize=landscape(letter), leftMargin=36, rightMargin=36, topMargin=30, bottomMargin=34, **kw)
        self.addPageTemplates([PageTemplate("p", [Frame(36, 34, 720, 548, id="f", leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)])])
story = [Paragraph("North Carolina 100 Counties — Democratic Registration, Democratic U.S. Senate Votes and Total Ballots, 2022 vs 2026*", title),
         Paragraph("Sorted by 2026 Democratic share of registration (Democratic registered voters ÷ all registered voters, SBOE voter_stats for 11/03/2026), highest first. "
                   f"{df.county[0]} leads by share; {df.loc[df.regdem26.idxmax(), 'county']} leads by raw Democratic registration. Race: U.S. Senate (no governor race in North Carolina in 2022 or 2026).", sub),
         Spacer(1, 5), Paragraph(NOTE, sub), Spacer(1, 5), legend, Spacer(1, 4), t1, PageBreak(),
         Paragraph("Democratic U.S. Senate Votes as a Share of Total Ballots, and Democratic Share of Registration, 2022 vs 2026*", title),
         Paragraph("Sorted by 2026 Democratic share of registration, highest first. " + NOTE, sub), Spacer(1, 3),
         Paragraph("Share of ballots = Democratic Senate votes ÷ total ballots cast. Share of registration = Democratic registered voters ÷ all registered voters. "
                   "Change (pts) = 2026 share minus 2022 share, in percentage points (computed from unrounded shares).", sub), Spacer(1, 5), t2]
Doc(OUT, title="North Carolina 100 County Democratic Registration and Vote Change", author="mbenson8989").build(story, canvasmaker=NumberedCanvas)
print("wrote", OUT)
