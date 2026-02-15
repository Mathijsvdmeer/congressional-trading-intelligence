const { Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell, 
        HeadingLevel, AlignmentType, BorderStyle, WidthType, ShadingType,
        PageBreak } = require('docx');
const fs = require('fs');

const border = { style: BorderStyle.SINGLE, size: 1, color: "CCCCCC" };
const borders = { top: border, bottom: border, left: border, right: border };

const doc = new Document({
  styles: {
    default: { document: { run: { font: "Arial", size: 24 } } },
    paragraphStyles: [
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 32, bold: true, font: "Arial" },
        paragraph: { spacing: { before: 240, after: 240 }, outlineLevel: 0 } },
      { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 28, bold: true, font: "Arial" },
        paragraph: { spacing: { before: 180, after: 180 }, outlineLevel: 1 } },
      { id: "Heading3", name: "Heading 3", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 26, bold: true, font: "Arial" },
        paragraph: { spacing: { before: 140, after: 140 }, outlineLevel: 2 } },
      { id: "Code", name: "Code", basedOn: "Normal",
        run: { font: "Courier New", size: 20 },
        paragraph: { spacing: { before: 120, after: 120 } } }
    ]
  },
  sections: [{
    properties: {
      page: {
        size: { width: 12240, height: 15840 },
        margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 }
      }
    },
    children: [
      // Title Page
      new Paragraph({ 
        heading: HeadingLevel.HEADING_1,
        alignment: AlignmentType.CENTER,
        spacing: { before: 2880, after: 480 },
        children: [new TextRun("Congressional Trading Intelligence")]
      }),
      new Paragraph({ 
        alignment: AlignmentType.CENTER,
        spacing: { after: 240 },
        children: [new TextRun({ text: "Technical Documentation", size: 28 })]
      }),
      new Paragraph({ 
        alignment: AlignmentType.CENTER,
        spacing: { after: 1440 },
        children: [new TextRun({ text: "Version 1.0 - February 2026", size: 24, italics: true })]
      }),
      
      new Paragraph({ children: [new PageBreak()] }),

      // 1. PROJECT OVERVIEW
      new Paragraph({ 
        heading: HeadingLevel.HEADING_1,
        children: [new TextRun("1. Project Overview")]
      }),
      new Paragraph({ 
        children: [new TextRun("Congressional Trading Intelligence is a SaaS platform that tracks and displays real-time stock trading activity by U.S. Congressional members. The platform aggregates data from the Quiver Quantitative API, stores it in a PostgreSQL database, and presents it through an interactive web dashboard.")]
      }),
      new Paragraph({ spacing: { before: 240 }, children: [new TextRun({ text: "Key Features:", bold: true })] }),
      new Paragraph({ children: [new TextRun("• Real-time tracking of 109,847+ congressional stock trades")] }),
      new Paragraph({ children: [new TextRun("• 39 politicians monitored (House & Senate)")] }),
      new Paragraph({ children: [new TextRun("• 71 unique stock tickers tracked")] }),
      new Paragraph({ children: [new TextRun("• Search and filter by politician, ticker, party, and trade type")] }),
      new Paragraph({ children: [new TextRun("• Professional, responsive dashboard interface")] }),

      new Paragraph({ children: [new PageBreak()] }),

      // 2. TECHNOLOGY STACK
      new Paragraph({ 
        heading: HeadingLevel.HEADING_1,
        children: [new TextRun("2. Technology Stack")]
      }),

      new Table({
        width: { size: 9360, type: WidthType.DXA },
        columnWidths: [2800, 6560],
        rows: [
          new TableRow({
            children: [
              new TableCell({
                borders, width: { size: 2800, type: WidthType.DXA },
                shading: { fill: "D5E8F0", type: ShadingType.CLEAR },
                margins: { top: 80, bottom: 80, left: 120, right: 120 },
                children: [new Paragraph({ children: [new TextRun({ text: "Component", bold: true })] })]
              }),
              new TableCell({
                borders, width: { size: 6560, type: WidthType.DXA },
                shading: { fill: "D5E8F0", type: ShadingType.CLEAR },
                margins: { top: 80, bottom: 80, left: 120, right: 120 },
                children: [new Paragraph({ children: [new TextRun({ text: "Technology", bold: true })] })]
              })
            ]
          }),
          new TableRow({
            children: [
              new TableCell({
                borders, width: { size: 2800, type: WidthType.DXA },
                margins: { top: 80, bottom: 80, left: 120, right: 120 },
                children: [new Paragraph({ children: [new TextRun("Data Source")] })]
              }),
              new TableCell({
                borders, width: { size: 6560, type: WidthType.DXA },
                margins: { top: 80, bottom: 80, left: 120, right: 120 },
                children: [new Paragraph({ children: [new TextRun("Quiver Quantitative API ($10/month Hobbyist tier)")] })]
              })
            ]
          }),
          new TableRow({
            children: [
              new TableCell({
                borders, width: { size: 2800, type: WidthType.DXA },
                margins: { top: 80, bottom: 80, left: 120, right: 120 },
                children: [new Paragraph({ children: [new TextRun("Backend API")] })]
              }),
              new TableCell({
                borders, width: { size: 6560, type: WidthType.DXA },
                margins: { top: 80, bottom: 80, left: 120, right: 120 },
                children: [new Paragraph({ children: [new TextRun("FastAPI (Python 3.13) deployed on Railway")] })]
              })
            ]
          }),
          new TableRow({
            children: [
              new TableCell({
                borders, width: { size: 2800, type: WidthType.DXA },
                margins: { top: 80, bottom: 80, left: 120, right: 120 },
                children: [new Paragraph({ children: [new TextRun("Database")] })]
              }),
              new TableCell({
                borders, width: { size: 6560, type: WidthType.DXA },
                margins: { top: 80, bottom: 80, left: 120, right: 120 },
                children: [new Paragraph({ children: [new TextRun("Supabase PostgreSQL (hosted)")] })]
              })
            ]
          }),
          new TableRow({
            children: [
              new TableCell({
                borders, width: { size: 2800, type: WidthType.DXA },
                margins: { top: 80, bottom: 80, left: 120, right: 120 },
                children: [new Paragraph({ children: [new TextRun("Frontend")] })]
              }),
              new TableCell({
                borders, width: { size: 6560, type: WidthType.DXA },
                margins: { top: 80, bottom: 80, left: 120, right: 120 },
                children: [new Paragraph({ children: [new TextRun("HTML/CSS/JavaScript (Vanilla) on Netlify")] })]
              })
            ]
          }),
          new TableRow({
            children: [
              new TableCell({
                borders, width: { size: 2800, type: WidthType.DXA },
                margins: { top: 80, bottom: 80, left: 120, right: 120 },
                children: [new Paragraph({ children: [new TextRun("Data Pipeline")] })]
              }),
              new TableCell({
                borders, width: { size: 6560, type: WidthType.DXA },
                margins: { top: 80, bottom: 80, left: 120, right: 120 },
                children: [new Paragraph({ children: [new TextRun("Python script (fetch_quiver_fixed.py) - manual execution")] })]
              })
            ]
          })
        ]
      }),

      new Paragraph({ children: [new PageBreak()] }),

      // 3. ARCHITECTURE
      new Paragraph({ 
        heading: HeadingLevel.HEADING_1,
        children: [new TextRun("3. System Architecture")]
      }),
      
      new Paragraph({ 
        heading: HeadingLevel.HEADING_2,
        children: [new TextRun("3.1 Data Flow")]
      }),
      new Paragraph({ children: [new TextRun("1. Quiver API → fetch_quiver_fixed.py script fetches congressional trades")] }),
      new Paragraph({ children: [new TextRun("2. Script normalizes field mappings (Traded → trade_date, Filed → disclosure_date)")] }),
      new Paragraph({ children: [new TextRun("3. Data stored in Supabase PostgreSQL congressional_trades table")] }),
      new Paragraph({ children: [new TextRun("4. FastAPI backend exposes REST endpoints")] }),
      new Paragraph({ children: [new TextRun("5. Netlify frontend fetches from API and renders dashboard")] }),

      new Paragraph({ spacing: { before: 240 }, children: [] }),

      new Paragraph({ 
        heading: HeadingLevel.HEADING_2,
        children: [new TextRun("3.2 Database Schema")]
      }),
      new Paragraph({ 
        spacing: { before: 120 },
        children: [new TextRun({ text: "Table: congressional_trades", bold: true })]
      }),

      new Table({
        width: { size: 9360, type: WidthType.DXA },
        columnWidths: [2200, 2200, 4960],
        rows: [
          new TableRow({
            children: [
              new TableCell({
                borders, width: { size: 2200, type: WidthType.DXA },
                shading: { fill: "D5E8F0", type: ShadingType.CLEAR },
                margins: { top: 80, bottom: 80, left: 120, right: 120 },
                children: [new Paragraph({ children: [new TextRun({ text: "Column", bold: true })] })]
              }),
              new TableCell({
                borders, width: { size: 2200, type: WidthType.DXA },
                shading: { fill: "D5E8F0", type: ShadingType.CLEAR },
                margins: { top: 80, bottom: 80, left: 120, right: 120 },
                children: [new Paragraph({ children: [new TextRun({ text: "Type", bold: true })] })]
              }),
              new TableCell({
                borders, width: { size: 4960, type: WidthType.DXA },
                shading: { fill: "D5E8F0", type: ShadingType.CLEAR },
                margins: { top: 80, bottom: 80, left: 120, right: 120 },
                children: [new Paragraph({ children: [new TextRun({ text: "Description", bold: true })] })]
              })
            ]
          }),
          new TableRow({
            children: [
              new TableCell({ borders, width: { size: 2200, type: WidthType.DXA }, margins: { top: 80, bottom: 80, left: 120, right: 120 },
                children: [new Paragraph({ children: [new TextRun("id")] })] }),
              new TableCell({ borders, width: { size: 2200, type: WidthType.DXA }, margins: { top: 80, bottom: 80, left: 120, right: 120 },
                children: [new Paragraph({ children: [new TextRun("SERIAL")] })] }),
              new TableCell({ borders, width: { size: 4960, type: WidthType.DXA }, margins: { top: 80, bottom: 80, left: 120, right: 120 },
                children: [new Paragraph({ children: [new TextRun("Primary key")] })] })
            ]
          }),
          new TableRow({
            children: [
              new TableCell({ borders, width: { size: 2200, type: WidthType.DXA }, margins: { top: 80, bottom: 80, left: 120, right: 120 },
                children: [new Paragraph({ children: [new TextRun("member_name")] })] }),
              new TableCell({ borders, width: { size: 2200, type: WidthType.DXA }, margins: { top: 80, bottom: 80, left: 120, right: 120 },
                children: [new Paragraph({ children: [new TextRun("TEXT")] })] }),
              new TableCell({ borders, width: { size: 4960, type: WidthType.DXA }, margins: { top: 80, bottom: 80, left: 120, right: 120 },
                children: [new Paragraph({ children: [new TextRun("Politician name")] })] })
            ]
          }),
          new TableRow({
            children: [
              new TableCell({ borders, width: { size: 2200, type: WidthType.DXA }, margins: { top: 80, bottom: 80, left: 120, right: 120 },
                children: [new Paragraph({ children: [new TextRun("trade_date")] })] }),
              new TableCell({ borders, width: { size: 2200, type: WidthType.DXA }, margins: { top: 80, bottom: 80, left: 120, right: 120 },
                children: [new Paragraph({ children: [new TextRun("DATE")] })] }),
              new TableCell({ borders, width: { size: 4960, type: WidthType.DXA }, margins: { top: 80, bottom: 80, left: 120, right: 120 },
                children: [new Paragraph({ children: [new TextRun("Trade execution date (NOT NULL)")] })] })
            ]
          }),
          new TableRow({
            children: [
              new TableCell({ borders, width: { size: 2200, type: WidthType.DXA }, margins: { top: 80, bottom: 80, left: 120, right: 120 },
                children: [new Paragraph({ children: [new TextRun("disclosure_date")] })] }),
              new TableCell({ borders, width: { size: 2200, type: WidthType.DXA }, margins: { top: 80, bottom: 80, left: 120, right: 120 },
                children: [new Paragraph({ children: [new TextRun("DATE")] })] }),
              new TableCell({ borders, width: { size: 4960, type: WidthType.DXA }, margins: { top: 80, bottom: 80, left: 120, right: 120 },
                children: [new Paragraph({ children: [new TextRun("Filing disclosure date")] })] })
            ]
          }),
          new TableRow({
            children: [
              new TableCell({ borders, width: { size: 2200, type: WidthType.DXA }, margins: { top: 80, bottom: 80, left: 120, right: 120 },
                children: [new Paragraph({ children: [new TextRun("ticker")] })] }),
              new TableCell({ borders, width: { size: 2200, type: WidthType.DXA }, margins: { top: 80, bottom: 80, left: 120, right: 120 },
                children: [new Paragraph({ children: [new TextRun("TEXT")] })] }),
              new TableCell({ borders, width: { size: 4960, type: WidthType.DXA }, margins: { top: 80, bottom: 80, left: 120, right: 120 },
                children: [new Paragraph({ children: [new TextRun("Stock ticker symbol")] })] })
            ]
          }),
          new TableRow({
            children: [
              new TableCell({ borders, width: { size: 2200, type: WidthType.DXA }, margins: { top: 80, bottom: 80, left: 120, right: 120 },
                children: [new Paragraph({ children: [new TextRun("trade_type")] })] }),
              new TableCell({ borders, width: { size: 2200, type: WidthType.DXA }, margins: { top: 80, bottom: 80, left: 120, right: 120 },
                children: [new Paragraph({ children: [new TextRun("TEXT")] })] }),
              new TableCell({ borders, width: { size: 4960, type: WidthType.DXA }, margins: { top: 80, bottom: 80, left: 120, right: 120 },
                children: [new Paragraph({ children: [new TextRun("Purchase, Sale, or Exchange")] })] })
            ]
          }),
          new TableRow({
            children: [
              new TableCell({ borders, width: { size: 2200, type: WidthType.DXA }, margins: { top: 80, bottom: 80, left: 120, right: 120 },
                children: [new Paragraph({ children: [new TextRun("amount_low")] })] }),
              new TableCell({ borders, width: { size: 2200, type: WidthType.DXA }, margins: { top: 80, bottom: 80, left: 120, right: 120 },
                children: [new Paragraph({ children: [new TextRun("INTEGER")] })] }),
              new TableCell({ borders, width: { size: 4960, type: WidthType.DXA }, margins: { top: 80, bottom: 80, left: 120, right: 120 },
                children: [new Paragraph({ children: [new TextRun("Lower bound of trade value")] })] })
            ]
          }),
          new TableRow({
            children: [
              new TableCell({ borders, width: { size: 2200, type: WidthType.DXA }, margins: { top: 80, bottom: 80, left: 120, right: 120 },
                children: [new Paragraph({ children: [new TextRun("amount_high")] })] }),
              new TableCell({ borders, width: { size: 2200, type: WidthType.DXA }, margins: { top: 80, bottom: 80, left: 120, right: 120 },
                children: [new Paragraph({ children: [new TextRun("INTEGER")] })] }),
              new TableCell({ borders, width: { size: 4960, type: WidthType.DXA }, margins: { top: 80, bottom: 80, left: 120, right: 120 },
                children: [new Paragraph({ children: [new TextRun("Upper bound of trade value")] })] })
            ]
          }),
          new TableRow({
            children: [
              new TableCell({ borders, width: { size: 2200, type: WidthType.DXA }, margins: { top: 80, bottom: 80, left: 120, right: 120 },
                children: [new Paragraph({ children: [new TextRun("party")] })] }),
              new TableCell({ borders, width: { size: 2200, type: WidthType.DXA }, margins: { top: 80, bottom: 80, left: 120, right: 120 },
                children: [new Paragraph({ children: [new TextRun("TEXT")] })] }),
              new TableCell({ borders, width: { size: 4960, type: WidthType.DXA }, margins: { top: 80, bottom: 80, left: 120, right: 120 },
                children: [new Paragraph({ children: [new TextRun("D (Democrat) or R (Republican)")] })] })
            ]
          }),
          new TableRow({
            children: [
              new TableCell({ borders, width: { size: 2200, type: WidthType.DXA }, margins: { top: 80, bottom: 80, left: 120, right: 120 },
                children: [new Paragraph({ children: [new TextRun("chamber")] })] }),
              new TableCell({ borders, width: { size: 2200, type: WidthType.DXA }, margins: { top: 80, bottom: 80, left: 120, right: 120 },
                children: [new Paragraph({ children: [new TextRun("TEXT")] })] }),
              new TableCell({ borders, width: { size: 4960, type: WidthType.DXA }, margins: { top: 80, bottom: 80, left: 120, right: 120 },
                children: [new Paragraph({ children: [new TextRun("House or Senate")] })] })
            ]
          }),
          new TableRow({
            children: [
              new TableCell({ borders, width: { size: 2200, type: WidthType.DXA }, margins: { top: 80, bottom: 80, left: 120, right: 120 },
                children: [new Paragraph({ children: [new TextRun("company_name")] })] }),
              new TableCell({ borders, width: { size: 2200, type: WidthType.DXA }, margins: { top: 80, bottom: 80, left: 120, right: 120 },
                children: [new Paragraph({ children: [new TextRun("TEXT")] })] }),
              new TableCell({ borders, width: { size: 4960, type: WidthType.DXA }, margins: { top: 80, bottom: 80, left: 120, right: 120 },
                children: [new Paragraph({ children: [new TextRun("Company name (nullable)")] })] })
            ]
          }),
          new TableRow({
            children: [
              new TableCell({ borders, width: { size: 2200, type: WidthType.DXA }, margins: { top: 80, bottom: 80, left: 120, right: 120 },
                children: [new Paragraph({ children: [new TextRun("created_at")] })] }),
              new TableCell({ borders, width: { size: 2200, type: WidthType.DXA }, margins: { top: 80, bottom: 80, left: 120, right: 120 },
                children: [new Paragraph({ children: [new TextRun("TIMESTAMP")] })] }),
              new TableCell({ borders, width: { size: 4960, type: WidthType.DXA }, margins: { top: 80, bottom: 80, left: 120, right: 120 },
                children: [new Paragraph({ children: [new TextRun("Record creation timestamp")] })] })
            ]
          })
        ]
      }),

      new Paragraph({ children: [new PageBreak()] }),

      // 4. API ENDPOINTS
      new Paragraph({ 
        heading: HeadingLevel.HEADING_1,
        children: [new TextRun("4. API Endpoints")]
      }),
      new Paragraph({ 
        children: [new TextRun({ text: "Base URL: ", bold: true }), 
                   new TextRun("https://congress-trader-api-production.up.railway.app")]
      }),

      new Paragraph({ spacing: { before: 240 }, heading: HeadingLevel.HEADING_2, children: [new TextRun("4.1 GET /stats")] }),
      new Paragraph({ children: [new TextRun("Returns aggregated statistics efficiently without fetching all trade data.")] }),
      new Paragraph({ spacing: { before: 120 }, children: [new TextRun({ text: "Response Example:", bold: true })] }),
      new Paragraph({ 
        style: "Code",
        children: [new TextRun('{\n  "total_trades": 109847,\n  "unique_politicians": 39,\n  "unique_tickers": 71,\n  "recent_trades": 585\n}')]
      }),

      new Paragraph({ spacing: { before: 240 }, heading: HeadingLevel.HEADING_2, children: [new TextRun("4.2 GET /trades?limit=1000")] }),
      new Paragraph({ children: [new TextRun("Returns most recent trades. Default limit: 1000 for performance.")] }),

      new Paragraph({ spacing: { before: 240 }, heading: HeadingLevel.HEADING_2, children: [new TextRun("4.3 GET /trades/ticker/{ticker}")] }),
      new Paragraph({ children: [new TextRun("Returns all trades for a specific ticker symbol.")] }),
      new Paragraph({ spacing: { before: 120 }, children: [new TextRun({ text: "Example:", bold: true }), new TextRun(" /trades/ticker/NVDA")] }),

      new Paragraph({ spacing: { before: 240 }, heading: HeadingLevel.HEADING_2, children: [new TextRun("4.4 GET /trades/recent?days=30")] }),
      new Paragraph({ children: [new TextRun("Returns trades from the last N days (default 30).")] }),

      new Paragraph({ spacing: { before: 240 }, heading: HeadingLevel.HEADING_2, children: [new TextRun("4.5 GET /politician/{name}")] }),
      new Paragraph({ children: [new TextRun("Returns politician profile with trade summary.")] }),
      new Paragraph({ spacing: { before: 120 }, children: [new TextRun({ text: "Example:", bold: true }), new TextRun(" /politician/pelosi")] }),

      new Paragraph({ spacing: { before: 240 }, heading: HeadingLevel.HEADING_2, children: [new TextRun("4.6 GET /top-traders")] }),
      new Paragraph({ children: [new TextRun("Returns top 10 politicians by trade count.")] }),

      new Paragraph({ children: [new PageBreak()] }),

      // 5. DEPLOYMENT
      new Paragraph({ 
        heading: HeadingLevel.HEADING_1,
        children: [new TextRun("5. Deployment Configuration")]
      }),
      
      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("5.1 Railway (Backend API)")] }),
      new Paragraph({ children: [new TextRun("Location: congress-trader-api/")] }),
      new Paragraph({ children: [new TextRun("Command: uvicorn api:app --host 0.0.0.0 --port $PORT")] }),
      new Paragraph({ children: [new TextRun("Environment Variables: SUPABASE_URL, SUPABASE_KEY")] }),
      new Paragraph({ children: [new TextRun("Domain: congress-trader-api-production.up.railway.app")] }),

      new Paragraph({ spacing: { before: 240 }, heading: HeadingLevel.HEADING_2, children: [new TextRun("5.2 Netlify (Frontend)")] }),
      new Paragraph({ children: [new TextRun("Location: congress-trades-dashboard/")] }),
      new Paragraph({ children: [new TextRun("Deployment: Drag-and-drop folder to Netlify")] }),
      new Paragraph({ children: [new TextRun("Current URL: calm-entremet-cf440f.netlify.app")] }),

      new Paragraph({ spacing: { before: 240 }, heading: HeadingLevel.HEADING_2, children: [new TextRun("5.3 Supabase (Database)")] }),
      new Paragraph({ children: [new TextRun("Hosted PostgreSQL instance")] }),
      new Paragraph({ children: [new TextRun("Table: congressional_trades (109,847 records)")] }),

      new Paragraph({ children: [new PageBreak()] }),

      // 6. DATA PIPELINE
      new Paragraph({ 
        heading: HeadingLevel.HEADING_1,
        children: [new TextRun("6. Data Pipeline Script")]
      }),
      
      new Paragraph({ 
        children: [new TextRun({ text: "Script: ", bold: true }), new TextRun("fetch_quiver_fixed.py")]
      }),
      
      new Paragraph({ spacing: { before: 240 }, heading: HeadingLevel.HEADING_2, children: [new TextRun("6.1 Critical Field Mappings")] }),
      new Paragraph({ children: [new TextRun('The Quiver API returns different field names than expected. These mappings were discovered through debugging:')] }),
      new Paragraph({ children: [new TextRun('• "Traded" → trade_date (NOT "TransactionDate")')] }),
      new Paragraph({ children: [new TextRun('• "Filed" → disclosure_date (NOT "ReportDate")')] }),
      new Paragraph({ children: [new TextRun('• "Trade_Size_USD" → amount (NOT "Amount")')] }),
      new Paragraph({ children: [new TextRun('• "Name" → member_name')] }),

      new Paragraph({ spacing: { before: 240 }, heading: HeadingLevel.HEADING_2, children: [new TextRun("6.2 Execution Process")] }),
      new Paragraph({ children: [new TextRun("1. Script fetches all trades from Quiver bulk endpoint")] }),
      new Paragraph({ children: [new TextRun("2. Normalizes field names to match database schema")] }),
      new Paragraph({ children: [new TextRun("3. Validates required fields (trade_date must not be NULL)")] }),
      new Paragraph({ children: [new TextRun("4. Clears existing data from congressional_trades table")] }),
      new Paragraph({ children: [new TextRun("5. Inserts in batches of 100 trades")] }),
      new Paragraph({ children: [new TextRun("6. Reports success/failure statistics")] }),

      new Paragraph({ spacing: { before: 240 }, heading: HeadingLevel.HEADING_2, children: [new TextRun("6.3 Manual Execution")] }),
      new Paragraph({ 
        style: "Code",
        children: [new TextRun("python3 fetch_quiver_fixed.py")]
      }),
      new Paragraph({ spacing: { before: 120 }, children: [new TextRun("NOTE: This is currently a manual process. Automation needed for production.")] }),

      new Paragraph({ children: [new PageBreak()] }),

      // 7. CURRENT STATUS
      new Paragraph({ 
        heading: HeadingLevel.HEADING_1,
        children: [new TextRun("7. Current Status & Functionality")]
      }),

      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("7.1 What's Working")] }),
      new Paragraph({ children: [new TextRun("✅ Quiver API integration (109,847 trades successfully imported)")] }),
      new Paragraph({ children: [new TextRun("✅ Database storage with proper schema and constraints")] }),
      new Paragraph({ children: [new TextRun("✅ FastAPI backend with 6 endpoints deployed on Railway")] }),
      new Paragraph({ children: [new TextRun("✅ Efficient /stats endpoint for dashboard statistics")] }),
      new Paragraph({ children: [new TextRun("✅ Responsive frontend dashboard on Netlify")] }),
      new Paragraph({ children: [new TextRun("✅ Search by politician, ticker, party, trade type")] }),
      new Paragraph({ children: [new TextRun("✅ Real-time filtering and sorting")] }),
      new Paragraph({ children: [new TextRun("✅ Professional UI with color-coded badges")] }),

      new Paragraph({ spacing: { before: 240 }, heading: HeadingLevel.HEADING_2, children: [new TextRun("7.2 Known Limitations")] }),
      new Paragraph({ children: [new TextRun("⚠️ Some company_name fields are NULL (authentic government data limitation)")] }),
      new Paragraph({ children: [new TextRun("⚠️ Manual data refresh (script must be run manually)")] }),
      new Paragraph({ children: [new TextRun("⚠️ No automated daily/weekly updates")] }),
      new Paragraph({ children: [new TextRun("⚠️ No user authentication system")] }),
      new Paragraph({ children: [new TextRun("⚠️ No email alerts or notifications")] }),
      new Paragraph({ children: [new TextRun("⚠️ Temporary Netlify URL (not custom domain)")] }),
      new Paragraph({ children: [new TextRun("⚠️ No analytics or user tracking")] }),

      new Paragraph({ children: [new PageBreak()] }),

      // 8. PRE-LAUNCH IMPROVEMENTS
      new Paragraph({ 
        heading: HeadingLevel.HEADING_1,
        children: [new TextRun("8. Required Improvements Before Launch")]
      }),

      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("8.1 Critical (Must-Have)")] }),
      new Paragraph({ children: [new TextRun("1. Automated Data Updates")] }),
      new Paragraph({ children: [new TextRun("   • Set up daily cron job to fetch new trades")] }),
      new Paragraph({ children: [new TextRun("   • Consider GitHub Actions or Railway scheduler")] }),
      new Paragraph({ children: [new TextRun("   • Implement incremental updates (not full replacement)")] }),

      new Paragraph({ spacing: { before: 180 }, children: [new TextRun("2. Custom Domain")] }),
      new Paragraph({ children: [new TextRun("   • Purchase professional domain (e.g., congresstrades.io)")] }),
      new Paragraph({ children: [new TextRun("   • Configure Netlify custom domain")] }),
      new Paragraph({ children: [new TextRun("   • Set up SSL certificate")] }),

      new Paragraph({ spacing: { before: 180 }, children: [new TextRun("3. Error Handling & Monitoring")] }),
      new Paragraph({ children: [new TextRun("   • Add error logging to API")] }),
      new Paragraph({ children: [new TextRun("   • Set up uptime monitoring (UptimeRobot, etc.)")] }),
      new Paragraph({ children: [new TextRun("   • Alert on API failures or data sync issues")] }),

      new Paragraph({ spacing: { before: 180 }, children: [new TextRun("4. Performance Optimization")] }),
      new Paragraph({ children: [new TextRun("   • Add database indexes on ticker, member_name, trade_date")] }),
      new Paragraph({ children: [new TextRun("   • Implement API response caching")] }),
      new Paragraph({ children: [new TextRun("   • Optimize /top-traders query (currently loads all data)")] }),

      new Paragraph({ spacing: { before: 240 }, heading: HeadingLevel.HEADING_2, children: [new TextRun("8.2 Important (Should-Have)")] }),
      new Paragraph({ children: [new TextRun("1. User Authentication")] }),
      new Paragraph({ children: [new TextRun("   • Free tier with limited features")] }),
      new Paragraph({ children: [new TextRun("   • Premium tier for advanced analytics")] }),
      new Paragraph({ children: [new TextRun("   • Supabase Auth integration")] }),

      new Paragraph({ spacing: { before: 180 }, children: [new TextRun("2. Email Alerts")] }),
      new Paragraph({ children: [new TextRun("   • Allow users to follow specific politicians/tickers")] }),
      new Paragraph({ children: [new TextRun("   • Send notifications on new trades")] }),
      new Paragraph({ children: [new TextRun("   • Use SendGrid or similar service")] }),

      new Paragraph({ spacing: { before: 180 }, children: [new TextRun("3. Analytics Dashboard")] }),
      new Paragraph({ children: [new TextRun("   • Track page views, user engagement")] }),
      new Paragraph({ children: [new TextRun("   • Monitor which politicians/stocks are most searched")] }),
      new Paragraph({ children: [new TextRun("   • Google Analytics or Plausible integration")] }),

      new Paragraph({ spacing: { before: 240 }, heading: HeadingLevel.HEADING_2, children: [new TextRun("8.3 Nice-to-Have (Future Enhancements)")] }),
      new Paragraph({ children: [new TextRun("• Trading volume charts and visualizations")] }),
      new Paragraph({ children: [new TextRun("• Stock performance correlation analysis")] }),
      new Paragraph({ children: [new TextRun("• Export to CSV/Excel functionality")] }),
      new Paragraph({ children: [new TextRun("• Mobile app (React Native)")] }),
      new Paragraph({ children: [new TextRun("• API rate limiting and authentication")] }),
      new Paragraph({ children: [new TextRun("• Historical trend analysis")] }),

      new Paragraph({ children: [new PageBreak()] }),

      // 9. COST STRUCTURE
      new Paragraph({ 
        heading: HeadingLevel.HEADING_1,
        children: [new TextRun("9. Current Cost Structure")]
      }),

      new Table({
        width: { size: 9360, type: WidthType.DXA },
        columnWidths: [3120, 3120, 3120],
        rows: [
          new TableRow({
            children: [
              new TableCell({
                borders, width: { size: 3120, type: WidthType.DXA },
                shading: { fill: "D5E8F0", type: ShadingType.CLEAR },
                margins: { top: 80, bottom: 80, left: 120, right: 120 },
                children: [new Paragraph({ children: [new TextRun({ text: "Service", bold: true })] })]
              }),
              new TableCell({
                borders, width: { size: 3120, type: WidthType.DXA },
                shading: { fill: "D5E8F0", type: ShadingType.CLEAR },
                margins: { top: 80, bottom: 80, left: 120, right: 120 },
                children: [new Paragraph({ children: [new TextRun({ text: "Plan", bold: true })] })]
              }),
              new TableCell({
                borders, width: { size: 3120, type: WidthType.DXA },
                shading: { fill: "D5E8F0", type: ShadingType.CLEAR },
                margins: { top: 80, bottom: 80, left: 120, right: 120 },
                children: [new Paragraph({ children: [new TextRun({ text: "Monthly Cost", bold: true })] })]
              })
            ]
          }),
          new TableRow({
            children: [
              new TableCell({ borders, width: { size: 3120, type: WidthType.DXA }, margins: { top: 80, bottom: 80, left: 120, right: 120 },
                children: [new Paragraph({ children: [new TextRun("Quiver API")] })] }),
              new TableCell({ borders, width: { size: 3120, type: WidthType.DXA }, margins: { top: 80, bottom: 80, left: 120, right: 120 },
                children: [new Paragraph({ children: [new TextRun("Hobbyist")] })] }),
              new TableCell({ borders, width: { size: 3120, type: WidthType.DXA }, margins: { top: 80, bottom: 80, left: 120, right: 120 },
                children: [new Paragraph({ children: [new TextRun("$10.00")] })] })
            ]
          }),
          new TableRow({
            children: [
              new TableCell({ borders, width: { size: 3120, type: WidthType.DXA }, margins: { top: 80, bottom: 80, left: 120, right: 120 },
                children: [new Paragraph({ children: [new TextRun("Railway")] })] }),
              new TableCell({ borders, width: { size: 3120, type: WidthType.DXA }, margins: { top: 80, bottom: 80, left: 120, right: 120 },
                children: [new Paragraph({ children: [new TextRun("Hobby (trial)")] })] }),
              new TableCell({ borders, width: { size: 3120, type: WidthType.DXA }, margins: { top: 80, bottom: 80, left: 120, right: 120 },
                children: [new Paragraph({ children: [new TextRun("$5.00*")] })] })
            ]
          }),
          new TableRow({
            children: [
              new TableCell({ borders, width: { size: 3120, type: WidthType.DXA }, margins: { top: 80, bottom: 80, left: 120, right: 120 },
                children: [new Paragraph({ children: [new TextRun("Supabase")] })] }),
              new TableCell({ borders, width: { size: 3120, type: WidthType.DXA }, margins: { top: 80, bottom: 80, left: 120, right: 120 },
                children: [new Paragraph({ children: [new TextRun("Free")] })] }),
              new TableCell({ borders, width: { size: 3120, type: WidthType.DXA }, margins: { top: 80, bottom: 80, left: 120, right: 120 },
                children: [new Paragraph({ children: [new TextRun("$0.00")] })] })
            ]
          }),
          new TableRow({
            children: [
              new TableCell({ borders, width: { size: 3120, type: WidthType.DXA }, margins: { top: 80, bottom: 80, left: 120, right: 120 },
                children: [new Paragraph({ children: [new TextRun("Netlify")] })] }),
              new TableCell({ borders, width: { size: 3120, type: WidthType.DXA }, margins: { top: 80, bottom: 80, left: 120, right: 120 },
                children: [new Paragraph({ children: [new TextRun("Free")] })] }),
              new TableCell({ borders, width: { size: 3120, type: WidthType.DXA }, margins: { top: 80, bottom: 80, left: 120, right: 120 },
                children: [new Paragraph({ children: [new TextRun("$0.00")] })] })
            ]
          }),
          new TableRow({
            children: [
              new TableCell({ borders, width: { size: 3120, type: WidthType.DXA }, margins: { top: 80, bottom: 80, left: 120, right: 120 },
                shading: { fill: "F0F0F0", type: ShadingType.CLEAR },
                children: [new Paragraph({ children: [new TextRun({ text: "TOTAL", bold: true })] })] }),
              new TableCell({ borders, width: { size: 3120, type: WidthType.DXA }, margins: { top: 80, bottom: 80, left: 120, right: 120 },
                shading: { fill: "F0F0F0", type: ShadingType.CLEAR },
                children: [new Paragraph({ children: [new TextRun("")] })] }),
              new TableCell({ borders, width: { size: 3120, type: WidthType.DXA }, margins: { top: 80, bottom: 80, left: 120, right: 120 },
                shading: { fill: "F0F0F0", type: ShadingType.CLEAR },
                children: [new Paragraph({ children: [new TextRun({ text: "$15.00/month", bold: true })] })] })
            ]
          })
        ]
      }),
      new Paragraph({ spacing: { before: 120 }, children: [new TextRun({ text: "*Note: ", italics: true, size: 20 }), new TextRun({ text: "Railway trial ends in 27 days", italics: true, size: 20 })] }),

      new Paragraph({ children: [new PageBreak()] }),

      // 10. ENVIRONMENT SETUP
      new Paragraph({ 
        heading: HeadingLevel.HEADING_1,
        children: [new TextRun("10. Environment Variables")]
      }),

      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("10.1 Required Variables")] }),
      
      new Paragraph({ spacing: { before: 120 }, children: [new TextRun({ text: "QUIVER_API_KEY", bold: true })] }),
      new Paragraph({ children: [new TextRun("Token: 9470ba57b0b4e9ab5dae1ab77ce91573c9334cdb")] }),
      new Paragraph({ children: [new TextRun("Location: .env file, used by fetch_quiver_fixed.py")] }),

      new Paragraph({ spacing: { before: 180 }, children: [new TextRun({ text: "SUPABASE_URL", bold: true })] }),
      new Paragraph({ children: [new TextRun("Location: Railway environment variables")] }),
      new Paragraph({ children: [new TextRun("Used by: FastAPI backend for database connection")] }),

      new Paragraph({ spacing: { before: 180 }, children: [new TextRun({ text: "SUPABASE_KEY", bold: true })] }),
      new Paragraph({ children: [new TextRun("Location: Railway environment variables")] }),
      new Paragraph({ children: [new TextRun("Used by: FastAPI backend for database authentication")] }),

      new Paragraph({ children: [new PageBreak()] }),

      // 11. NEXT STEPS
      new Paragraph({ 
        heading: HeadingLevel.HEADING_1,
        children: [new TextRun("11. Recommended Next Steps")]
      }),

      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("11.1 Development Environment Setup")] }),
      new Paragraph({ children: [new TextRun("Consider creating a dedicated Mac user for SaaS development:")] }),
      new Paragraph({ children: [new TextRun("• Isolates development environment from personal files")] }),
      new Paragraph({ children: [new TextRun("• Cleaner project organization")] }),
      new Paragraph({ children: [new TextRun("• Run Claude Code CLI directly in terminal for faster iteration")] }),
      new Paragraph({ children: [new TextRun("• Easier Railway deployments without permission issues")] }),

      new Paragraph({ spacing: { before: 240 }, heading: HeadingLevel.HEADING_2, children: [new TextRun("11.2 Immediate Priorities (Week 1)")] }),
      new Paragraph({ children: [new TextRun("1. Set up automated daily data refresh")] }),
      new Paragraph({ children: [new TextRun("2. Purchase and configure custom domain")] }),
      new Paragraph({ children: [new TextRun("3. Add database indexes for performance")] }),
      new Paragraph({ children: [new TextRun("4. Implement basic error logging and monitoring")] }),

      new Paragraph({ spacing: { before: 240 }, heading: HeadingLevel.HEADING_2, children: [new TextRun("11.3 Short-term Goals (Month 1)")] }),
      new Paragraph({ children: [new TextRun("1. Build user authentication system")] }),
      new Paragraph({ children: [new TextRun("2. Create pricing tiers (Free vs Premium)")] }),
      new Paragraph({ children: [new TextRun("3. Add email alert functionality")] }),
      new Paragraph({ children: [new TextRun("4. Implement analytics tracking")] }),
      new Paragraph({ children: [new TextRun("5. Beta test with 10-20 users")] }),

      new Paragraph({ spacing: { before: 240 }, heading: HeadingLevel.HEADING_2, children: [new TextRun("11.4 Launch Preparation")] }),
      new Paragraph({ children: [new TextRun("1. Create landing page with value proposition")] }),
      new Paragraph({ children: [new TextRun("2. Write documentation and FAQ")] }),
      new Paragraph({ children: [new TextRun("3. Set up payment processing (Stripe)")] }),
      new Paragraph({ children: [new TextRun("4. Prepare marketing materials")] }),
      new Paragraph({ children: [new TextRun("5. Soft launch to targeted communities (HackerNews, Reddit)")] }),

      new Paragraph({ children: [new PageBreak()] }),

      // 12. CONCLUSION
      new Paragraph({ 
        heading: HeadingLevel.HEADING_1,
        children: [new TextRun("12. Conclusion")]
      }),
      new Paragraph({ 
        children: [new TextRun("Congressional Trading Intelligence has successfully reached MVP status with 109,847 real congressional trades from the Quiver API, a functional FastAPI backend, and a professional dashboard interface. The core functionality is working, and the foundation is solid.")]
      }),
      new Paragraph({ 
        spacing: { before: 240 },
        children: [new TextRun("Before commercial launch, critical improvements include automated data updates, custom domain setup, performance optimization, and user authentication. With these enhancements, the platform will be ready for beta testing and eventual public release.")]
      }),
      new Paragraph({ 
        spacing: { before: 240 },
        children: [new TextRun("The project demonstrates successful integration of multiple technologies (Quiver API, FastAPI, Supabase, Railway, Netlify) into a cohesive SaaS product. The total monthly operating cost is $15, making this a highly cost-effective MVP.")]
      }),

      new Paragraph({ spacing: { before: 480 }, children: [] }),
      new Paragraph({ 
        alignment: AlignmentType.CENTER,
        children: [new TextRun({ text: "— End of Documentation —", italics: true })]
      }),
    ]
  }]
});

Packer.toBuffer(doc).then(buffer => {
  fs.writeFileSync("Congressional_Trading_Intelligence_Documentation.docx", buffer);
  console.log("✅ Documentation created successfully!");
});
