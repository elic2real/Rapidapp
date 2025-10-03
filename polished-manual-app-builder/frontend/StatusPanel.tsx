import React from 'react';

type StatusPanelProps = {
  status: string;
  progress?: number;
};

export default function StatusPanel({ status, progress }: StatusPanelProps) {
  return (
    <div>
      Status: {status}
      {typeof progress === 'number' && <span> {progress}%</span>}
    </div>
  );
}
