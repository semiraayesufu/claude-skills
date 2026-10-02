const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  Header, Footer, AlignmentType, LevelFormat, BorderStyle,
  WidthType, ShadingType, TabStopType, PageNumber
} = require('docx');
const fs = require('fs');

// ─────────────────────────────────────────────────────────────────────────────
// BRAND SETTINGS (edit once for your company)
// ─────────────────────────────────────────────────────────────────────────────
const BRAND = {
  company:     "Your Company",            // used in the header and sources line
  reportTitle: "Weekly Category Summary", // header text, top right
  accent:      "ff6153",                  // hex, no #. Rules, citations, Field Insight bar
  accentWash:  "fff0eb",                  // light tint of the accent for the Field Insight box
  footer:      "Confidential  ·  Internal Use Only",
};

// ─────────────────────────────────────────────────────────────────────────────
// REPORT DATA (Claude fills this in each run; sample values shown)
// ─────────────────────────────────────────────────────────────────────────────
const data = {
  category:   "Example Category",
  period:     "Week of Month DD, YYYY",
  preparedBy: "Category Specialist",

  healthSnapshot: {
    demandTrend:         "Stable",       // Increasing | Stable | Decreasing
    competitivePressure: "Moderate",     // Low | Moderate | High
    keyRisk:        "One sentence on the biggest risk, grounded in this week's notes.",
    keyOpportunity: "One sentence on the biggest opportunity, grounded in this week's notes."
  },

  keyTakeaways: [
    "Up to three short signals leadership should know this week."
  ],

  demandSignals: [
    "Up to four bullets drawn only from the specialist's observations."
  ],

  competitiveSignals: [
    { text: "Up to two cited competitor or market signals.", cite: "1" }
  ],

  fieldInsight: "",  // optional; leave empty to hide the Field Insight box

  recommendations: [
    "Up to two actions, each traceable to an observation above."
  ],

  sources: {
    external: [
      { id: "1", text: "Source name", date: "Mon YYYY" }
    ],
    internal: [
      "Specialist observations"
    ]
  }
};

const outputPath = process.argv[2] || "output.docx";

// ─────────────────────────────────────────────────────────────────────────────
// DESIGN TOKENS
// ─────────────────────────────────────────────────────────────────────────────
const C = {
  coral:   BRAND.accent,
  ink:     "111111",   // title, section labels
  body:    "1e1e1e",   // bullet body
  mid:     "555555",   // secondary
  muted:   "999999",   // meta, header, footer, chip labels
  black:   "000000",   // key risk/opportunity labels in table
  ghost:   "c8c8c8",   // cell dividers
  chipBg:  "f7f6f4",   // top row chips
  white:   "ffffff",   // bottom row cells
  green:   "1b6b3a",   // Increasing
  amber:   "8b5e00",   // Moderate
  red:     "b91c1c",   // Decreasing/High
};

// Fonts — exactly as found in target
const F  = "Instrument Sans";          // everything
const FB = "Instrument Sans SemiBold"; // title only
const FN = "Noto Sans Symbols";        // bullet character rendering

// Sizes in half-points — exact from target XML
const SZ = {
  title:   46,   // 23pt — category name, Instrument Sans SemiBold
  section: 20,   // 10pt — section labels (KEY TAKEAWAYS etc)
  body:    20,   // 10pt — bullet body text
  meta:    17,   // 8.5pt — "Prepared by" line (but bold+allCaps in target)
  chip:    15,   // 7.5pt — chip labels (DEMAND TREND etc)
  chipVal: 20,   // 10pt — chip values (Increasing, Moderate)
  sources: 15,   // 7.5pt — sources lines
  footer:  15,   // 7.5pt — footer
  header:  17,   // 8.5pt — header right text
  super:   13,   // 6.5pt — citation superscripts
};

const LINE = 276; // 1.15× — exact from target

// Page: 12240×15840, margins: top=520 right=720 bottom=600 left=720 header=640 footer=640
// Content width = 12240 - 720 - 720 = 10800 DXA
const CW = 10800;


