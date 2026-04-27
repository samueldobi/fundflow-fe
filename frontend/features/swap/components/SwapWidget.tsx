import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { Card, CardGlow } from "@/components/ui/Card";
import { Input, Label, HelperText } from "@/components/ui/Input";
import { Select, SelectWrap } from "@/components/ui/Select";

const tokens = ["ETH", "USDC", "USDT", "DAI", "WBTC", "ARB", "OP", "LINK"] as const;

export default function SwapWidget() {
  // Placeholder values (wire to quote + fee logic later)
  const swapFeePct = 0.3;
  const swapFeeValue = "—";
  const estimatedOutput = "227999167.500000 USDC ($227999167.50)";

  return (
    <Card className="p-6 overflow-hidden">
      <CardGlow className="opacity-25" />
      <div className="relative">
        <div className="flex items-start justify-between gap-4">
          <div>
            <div className="font-syne font-700 tracking-tight text-[18px]">
              Token swap
            </div>
            <div className="mt-1 text-[13px] text-[color:var(--ff-muted)]">
              Quote, fees, and price impact are mocked for now.
            </div>
          </div>
          <Badge variant="purple">Multi-token</Badge>
        </div>

        <div className="mt-6 space-y-4">
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            <div className="sm:col-span-2">
              <Label htmlFor="fromAmount">You pay</Label>
              <Input
                id="fromAmount"
                placeholder="0.00"
                type="number"
                inputMode="decimal"
                min={0}
                step="any"
              />
            </div>
            <div>
              <Label htmlFor="fromToken">Token</Label>
              <SelectWrap>
                <Select id="fromToken" defaultValue="ETH">
                  {tokens.map((t) => (
                    <option key={t} value={t} className="bg-[#0f172a]">
                      {t}
                    </option>
                  ))}
                </Select>
              </SelectWrap>
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            <div className="sm:col-span-2">
              <Label htmlFor="toAmount">You receive</Label>
              <Input
                id="toAmount"
                placeholder="0.00"
                inputMode="decimal"
                readOnly
                aria-readonly="true"
                className="cursor-not-allowed opacity-80"
              />
            </div>
            <div>
              <Label htmlFor="toToken">Token</Label>
              <SelectWrap>
                <Select id="toToken" defaultValue="USDC">
                  {tokens.map((t) => (
                    <option key={t} value={t} className="bg-[#0f172a]">
                      {t}
                    </option>
                  ))}
                </Select>
              </SelectWrap>
            </div>
          </div>

          <div className="rounded-2xl border border-white/[0.10] bg-white/[0.03] px-4 py-4">
            <div className="flex items-center justify-between text-[13px]">
              <span className="text-white/85">Price impact</span>
              <span className="text-white/85">0.32%</span>
            </div>
            <div className="mt-2 flex items-center justify-between text-[13px]">
              <span className="text-white/85">{`Swap Fee (${swapFeePct}%)`}</span>
              <span className="text-white/85">{swapFeeValue}</span>
            </div>
            <div className="mt-2 flex items-center justify-between text-[13px]">
              <span className="text-white/85">Network fee</span>
              <span className="text-white/85">$1.42</span>
            </div>
            <div className="mt-2 flex items-center justify-between text-[13px]">
              <span className="text-white/85">Protocol fee</span>
              <span className="text-white/85">0.20%</span>
            </div>
            {/* <div className="mt-3 rounded-2xl border border-white/[0.10] bg-white/[0.02] px-3 py-2 text-[12px] text-white/80">
              {estimatedOutput}
            </div> */}
            <HelperText>
              This section becomes real once wallet + DEX integration lands.
            </HelperText>
          </div>

          <Button variant="primary" size="lg" className="w-full">
            Swap Tokens
          </Button>
        </div>
      </div>
    </Card>
  );
}
