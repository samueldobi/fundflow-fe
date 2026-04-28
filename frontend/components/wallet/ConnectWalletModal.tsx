"use client";

import { useEffect, useMemo, useState } from "react";

import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { Card, CardGlow } from "@/components/ui/Card";
import { HelperText, Input, Label } from "@/components/ui/Input";

type WalletStatus = "idle" | "connecting" | "connected" | "invalid";

function isValidEvmAddress(value: string) {
  return /^0x[a-fA-F0-9]{40}$/.test(value.trim());
}

function truncateAddress(value: string) {
  const v = value.trim();
  if (v.length <= 12) return v;
  return `${v.slice(0, 6)}…${v.slice(-4)}`;
}

export default function ConnectWalletModal({
  onClose,
}: {
  onClose: () => void;
}) {
  const [address, setAddress] = useState("");
  const [status, setStatus] = useState<WalletStatus>("idle");

  const statusMeta = useMemo(() => {
    if (status === "connected")
      return { label: "Wallet connected", variant: "green" as const };
    if (status === "invalid")
      return { label: "Invalid wallet", variant: "purple" as const };
    if (status === "connecting")
      return { label: "Connecting…", variant: "neutral" as const };
    return { label: "Connect wallet", variant: "neutral" as const };
  }, [status]);

  useEffect(() => {
    const previousOverflow = document.body.style.overflow;
    document.body.style.overflow = "hidden";

    const onKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Escape") onClose();
    };
    document.addEventListener("keydown", onKeyDown);

    return () => {
      document.body.style.overflow = previousOverflow;
      document.removeEventListener("keydown", onKeyDown);
    };
  }, [onClose]);

  const connect = () => {
    const v = address.trim();
    setStatus("connecting");
    window.setTimeout(() => {
      setStatus(isValidEvmAddress(v) ? "connected" : "invalid");
    }, 450);
  };

  const refresh = () => {
    setStatus("connecting");
    window.setTimeout(() => {
      setStatus("connected");
    }, 350);
  };

  return (
    <div className="fixed inset-0 z-[100]">
      <button
        aria-label="Close"
        onClick={onClose}
        className="absolute inset-0 bg-black/60"
      />

      <div className="relative h-full w-full flex items-center justify-center p-5">
        <Card className="w-full max-w-[520px] p-6 sm:p-7 overflow-hidden">
          <CardGlow className="opacity-30" />
          <div className="relative">
            <div className="flex items-start justify-between gap-4">
              <div>
                <div className="font-syne font-700 tracking-tight text-[20px]">
                  Connect wallet
                </div>
                <div className="mt-1 text-[13px] text-[color:var(--ff-muted)]">
                  Paste wallet address
                </div>
              </div>
              <button
                onClick={onClose}
                className="h-10 w-10 inline-flex items-center justify-center rounded-2xl border border-white/[0.12] bg-white/[0.04] hover:bg-white/[0.07] transition-colors"
                aria-label="Close modal"
              >
                <svg
                  className="h-4 w-4 text-white/80"
                  viewBox="0 0 20 20"
                  fill="none"
                >
                  <path
                    d="M5 5l10 10M15 5L5 15"
                    stroke="currentColor"
                    strokeWidth="1.8"
                    strokeLinecap="round"
                  />
                </svg>
              </button>
            </div>

            <div className="mt-6 space-y-4">
              <div>
                <Label htmlFor="walletAddress">Wallet address</Label>
                <Input
                  id="walletAddress"
                  placeholder="0x…"
                  value={address}
                  onChange={(e) => setAddress(e.target.value)}
                  autoComplete="off"
                  spellCheck={false}
                />
                <HelperText>
                   wallet will be connected 
                </HelperText>
              </div>

              <div className="rounded-2xl border border-white/[0.10] bg-white/[0.03] px-4 py-4">
                <div className="flex items-center justify-between gap-3">
                  <div className="text-[13px] font-medium text-white/90">
                    Status
                  </div>
                  <Badge variant={statusMeta.variant}>{statusMeta.label}</Badge>
                </div>
                <div className="mt-2 text-[12px] text-[color:var(--ff-muted)]">
                  {status === "connected"
                    ? `Connected: ${truncateAddress(address)}`
                    : status === "invalid"
                      ? "Please paste a valid wallet address."
                      : status === "connecting"
                        ? "Checking address and preparing session…"
                        : "Connect to access campaign actions and personal data."}
                </div>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <Button
                  variant="primary"
                  size="lg"
                  className="w-full"
                  onClick={connect}
                  disabled={status === "connecting"}
                >
                  Connect
                </Button>
                <Button
                  variant="secondary"
                  size="lg"
                  className="w-full"
                  onClick={refresh}
                  disabled={status !== "connected"}
                >
                  Refresh data
                </Button>
              </div>
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
}