// ─────────────────────────────────────────────────────────────────────────────
// HELPERS
// ─────────────────────────────────────────────────────────────────────────────
const sp = (after = 0, before = 0) => new Paragraph({
  children: [],
  spacing: { after, before, line: LINE, lineRule: "auto" }
});

const thinRule = (after = 50) => new Paragraph({
  children: [],
  border: { bottom: { style: BorderStyle.SINGLE, size: 4, color: C.ghost, space: 1 } },
  spacing: { after, line: LINE, lineRule: "auto" }
});

// Section label — black, bold, allCaps, 10pt, before=140 after=60
const sectionLabel = (text) => new Paragraph({
  children: [new TextRun({ text, font: F, bold: true, color: C.ink, size: SZ.section, allCaps: true })],
  spacing: { before: 140, after: 60, line: LINE, lineRule: "auto" }
});

// Bullet — filled circle ● (Noto Sans Symbols), body in Instrument Sans
const bullet = (text, cite = null) => new Paragraph({
  numbering: { reference: "bullets", level: 0 },
  spacing: { after: 0, before: 0, line: LINE, lineRule: "auto" },
  children: [
    new TextRun({ text, font: F, size: SZ.body, color: C.body }),
    ...(cite ? [new TextRun({
      text: ` [${cite}]`, font: F, size: SZ.super, color: C.coral, superScript: true
    })] : [])
  ]
});

// ─────────────────────────────────────────────────────────────────────────────
// CATEGORY HEALTH SNAPSHOT TABLE
// Exact structure from target:
//   Row 1: top row — chip bg f7f6f4, bottom+right borders in c8c8c8 only (no top/left)
//   Row 2: bottom row — white bg, bottom+right borders in c8c8c8 (no top/left)
// ─────────────────────────────────────────────────────────────────────────────
const noBorder = { style: BorderStyle.NONE };
const chipBorder = { style: BorderStyle.SINGLE, size: 4, color: C.ghost };

const signalColor = (val, type) => {
  if (type === "demand") {
    return val === "Increasing" ? C.green : val === "Decreasing" ? C.red : C.amber;
  }
  return val === "High" ? C.red : val === "Low" ? C.green : C.amber;
};

// Top row cell (chip bg, label + colored value)
const chipCell = (label, value, type, isRight = false) => new TableCell({
  width: { size: CW / 2, type: WidthType.DXA },
  borders: {
    top:    noBorder,
    left:   noBorder,
    bottom: chipBorder,
    right:  isRight ? noBorder : chipBorder,
  },
  shading: { fill: C.chipBg, type: ShadingType.CLEAR },
  margins: { top: 100, bottom: 100, left: 140, right: 140 },
  children: [
    new Paragraph({
      spacing: { after: 24, line: LINE, lineRule: "auto" },
      children: [new TextRun({ text: label, font: F, size: SZ.chip, color: C.muted, bold: true, allCaps: true })]
    }),
    new Paragraph({
      spacing: { after: 0, line: LINE, lineRule: "auto" },
      children: [new TextRun({ text: value, font: F, size: SZ.chipVal, bold: true, color: signalColor(value, type) })]
    })
  ]
});

// Bottom row cell (white bg, label + narrative text)
const narrativeCell = (label, value, isRight = false) => new TableCell({
  width: { size: CW / 2, type: WidthType.DXA },
  borders: {
    top:    noBorder,
    left:   noBorder,
    bottom: chipBorder,
    right:  isRight ? noBorder : chipBorder,
  },
  shading: { fill: C.white, type: ShadingType.CLEAR },
  margins: { top: 80, bottom: 80, left: 140, right: 140 },
  children: [
    new Paragraph({
      spacing: { after: 20, line: LINE, lineRule: "auto" },
      children: [new TextRun({ text: label, font: F, size: SZ.chip, color: C.black, bold: true, allCaps: true })]
    }),
    new Paragraph({
      spacing: { after: 0, line: LINE, lineRule: "auto" },
      children: [new TextRun({ text: value, font: F, size: SZ.body, color: C.body })]
    })
  ]
});

