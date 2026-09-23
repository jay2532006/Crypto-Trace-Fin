"use client";

import * as React from "react";
import Link from "next/link";
import { FolderLock, Plus, Search, Filter, GitFork, AlertCircle, CheckCircle2 } from "lucide-react";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Badge } from "@/components/ui/Badge";
import { Input } from "@/components/ui/Input";
import { Modal } from "@/components/ui/Modal";
import { Table, TableHeader, TableBody, TableRow, TableHead, TableCell } from "@/components/ui/Table";
import { AddressBadge } from "@/components/forensic/AddressBadge";
import { apiClient } from "@/lib/api-client";
import { CaseRecord } from "@/types/domain";
import { formatCurrency, formatDateTime } from "@/lib/utils";

export default function CasesPage() {
  const [cases, setCases] = React.useState<CaseRecord[]>([]);
  const [search, setSearch] = React.useState("");
  const [statusFilter, setStatusFilter] = React.useState("ALL");
  const [isModalOpen, setIsModalOpen] = React.useState(false);
  const [isLoading, setIsLoading] = React.useState(true);

  // Form State
  const [newWallet, setNewWallet] = React.useState("");
  const [newChain, setNewChain] = React.useState("ETH");
  const [newAmount, setNewAmount] = React.useState("");
  const [newComplainant, setNewComplainant] = React.useState("");
  const [newFirNumber, setNewFirNumber] = React.useState("");
  const [newComplaintText, setNewComplaintText] = React.useState("");
  const [formError, setFormError] = React.useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = React.useState(false);

  const fetchCases = React.useCallback(async () => {
    setIsLoading(true);
    try {
      const res = await apiClient.get<CaseRecord[]>("/api/v1/cases");
      setCases(Array.isArray(res.data) ? res.data : []);
    } catch {
      // Fallback
    } finally {
      setIsLoading(false);
    }
  }, []);

  React.useEffect(() => {
    fetchCases();
  }, [fetchCases]);

  const handleCreateCase = async (e: React.FormEvent) => {
    e.preventDefault();
    setFormError(null);

    // Private key / mnemonic detection
    const fullText = `${newWallet} ${newComplaintText}`.toLowerCase();
    if (/[0-9a-f]{64}/.test(fullText)) {
      setFormError("SECURITY VIOLATION: Potential 64-character private key detected. Credential input rejected.");
      return;
    }

    setIsSubmitting(true);
    try {
      await apiClient.post("/api/v1/cases", {
        wallet: newWallet.trim(),
        chain: newChain,
        reported_amount: parseFloat(newAmount) || 0,
        complainant_name: newComplainant || "Anonymous Complainant",
        fir_number: newFirNumber || null,
        complaint_text: newComplaintText || "Intake via CryptoTrace LEA Workstation",
        source: "LEA_INVESTIGATOR_PORTAL",
      });
      setIsModalOpen(false);
      // Reset form
      setNewWallet("");
      setNewAmount("");
      setNewComplainant("");
      setNewFirNumber("");
      setNewComplaintText("");
      fetchCases();
    } catch (err: any) {
      setFormError(err.response?.data?.detail || "Failed to create case. Check input format.");
    } finally {
      setIsSubmitting(false);
    }
  };

  const filteredCases = cases.filter((c) => {
    const matchSearch =
      c.case_id.toLowerCase().includes(search.toLowerCase()) ||
      c.wallet.toLowerCase().includes(search.toLowerCase()) ||
      (c.complaint_text || "").toLowerCase().includes(search.toLowerCase());
    const matchStatus = statusFilter === "ALL" || c.status === statusFilter;
    return matchSearch && matchStatus;
  });

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-200 dark:border-slate-800 pb-5">
        <div>
          <h1 className="text-2xl font-bold font-display text-[#062B6F] dark:text-white">
            Case Management & Intake
          </h1>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
            Authoritative Law Enforcement Dossiers • Immutable Evidence Chaining
          </p>
        </div>
        <Button onClick={() => setIsModalOpen(true)} variant="primary" size="sm" className="gap-2">
          <Plus className="h-4 w-4" />
          <span>Intake New Case</span>
        </Button>
      </div>

      {/* Filter & Search Bar */}
      <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
        <div className="relative w-full sm:w-96">
          <Search className="absolute left-3 top-2.5 h-4 w-4 text-slate-400" />
          <Input
            placeholder="Search by Case ID, Wallet, or Crime Narrative..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="pl-9 text-xs"
          />
        </div>
        <div className="flex items-center gap-2 self-start sm:self-auto">
          <Filter className="h-3.5 w-3.5 text-slate-400" />
          <span className="text-xs font-semibold text-slate-500">Filter Status:</span>
          {["ALL", "OPEN", "CLOSED"].map((st) => (
            <button
              key={st}
              onClick={() => setStatusFilter(st)}
              className={`px-2.5 py-1 rounded text-xs font-semibold transition-colors ${
                statusFilter === st
                  ? "bg-[#062B6F] text-white"
                  : "bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 hover:bg-slate-200"
              }`}
            >
              {st}
            </button>
          ))}
        </div>
      </div>

      {/* Cases Table */}
      <Card>
        <CardContent className="p-0">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Case Identifier</TableHead>
                <TableHead>Target Address</TableHead>
                <TableHead>Chain</TableHead>
                <TableHead>Reported Value</TableHead>
                <TableHead>Complainant / FIR</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Registered At</TableHead>
                <TableHead className="text-right">Action</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {filteredCases.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={8} className="text-center py-8 text-slate-400">
                    No cases match the specified search or filter criteria.
                  </TableCell>
                </TableRow>
              ) : (
                filteredCases.map((c) => (
                  <TableRow key={c.case_id}>
                    <TableCell className="font-bold text-[#062B6F] dark:text-cyan-400 font-mono text-xs">
                      {c.case_id}
                    </TableCell>
                    <TableCell>
                      <AddressBadge address={c.wallet} chain={c.chain} />
                    </TableCell>
                    <TableCell>
                      <Badge variant="outline">{c.chain}</Badge>
                    </TableCell>
                    <TableCell className="font-mono text-emerald-600 dark:text-emerald-400 font-bold">
                      {c.reported_amount ? formatCurrency(c.reported_amount) : "-"}
                    </TableCell>
                    <TableCell className="text-slate-600 dark:text-slate-300">
                      <div>{c.complainant_name || "N/A"}</div>
                      {c.fir_number && <div className="text-[10px] text-slate-400">FIR: {c.fir_number}</div>}
                    </TableCell>
                    <TableCell>
                      <Badge variant={c.status === "OPEN" ? "institutional" : "default"}>{c.status}</Badge>
                    </TableCell>
                    <TableCell className="text-slate-500 text-[11px]">{formatDateTime(c.created_date)}</TableCell>
                    <TableCell className="text-right">
                      <Link href={`/investigations?address=${c.wallet}&chain=${c.chain}&caseId=${c.case_id}`}>
                        <Button variant="secondary" size="sm" className="h-7 text-xs gap-1.5">
                          <GitFork className="h-3 w-3" />
                          <span>Trace</span>
                        </Button>
                      </Link>
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      {/* Case Intake Modal */}
      <Modal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        title="Authoritative Case Intake (Section 91 / NCRP)"
        description="Registers a new cryptocurrency fraud complaint on canonical PostgreSQL storage."
        maxWidth="xl"
      >
        <form onSubmit={handleCreateCase} className="space-y-4">
          {formError && (
            <div className="rounded-lg bg-red-500/10 border border-red-500/30 p-3 text-xs text-red-400 flex items-center gap-2">
              <AlertCircle className="h-4 w-4 flex-shrink-0" />
              <span>{formError}</span>
            </div>
          )}

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            <div className="sm:col-span-2">
              <Input
                label="Suspect Cryptocurrency Address"
                value={newWallet}
                onChange={(e) => setNewWallet(e.target.value)}
                placeholder="0x... or 1A1z... or T..."
                required
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-700 dark:text-slate-200 mb-1.5">
                Blockchain
              </label>
              <select
                value={newChain}
                onChange={(e) => setNewChain(e.target.value)}
                className="w-full h-10 rounded-md border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-900 px-3 text-xs text-slate-800 dark:text-slate-200 focus:ring-2 focus:ring-[#1F66B8]"
              >
                <option value="ETH">Ethereum (ETH)</option>
                <option value="BTC">Bitcoin (BTC)</option>
                <option value="TRON">Tron (TRC-20)</option>
                <option value="POLYGON">Polygon</option>
                <option value="SOL">Solana</option>
              </select>
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            <div>
              <Input
                label="Reported Fraud Loss (USD)"
                type="number"
                value={newAmount}
                onChange={(e) => setNewAmount(e.target.value)}
                placeholder="e.g. 25000"
              />
            </div>
            <div>
              <Input
                label="Complainant Name"
                value={newComplainant}
                onChange={(e) => setNewComplainant(e.target.value)}
                placeholder="e.g. Rajesh Sharma"
              />
            </div>
            <div>
              <Input
                label="FIR / NCRP Ack No."
                value={newFirNumber}
                onChange={(e) => setNewFirNumber(e.target.value)}
                placeholder="e.g. NCRP-2026-9021"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-700 dark:text-slate-200 mb-1.5">
              Incident Narrative / Modus Operandi
            </label>
            <textarea
              rows={3}
              value={newComplaintText}
              onChange={(e) => setNewComplaintText(e.target.value)}
              placeholder="Describe illicit transfer pattern, Telegram scam syndicate, fake mining pool, or ransomware demand..."
              className="w-full rounded-md border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-900 p-3 text-xs text-slate-800 dark:text-slate-200 placeholder:text-slate-400 focus:ring-2 focus:ring-[#1F66B8] focus:outline-none"
            />
          </div>

          <div className="flex justify-end gap-3 pt-3 border-t border-slate-100 dark:border-slate-800">
            <Button type="button" variant="outline" size="sm" onClick={() => setIsModalOpen(false)}>
              Cancel
            </Button>
            <Button type="submit" variant="primary" size="sm" isLoading={isSubmitting}>
              Register Case
            </Button>
          </div>
        </form>
      </Modal>
    </div>
  );
}
