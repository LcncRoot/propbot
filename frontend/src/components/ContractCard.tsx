import React from 'react';
import styles from './ContractCard.module.css';

interface ContractCardProps {
  contract: {
    opportunity_id: string;
    title: string;
    naics_code: string | null;
    response_deadline: string;
    description: string;
    link: string;
  };
}

export default function ContractCard({ contract }: ContractCardProps) {
  const formatDate = (dateString: string) => {
    if (!dateString) return 'No deadline';
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  return (
    <div className={styles.card}>
      <div className={styles.cardHeader}>
        <span className={styles.naicsCode}>
          NAICS: {contract.naics_code || 'N/A'}
        </span>
        <span className={styles.deadline}>
          Due: {formatDate(contract.response_deadline)}
        </span>
      </div>
      
      <h3 className={styles.title}>{contract.title}</h3>
      
      <p className={styles.description}>
        {contract.description.length > 200
          ? `${contract.description.substring(0, 200)}...`
          : contract.description}
      </p>

      <div className={styles.cardFooter}>
        <span className={styles.id}>ID: {contract.opportunity_id}</span>
        {contract.link && (
          <a
            href={contract.link}
            target="_blank"
            rel="noopener noreferrer"
            className={styles.viewButton}
          >
            View Details
          </a>
        )}
      </div>
    </div>
  );
} 