const healthTable = (hs) => new Table({
  width: { size: CW, type: WidthType.DXA },
  columnWidths: [CW / 2, CW / 2],
  borders: {
    // Outer table border — visible in target as thin black outline
    top:    { style: BorderStyle.SINGLE, size: 4, color: C.ghost },
    left:   { style: BorderStyle.SINGLE, size: 4, color: C.ghost },
    bottom: { style: BorderStyle.SINGLE, size: 4, color: C.ghost },
    right:  { style: BorderStyle.SINGLE, size: 4, color: C.ghost },
    insideH:{ style: BorderStyle.NONE },
    insideV:{ style: BorderStyle.NONE },
  },
  rows: [
    new TableRow({ children: [
      chipCell("Demand Trend",         hs.demandTrend,         "demand", false),
      chipCell("Competitive Pressure", hs.competitivePressure, "competitive", true),
    ]}),
    new TableRow({ children: [
      narrativeCell("Key Risk",        hs.keyRisk,        false),
      narrativeCell("Key Opportunity", hs.keyOpportunity, true),
    ]})
  ]
});

// ─────────────────────────────────────────────────────────────────────────────
// FIELD INSIGHT — coral left bar, light coral wash
// ─────────────────────────────────────────────────────────────────────────────
const fieldInsightBlock = (text) => new Table({
  width: { size: CW, type: WidthType.DXA },
  columnWidths: [CW],
  rows: [new TableRow({ children: [new TableCell({
    width: { size: CW, type: WidthType.DXA },
    borders: {
      left:   { style: BorderStyle.SINGLE, size: 24, color: C.coral },
      top:    noBorder,
      right:  noBorder,
      bottom: noBorder,
    },
    shading: { fill: BRAND.accentWash, type: ShadingType.CLEAR },
    margins: { top: 100, bottom: 100, left: 180, right: 160 },
    children: [
      new Paragraph({
        spacing: { after: 20, line: LINE, lineRule: "auto" },
        children: [new TextRun({ text: "Field Insight", font: F, bold: true, color: C.coral, size: SZ.chip + 1, allCaps: true })]
      }),
      new Paragraph({
        spacing: { after: 0, line: LINE, lineRule: "auto" },
        children: [new TextRun({ text, font: F, italics: true, size: SZ.body, color: C.body })]
      })
    ]
  })]})],
});

