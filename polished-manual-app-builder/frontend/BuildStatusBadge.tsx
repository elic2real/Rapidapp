import React from 'react';

type BuildStatusBadgeProps = {
  status: 'passing' | 'failing' | 'unknown' | 'success' | 'error';
};

export default function BuildStatusBadge({ status }: BuildStatusBadgeProps) {
  let color = '#ccc';
  let label = 'build status unknown';
  if (status === 'passing' || status === 'success') {
    color = 'green';
    label = 'build succeeded';
  }
  if (status === 'failing' || status === 'error') {
    color = 'red';
    label = 'build failed';
  }
  return (
    <span
      style={{ background: color, color: 'white', padding: '2px 8px', borderRadius: 4 }}
      aria-label={label}
    >
      Build: {status}
    </span>
  );
}
