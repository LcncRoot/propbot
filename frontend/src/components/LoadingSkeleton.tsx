import React from 'react';
import styles from './LoadingSkeleton.module.css';

export default function LoadingSkeleton() {
  return (
    <div className={styles.skeleton}>
      <div className={styles.header}>
        <div className={styles.naicsPulse}></div>
        <div className={styles.datePulse}></div>
      </div>
      <div className={styles.titlePulse}></div>
      <div className={styles.descriptionPulse}>
        <div></div>
        <div></div>
        <div></div>
      </div>
      <div className={styles.footer}>
        <div className={styles.idPulse}></div>
        <div className={styles.buttonPulse}></div>
      </div>
    </div>
  );
} 