// ─────────────────────────────────────────────────────────────────────────────
// DOCUMENT
// ─────────────────────────────────────────────────────────────────────────────
const doc = new Document({
  // Bullet: filled circle ● — matches target exactly
  numbering: {
    config: [{
      reference: "bullets",
      levels: [{
        level: 0,
        format: LevelFormat.BULLET,
        text: "•",   // • small bullet
        alignment: AlignmentType.LEFT,
        style: {
          run: { font: FN, size: SZ.body, color: C.body },
          paragraph: {
            indent: { left: 720, hanging: 360 },
            spacing: { after: 0, before: 0, line: LINE, lineRule: "auto" }
          }
        }
      }]
    }]
  },

  styles: {
    default: { document: { run: { font: F, size: SZ.body, color: C.body } } }
  },

  sections: [{
    properties: {
      page: {
        size: { width: 12240, height: 15840 },
        margin: { top: 520, right: 720, bottom: 600, left: 720, header: 640, footer: 640 }
      }
    },

    // ── HEADER ────────────────────────────────────────────────────────────
    headers: {
      default: new Header({ children: [
        new Paragraph({
          tabStops: [{ type: TabStopType.RIGHT, position: CW }],
          spacing: { after: 30, line: LINE, lineRule: "auto" },
          children: [
            new TextRun({ text: BRAND.company, font: F, bold: true, size: SZ.header, color: C.ink }),
            new TextRun({ text: "\t", font: F, size: SZ.header }),
            new TextRun({ text: BRAND.reportTitle, font: F, size: SZ.header, color: C.muted })
          ]
        }),
        // Coral rule — exact from target
        new Paragraph({
          children: [],
          border: { bottom: { style: BorderStyle.SINGLE, size: 18, color: C.coral, space: 1 } },
          spacing: { after: 0, line: LINE, lineRule: "auto" }
        })
      ]})
    },

    // ── FOOTER ────────────────────────────────────────────────────────────
    // Target: "Confidential · Internal Use Only [TAB] Page 1"
    // Tab stop at position 10800 (right-aligned)
    footers: {
      default: new Footer({ children: [
        new Paragraph({
          tabStops: [{ type: TabStopType.RIGHT, position: CW }],
          border: { top: { style: BorderStyle.SINGLE, size: 4, color: C.ghost } },
          spacing: { before: 40, line: LINE, lineRule: "auto" },
          children: [
            new TextRun({ text: BRAND.footer, font: F, size: SZ.footer, color: C.muted }),
            new TextRun({ text: "\t", font: F, size: SZ.footer }),
            new TextRun({ text: "Page ", font: F, size: SZ.footer, color: C.muted }),
            new TextRun({ children: [PageNumber.CURRENT], font: F, size: SZ.footer, color: C.muted })
          ]
        })
      ]})
    },

    // ── BODY ──────────────────────────────────────────────────────────────
    children: [

      // Category title — Instrument Sans SemiBold, 23pt, ink
      new Paragraph({
        spacing: { after: 16, line: LINE, lineRule: "auto" },
        children: [new TextRun({ text: data.category, font: FB, size: SZ.title, color: C.ink })]
      }),

      // Meta line — "May 26–30, 2026 · Prepared by: [name]" — 8.5pt, bold, muted
      // Target: period in muted, "Prepared by:" in bold muted, name in bold muted
      new Paragraph({
        spacing: { after: 80, line: LINE, lineRule: "auto" },
        children: [
          new TextRun({ text: data.period + "  ·  Prepared by: ", font: F, size: SZ.meta, color: C.muted }),
          new TextRun({ text: data.preparedBy, font: F, size: SZ.meta, color: C.muted, bold: true })
        ]
      }),

      // CATEGORY HEALTH SNAPSHOT
      sectionLabel("Category Health Snapshot"),
      healthTable(data.healthSnapshot),
      sp(50),

      // KEY TAKEAWAYS
      sectionLabel("Key Takeaways"),
      ...data.keyTakeaways.map(t => bullet(t)),
      sp(40),

      // DEMAND & PERFORMANCE SIGNALS
      sectionLabel("Demand & Performance Signals"),
      ...data.demandSignals.map(t => bullet(t)),
      sp(40),

      // COMPETITIVE PRICING & MARKET SIGNALS
      sectionLabel("Competitive Pricing & Market Signals"),
      ...data.competitiveSignals.map(s => bullet(s.text, s.cite)),
      sp(50),

      // FIELD INSIGHT (optional)
      ...(data.fieldInsight ? [fieldInsightBlock(data.fieldInsight), sp(50)] : []),

      // RECOMMENDATIONS
      sectionLabel("Recommendations"),
      ...data.recommendations.map(t => bullet(t)),
      sp(50),

      // SOURCES — thin rule then two lines
      thinRule(40),
      new Paragraph({
        spacing: { after: 20, line: LINE, lineRule: "auto" },
        children: [
          new TextRun({ text: "External  ", font: F, bold: true, size: SZ.sources, color: C.muted }),
          ...data.sources.external.map((s, i) => new TextRun({
            text: `[${s.id}] ${s.text} (${s.date})${i < data.sources.external.length - 1 ? "  ·  " : ""}`,
            font: F, size: SZ.sources, color: C.muted
          }))
        ]
      }),
      new Paragraph({
        spacing: { after: 0, line: LINE, lineRule: "auto" },
        children: [
          new TextRun({ text: "Internal  ", font: F, bold: true, size: SZ.sources, color: C.muted }),
          new TextRun({ text: data.sources.internal.join("  ·  "), font: F, size: SZ.sources, color: C.muted })
        ]
      }),
    ]
  }]
});

Packer.toBuffer(doc).then(buf => {
  fs.writeFileSync(outputPath, buf);
  console.log('✅ Done');
});
