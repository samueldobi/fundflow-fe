// 'use client';

// import React, { createContext, useContext, useEffect, useState } from 'react';
// import { useAccount, useBalance } from 'wagmi';

// interface WalletContextType {
//   address: string | undefined;
//   isConnected: boolean;
//   balance: string;
//   chainId: number | undefined;
// }

// const WalletContext = createContext<WalletContextType | undefined>(undefined);

// export function WalletProvider({ children }: { children: React.ReactNode }) {
//   const { address, isConnected, chainId } = useAccount();
//   const { data: balanceData } = useBalance({
//     address: address,
//     query: { enabled: !!address },
//   });

//   const [balance, setBalance] = useState('0');

//   useEffect(() => {
//     if (balanceData) {
//       setBalance(balanceData.formatted.slice(0, 6)); // 6 decimals
//     }
//   }, [balanceData]);

//   return (
//     <WalletContext.Provider value={{ address, isConnected, balance, chainId }}>
//       {children}
//     </WalletContext.Provider>
//   );
// }

// export function useWallet() {
//   const context = useContext(WalletContext);
//   if (!context) {
//     throw new Error('useWallet must be used within WalletProvider');
//   }
//   return context;
// }