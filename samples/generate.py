"""Generate PH-style sample invoices for the InvoiceSentinel demo/test round."""
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import os
D=os.path.dirname(os.path.abspath(__file__))
F="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"; FB="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
def f(s,b=False): return ImageFont.truetype(FB if b else F,s)
def peso(x): return f"P{x:,.2f}"
def render(name, header, meta, items, totals, notes=(), w=900, footer=None):
    footer = list(footer) if footer else None
    h=380+len(meta)*28+len(items)*30+len(totals)*30+len(notes)*28+(120 if footer else 60)
    im=Image.new("RGB",(w,h),"white"); d=ImageDraw.Draw(im); y=30
    for i,l in enumerate(header):
        d.text((w//2,y),l,font=f(26 if i==0 else 16,i==0),fill="black",anchor="mt"); y+=34 if i==0 else 24
    y+=10; d.line((40,y,w-40,y),fill="black",width=2); y+=15
    for l in meta: d.text((50,y),l,font=f(17),fill="black"); y+=28
    y+=10; d.line((40,y,w-40,y),fill="gray"); y+=8
    for x,t in ((50,"DESCRIPTION"),(500,"QTY"),(580,"UNIT PRICE"),(740,"AMOUNT")): d.text((x,y),t,font=f(15,True),fill="black")
    y+=28
    for desc,q,u in items:
        d.text((50,y),desc,font=f(16),fill="black"); d.text((500,y),str(q),font=f(16),fill="black")
        d.text((580,y),f"{u:,.2f}",font=f(16),fill="black"); d.text((740,y),f"{q*u:,.2f}",font=f(16),fill="black"); y+=30
    y+=6; d.line((40,y,w-40,y),fill="gray"); y+=10
    for k,v,b in totals:
        d.text((480,y),k,font=f(17,b),fill="black"); d.text((740,y),v,font=f(17,b),fill="black"); y+=30
    y+=10
    for n in notes: d.text((50,y),n,font=f(16,True),fill=(170,0,0)); y+=28
    if footer:
        y+=10
        for l in footer: d.text((w//2,y),l,font=f(13),fill="black",anchor="mt"); y+=20
    return im
def vat_inv(items, vatable_total=None):
    sub=sum(q*u for _,q,u in items); vat=round(sub*0.12,2); return sub,vat,sub+vat
def foot(series):
    return [FOOT[0], f"Series: {series} | Printer: Gotesco Press, TIN 222-333-444-000", FOOT[2]]
FOOT=["BIR Authority to Print No. 4AU0001234567 | Date Issued: 01/15/2026","Series: 0001-5000 | Printer: Gotesco Press, TIN 222-333-444-000","THIS INVOICE SHALL BE VALID FOR FIVE (5) YEARS FROM THE DATE OF ATP"]
cases={}
# 1 clean legit VAT invoice
it=[("Laptop docking station USB-C",4,4850.0),("27in IPS monitor",2,9450.0),("HDMI cable 2m",6,320.0)]
s,v,t=vat_inv(it)
cases["01-legit-vat-invoice.png"]=render("",["Northstar IT Supplies Corp.","Unit 1203 Tycoon Centre, Pearl Drive, Ortigas, Pasig City","VAT Reg. TIN: 214-563-879-00000"],
 ["SALES INVOICE No. 0002871","Date: 2026-10-05","Sold to: Ocana Trading OPC   TIN: 498-221-307-000","Terms: 30 days   PO No.: PO-2026-0145","Pay to: BPI Acct 4410-2287-63, Northstar IT Supplies Corp."],it,
 [("VATable Sales",peso(s),False),("VAT (12%)",peso(v),False),("TOTAL AMOUNT DUE",peso(t),True)],footer=foot("0001-5000"))
# 2 small vendor receipt (VAT-inclusive, non-VAT style)
it=[("Bihon guisado bilao (good for 15)",2,850.0),("Lumpiang shanghai 50pcs",1,600.0),("Puto 50pcs",1,350.0)]
s=sum(q*u for _,q,u in it)
cases["02-legit-small-vendor-receipt.png"]=render("",["Aling Nena's Carinderia","123 P. Burgos St., Brgy. San Antonio, Makati City","NON-VAT Reg. TIN: 305-118-442-000"],
 ["OFFICIAL RECEIPT No. 1456","Date: 2026-10-08","Received from: Ocana Trading OPC"],it,
 [("TOTAL",peso(s),True)],footer=["BIR ATP No. 4AU0009876543 | Date Issued: 03/02/2026 | Series 1001-2000","THIS DOCUMENT IS NOT VALID FOR CLAIM OF INPUT TAX"],w=820)
# 3 ghost
it=[("Professional services - project facilitation",1,135000.0)]
cases["03-ghost-placeholder-tin.png"]=render("",["Prime Synergy Ventures","Metro Manila","TIN: 000-000-000-000"],
 ["INVOICE # PSV-0001","Date: 2026-10-09","Bill to: Ocana Trading OPC"],it,
 [("TOTAL",peso(135000),True)],notes=["Payment via GCash 0917-555-0101 only. Urgent."])
# 4 VAT math wrong
it=[("Office chair ergonomic",10,3200.0),("Steel filing cabinet 4-drawer",3,6800.0)]
s=sum(q*u for _,q,u in it)  # 52400 -> VAT should be 6288
cases["04-vat-math-wrong.png"]=render("",["Luzon Office Furniture Inc.","45 EDSA, Brgy. Wack-Wack, Mandaluyong City","VAT Reg. TIN: 331-772-045-00000"],
 ["SALES INVOICE No. 0010442","Date: 2026-10-06","Sold to: Ocana Trading OPC   PO No.: PO-2026-0148","Pay to: Metrobank Acct 117-3-11700452-1, Luzon Office Furniture Inc."],it,
 [("VATable Sales",peso(s),False),("VAT (12%)",peso(7860),False),("TOTAL AMOUNT DUE",peso(s+7860),True)],footer=foot("10001-15000"))
# 5 BEC bank change
it=[("NCR last-mile delivery (Oct 1-15)",1,42000.0),("Warehouse handling fee",1,3000.0)]
s,v,t=vat_inv(it)
cases["05-bec-bank-change.png"]=render("",["Manila Bay Logistics Co.","Pier 4, North Harbor, Tondo, Manila","VAT Reg. TIN: 987-654-321-000"],
 ["INVOICE No. MBL-4488","Date: 2026-10-07","Bill to: Ocana Trading OPC   PO No.: PO-2026-0142"],it,
 [("VATable Sales",peso(s),False),("VAT (12%)",peso(v),False),("TOTAL",peso(t),True)],
 notes=["IMPORTANT: Our BDO account is under audit. Please remit to our NEW account:","Union Bank Acct No. 1094-3321-8870, Acct Name: J. Dela Rosa. Do not call our office."],footer=foot("MBL-4001 to MBL-6000"))
# 6 overbilled
it=[("A4 Bond Paper 70gsm (ream)",20,2450.0),("Ballpoint pens (box of 12)",10,95.0)]
s,v,t=vat_inv(it)
cases["06-overbilled-bond-paper.png"]=render("",["Quickserve Office Depot","88 Rizal Ave., Sta. Cruz, Manila","VAT Reg. TIN: 268-447-119-00000"],
 ["SALES INVOICE No. 0004517","Date: 2026-10-03","Sold to: Ocana Trading OPC   PO No.: PO-2026-0139","Pay to: Security Bank Acct 0000-0618-8251, Quickserve Office Depot"],it,
 [("VATable Sales",peso(s),False),("VAT (12%)",peso(v),False),("TOTAL AMOUNT DUE",peso(t),True)],footer=foot("0001-5000"))
# 7 near duplicate of Acme seed (seed total 14000 incl tax). Reconstruct: subtotal 12500 + VAT 1500
it=[("A4 Bond Paper (ream)",25,250.0),("Ballpoint Pens (box)",20,175.0),("Staplers & clips kit",10,275.0)]
cases["07-near-duplicate-acme.png"]=render("",["Acme Office Supplies Inc.","210 Shaw Blvd., Mandaluyong City","VAT Reg. TIN: 123-456-789-000"],
 ["INVOICE No. INV-88427","Date: 2026-09-18","Bill to: Ocana Trading OPC"],it,
 [("VATable Sales",peso(12500),False),("VAT (12%)",peso(1500),False),("TOTAL",peso(14000),True)],footer=foot("INV-85001 to INV-90000"))
# 9 known vendor, quietly changed bank account (no urgency words: only the vendor master catches it)
it=[("Wireless keyboard + mouse combo",3,1250.0),("24-port gigabit network switch",1,8900.0)]
s,v,t=vat_inv(it)
cases["09-known-vendor-new-bank.png"]=render("",["Northstar IT Supplies Corp.","Unit 1203 Tycoon Centre, Pearl Drive, Ortigas, Pasig City","VAT Reg. TIN: 214-563-879-00000"],
 ["SALES INVOICE No. 0002904","Date: 2026-10-09","Sold to: Ocana Trading OPC   TIN: 498-221-307-000","Terms: 30 days   PO No.: PO-2026-0158","Pay to: Metrobank Acct 7721-0094-5512, Northstar IT Supplies Corp."],it,
 [("VATable Sales",peso(s),False),("VAT (12%)",peso(v),False),("TOTAL AMOUNT DUE",peso(t),True)],footer=foot("0001-5000"))
# 10 exceeds PO qty and unit price (PO-2026-0152: 10 chairs @3,200)
it=[("Office chair ergonomic",14,3450.0),("Conference table 8-seater",1,18500.0)]
s,v,t=vat_inv(it)
cases["10-exceeds-po-qty.png"]=render("",["Luzon Office Furniture Inc.","45 EDSA, Brgy. Wack-Wack, Mandaluyong City","VAT Reg. TIN: 331-772-045-00000"],
 ["SALES INVOICE No. 0010489","Date: 2026-10-10","Sold to: Ocana Trading OPC   PO No.: PO-2026-0152","Pay to: Metrobank Acct 117-3-11700452-1, Luzon Office Furniture Inc."],it,
 [("VATable Sales",peso(s),False),("VAT (12%)",peso(v),False),("TOTAL AMOUNT DUE",peso(t),True)],footer=foot("10001-15000"))
# 11 cites a PO that does not exist
it=[("Whiteboard markers (box)",12,180.0),("Sticky notes 3x3 (pack)",30,45.0)]
s,v,t=vat_inv(it)
cases["11-nonexistent-po.png"]=render("",["Acme Office Supplies Inc.","210 Shaw Blvd., Mandaluyong City","VAT Reg. TIN: 123-456-789-000"],
 ["INVOICE No. INV-88502","Date: 2026-10-10","Bill to: Ocana Trading OPC   PO No.: PO-2026-0999","Pay to: BDO Acct 0012-3456-7890, Acme Office Supplies Inc."],it,
 [("VATable Sales",peso(s),False),("VAT (12%)",peso(v),False),("TOTAL",peso(t),True)],footer=foot("INV-85001 to INV-90000"))
for k,im in cases.items(): im.save(os.path.join(D,k))
# 8 blurry photo of #1-like legit receipt
im=cases["02-legit-small-vendor-receipt.png"].rotate(4,expand=True,fillcolor=(200,190,170))
im=im.resize((im.width//2,im.height//2)).filter(ImageFilter.GaussianBlur(1.3))
from PIL import ImageEnhance; im=ImageEnhance.Brightness(im).enhance(0.8)
im.save(os.path.join(D,"08-blurry-legit-receipt.jpg"),quality=35)
print("ok")
