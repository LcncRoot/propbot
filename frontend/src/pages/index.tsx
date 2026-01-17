import React, { useState } from 'react';
import SearchBar from '../components/SearchBar';
import ContractCard from '../components/ContractCard';
import LoadingSkeleton from '../components/LoadingSkeleton';
import styles from '../styles/Home.module.css';

interface Contract {
  opportunity_id: string;
  title: string;
  naics_code: string | null;
  response_deadline: string;
  description: string;
  link: string;
}

export default function Home() {
  const [contracts, setContracts] = useState<Contract[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');

  const handleSearch = async (term: string) => {
    setIsLoading(true);
    try {
      const response = await fetch(`/api/contracts?search=${encodeURIComponent(term)}`);
      const data = await response.json();
      setContracts(data);
    } catch (error) {
      console.error('Error fetching contracts:', error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className={styles.container}>
      <header className={styles.header}>
        <h1>Federal Contract Search</h1>
        <SearchBar onSearch={handleSearch} />
      </header>

      <main className={styles.main}>
        {isLoading ? (
          <div className={styles.loadingGrid}>
            {[...Array(6)].map((_, i) => (
              <LoadingSkeleton key={i} />
            ))}
          </div>
        ) : (
          <div className={styles.contractGrid}>
            {contracts.map((contract) => (
              <ContractCard key={contract.opportunity_id} contract={contract} />
            ))}
          </div>
        )}
      </main>
    </div>
  );
} 