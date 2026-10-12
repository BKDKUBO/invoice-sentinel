"use client";

import { useCallback, useEffect, useState } from "react";
import {
  deletePO,
  deleteVendor,
  fetchPOs,
  fetchVendors,
  formatPHP,
  PurchaseOrder,
  savePO,
  saveVendor,
  Vendor,
} from "@/lib/api";

const input = "w-full rounded-md border border-slate-300 px-2 py-1 text-sm focus:border-sky-500 focus:outline-none";
const btn = "rounded-md px-3 py-1.5 text-xs font-medium";

const emptyVendor = (): Vendor => ({
  name: "",
  tin: "",
  address: "",
  vat_registered: true,
  contact: { name: "", phone: "", email: "" },
  verified_accounts: [{ method: "bank", bank: "", account_number: "", account_name: "" }],
  status: "approved",
});

export function VendorsManager() {
  const [vendors, setVendors] = useState<Vendor[]>([]);
  const [pos, setPos] = useState<PurchaseOrder[]>([]);
  const [editV, setEditV] = useState<Vendor | null>(null);
  const [editP, setEditP] = useState<PurchaseOrder | null>(null);
  const [err, setErr] = useState("");

  const load = useCallback(async () => {
    try {
      const [v, p] = await Promise.all([fetchVendors(), fetchPOs()]);
      setVendors(v);
      setPos(p);
    } catch (e) {
      setErr(String(e));
    }
  }, []);
  useEffect(() => {
    load();
  }, [load]);

  const run = async (fn: () => Promise<unknown>) => {
    setErr("");
    try {
      await fn();
      await load();
      return true;
    } catch (e) {
      setErr(e instanceof Error ? e.message : String(e));
      return false;
    }
  };

  return (
    <div className="space-y-6">
      {err && <p className="rounded-md bg-red-50 px-3 py-2 text-sm text-red-700">{err}</p>}

      <section className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
        <div className="flex items-center justify-between">
          <h2 className="text-sm font-semibold text-navy-900">Approved-vendor master ({vendors.length})</h2>
          <button className={`${btn} bg-navy-900 text-white hover:bg-navy-800`} onClick={() => setEditV(emptyVendor())}>
            + Add vendor
          </button>
        </div>
        <div className="mt-3 overflow-x-auto">
          <table className="min-w-full text-left text-sm">
            <thead className="text-xs uppercase text-slate-500">
              <tr>
                <th className="py-1.5 pr-3">ID</th>
                <th className="py-1.5 pr-3">Vendor</th>
                <th className="py-1.5 pr-3">TIN</th>
                <th className="py-1.5 pr-3">Verified payment account</th>
                <th className="py-1.5 pr-3">Contact</th>
                <th />
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {vendors.map((v) => (
                <tr key={v.id} className="align-top">
                  <td className="py-2 pr-3 font-mono text-xs text-slate-500">{v.id}</td>
                  <td className="py-2 pr-3">
                    <div className="font-medium text-navy-900">{v.name}</div>
                    <div className="text-xs text-slate-500">{v.address}</div>
                  </td>
                  <td className="py-2 pr-3 font-mono text-xs">{v.tin}</td>
                  <td className="py-2 pr-3 text-xs">
                    {(v.verified_accounts || []).map((a, i) => (
                      <div key={i}>
                        {a.bank} <span className="font-mono">{a.account_number}</span>
                        <div className="text-slate-500">{a.account_name}</div>
                      </div>
                    ))}
                  </td>
                  <td className="py-2 pr-3 text-xs">
                    {v.contact?.name}
                    <div className="text-slate-500">{v.contact?.phone}</div>
                  </td>
                  <td className="whitespace-nowrap py-2 text-right">
                    <button className={`${btn} text-sky-700 hover:bg-sky-50`} onClick={() => setEditV(structuredClone(v))}>
                      Edit
                    </button>
                    <button
                      className={`${btn} text-red-600 hover:bg-red-50`}
                      onClick={() => confirm(`Remove ${v.name}?`) && run(() => deleteVendor(v.id!))}
                    >
                      Remove
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        {editV && (
          <VendorForm
            v={editV}
            onChange={setEditV}
            onCancel={() => setEditV(null)}
            onSave={async () => (await run(() => saveVendor(editV))) && setEditV(null)}
          />
        )}
      </section>

      <section className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
        <div className="flex items-center justify-between">
          <h2 className="text-sm font-semibold text-navy-900">Purchase orders ({pos.length})</h2>
          <button
            className={`${btn} bg-navy-900 text-white hover:bg-navy-800`}
            onClick={() =>
              setEditP({
                vendor_id: vendors[0]?.id || "",
                date: new Date().toISOString().slice(0, 10),
                status: "open",
                items: [{ description: "", qty: 1, unit_price: 0 }],
              })
            }
          >
            + Add PO
          </button>
        </div>
        <div className="mt-3 grid gap-3 md:grid-cols-2">
          {pos.map((p) => (
            <div key={p.po_number} className="rounded-lg border border-slate-200 p-3">
              <div className="flex items-start justify-between gap-2">
                <div>
                  <div className="font-mono text-sm font-semibold text-navy-900">{p.po_number}</div>
                  <div className="text-xs text-slate-500">
                    {p.vendor} · {p.date} · {p.status}
                  </div>
                </div>
                <div className="whitespace-nowrap">
                  <button className={`${btn} text-sky-700 hover:bg-sky-50`} onClick={() => setEditP(structuredClone(p))}>
                    Edit
                  </button>
                  <button
                    className={`${btn} text-red-600 hover:bg-red-50`}
                    onClick={() => confirm(`Delete ${p.po_number}?`) && run(() => deletePO(p.po_number!))}
                  >
                    Delete
                  </button>
                </div>
              </div>
              <table className="mt-2 w-full text-xs">
                <tbody>
                  {p.items.map((i, k) => (
                    <tr key={k}>
                      <td className="py-0.5 pr-2">{i.description}</td>
                      <td className="py-0.5 pr-2 tabular-nums">×{i.qty}</td>
                      <td className="py-0.5 text-right tabular-nums">{formatPHP(i.unit_price)}</td>
                    </tr>
                  ))}
                  <tr className="border-t border-slate-100 font-semibold">
                    <td className="pt-1" colSpan={2}>
                      Subtotal (ex-VAT)
                    </td>
                    <td className="pt-1 text-right tabular-nums">{formatPHP(p.subtotal || 0)}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          ))}
        </div>
        {editP && (
          <POForm
            p={editP}
            vendors={vendors}
            onChange={setEditP}
            onCancel={() => setEditP(null)}
            onSave={async () => (await run(() => savePO(editP))) && setEditP(null)}
          />
        )}
      </section>
    </div>
  );
}

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <label className="block text-xs font-medium text-slate-600">
      {label}
      <div className="mt-0.5">{children}</div>
    </label>
  );
}

function VendorForm({
  v,
  onChange,
  onSave,
  onCancel,
}: {
  v: Vendor;
  onChange: (v: Vendor) => void;
  onSave: () => void;
  onCancel: () => void;
}) {
  const acct = v.verified_accounts[0] || { method: "bank", bank: "", account_number: "", account_name: "" };
  const setAcct = (k: string, val: string) =>
    onChange({ ...v, verified_accounts: [{ ...acct, [k]: val }, ...v.verified_accounts.slice(1)] });
  return (
    <div className="mt-4 rounded-lg border border-sky-200 bg-sky-50/40 p-3">
      <h3 className="text-sm font-semibold text-navy-900">{v.id ? `Edit ${v.id}` : "New vendor"}</h3>
      <div className="mt-2 grid gap-2 sm:grid-cols-3">
        <Field label="Registered name">
          <input className={input} value={v.name} onChange={(e) => onChange({ ...v, name: e.target.value })} />
        </Field>
        <Field label="TIN">
          <input className={input} value={v.tin} onChange={(e) => onChange({ ...v, tin: e.target.value })} />
        </Field>
        <Field label="Registered address">
          <input className={input} value={v.address} onChange={(e) => onChange({ ...v, address: e.target.value })} />
        </Field>
        <Field label="Verified bank / e-wallet">
          <input className={input} placeholder="BDO, GCash…" value={acct.bank} onChange={(e) => setAcct("bank", e.target.value)} />
        </Field>
        <Field label="Account / mobile number">
          <input className={input} value={acct.account_number} onChange={(e) => setAcct("account_number", e.target.value)} />
        </Field>
        <Field label="Account name">
          <input className={input} value={acct.account_name} onChange={(e) => setAcct("account_name", e.target.value)} />
        </Field>
        <Field label="Contact person">
          <input className={input} value={v.contact?.name || ""} onChange={(e) => onChange({ ...v, contact: { ...v.contact, name: e.target.value } })} />
        </Field>
        <Field label="Phone (for call-back)">
          <input className={input} value={v.contact?.phone || ""} onChange={(e) => onChange({ ...v, contact: { ...v.contact, phone: e.target.value } })} />
        </Field>
        <Field label="Email">
          <input className={input} value={v.contact?.email || ""} onChange={(e) => onChange({ ...v, contact: { ...v.contact, email: e.target.value } })} />
        </Field>
      </div>
      <div className="mt-3 flex gap-2">
        <button className={`${btn} bg-sky-600 text-white hover:bg-sky-700`} onClick={onSave}>
          Save vendor
        </button>
        <button className={`${btn} border border-slate-300 bg-white`} onClick={onCancel}>
          Cancel
        </button>
      </div>
    </div>
  );
}

function POForm({
  p,
  vendors,
  onChange,
  onSave,
  onCancel,
}: {
  p: PurchaseOrder;
  vendors: Vendor[];
  onChange: (p: PurchaseOrder) => void;
  onSave: () => void;
  onCancel: () => void;
}) {
  const setItem = (i: number, k: string, val: string) =>
    onChange({
      ...p,
      items: p.items.map((it, j) => (j === i ? { ...it, [k]: k === "description" ? val : Number(val) } : it)),
    });
  return (
    <div className="mt-4 rounded-lg border border-sky-200 bg-sky-50/40 p-3">
      <h3 className="text-sm font-semibold text-navy-900">{p.po_number ? `Edit ${p.po_number}` : "New purchase order"}</h3>
      <div className="mt-2 grid gap-2 sm:grid-cols-3">
        <Field label="PO number (blank = auto)">
          <input className={input} value={p.po_number || ""} onChange={(e) => onChange({ ...p, po_number: e.target.value })} />
        </Field>
        <Field label="Vendor">
          <select className={input} value={p.vendor_id} onChange={(e) => onChange({ ...p, vendor_id: e.target.value })}>
            {vendors.map((v) => (
              <option key={v.id} value={v.id}>
                {v.name}
              </option>
            ))}
          </select>
        </Field>
        <Field label="Date">
          <input type="date" className={input} value={p.date} onChange={(e) => onChange({ ...p, date: e.target.value })} />
        </Field>
      </div>
      <div className="mt-3 space-y-1.5">
        {p.items.map((it, i) => (
          <div key={i} className="grid grid-cols-12 gap-2">
            <input className={`${input} col-span-7`} placeholder="Item description" value={it.description} onChange={(e) => setItem(i, "description", e.target.value)} />
            <input className={`${input} col-span-2`} type="number" placeholder="Qty" value={it.qty} onChange={(e) => setItem(i, "qty", e.target.value)} />
            <input className={`${input} col-span-2`} type="number" placeholder="Unit price" value={it.unit_price} onChange={(e) => setItem(i, "unit_price", e.target.value)} />
            <button className="col-span-1 text-xs text-red-600" onClick={() => onChange({ ...p, items: p.items.filter((_, j) => j !== i) })}>
              ✕
            </button>
          </div>
        ))}
        <button className="text-xs font-medium text-sky-700" onClick={() => onChange({ ...p, items: [...p.items, { description: "", qty: 1, unit_price: 0 }] })}>
          + Add line
        </button>
      </div>
      <div className="mt-3 flex gap-2">
        <button className={`${btn} bg-sky-600 text-white hover:bg-sky-700`} onClick={onSave}>
          Save PO
        </button>
        <button className={`${btn} border border-slate-300 bg-white`} onClick={onCancel}>
          Cancel
        </button>
      </div>
    </div>
  );
}
